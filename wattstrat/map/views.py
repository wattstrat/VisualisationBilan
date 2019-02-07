######################## Batiment view ######################
from django.conf import settings

import shapely
import math
import mapbox_vector_tile
import mercantile

from django.contrib.gis.db.models.aggregates import Union
from django.contrib.gis.db.models.functions import Intersection
from django.contrib.gis.geos import Polygon
from django.contrib.gis.gdal import SpatialReference, CoordTransform

from world import models as wmodels
from world.views import reprojGeom, coordsToBBOX, Proj
from django.db.models import Q

from django.views import View
from django.http.response import Http404, HttpResponse
from braces.views import LoginRequiredMixin

from rest_framework.permissions import BasePermission, IsAuthenticated


# TODO: import IGN avec lien OSM id et vice versa


class BatiTilesView(LoginRequiredMixin, View):
    # recup les shape des communes payées
# Union de shape
# bbox inter union => poly_ign
# bbox - union => poly_osm
# IGN bati = filter ((id in list-bati.ign_code and geom in bbox) or (geom in poly_ign)
# IGN bati += metadata.ign=true IGN + filter metadata
# OSM bati = filter (geom in poly_osm and (id not in list-bati.osm_code))
# OSM bati += metadata.osm = true
# VECTO = OSM bati + IGN bati

    Proj = 2154
    permission_classes = (IsAuthenticated)

    @staticmethod
    def pixel_length(zoom):
        RADIUS = 6378137
        CIRCUM = 2 * math.pi * RADIUS
        SIZE = 512
        return CIRCUM / SIZE / 2 ** int(zoom)

    def _getOSMProps(self, bati):
        metadatas = {f.name: getattr(bati, f.name) for f in bati._meta.get_fields() if f.name not in ['way'] and getattr(bati, f.name, None) is not None }
        metadatas["IGN"] = False
        return metadatas
    
    def _getIGNProps(self, bati):
        metadatas = {f.name: getattr(bati, f.name) for f in bati._meta.get_fields() if f.name not in ["geom"] and getattr(bati, f.name, None) is not None }
        metadatas["IGN"] = True
        return metadatas
    
    @staticmethod
    def _createBBOX(zoom, x, y):
        bounds = mercantile.bounds(int(x), int(y), int(zoom))
        west, south = mercantile.xy(bounds.west, bounds.south)
        east, north = mercantile.xy(bounds.east, bounds.north)
        pixel = BatiTilesView.pixel_length(zoom)
        buffer = 4 * pixel
        bbox = Polygon.from_bbox((west - buffer, south - buffer, east + buffer, north + buffer))
        return bbox, west, south, east, north, pixel

    def get(self, request, *args, **kwargs):
        bbox, west, south, east, north, pixel  = self._createBBOX(*args, **kwargs)
        # Single Projection for OSM building and IGN building : easier
        bbox.transform(coordsToBBOX[self.Proj])
        dataBati = request.user.account.communes
        ign_list = [k[2:] for k in dataBati.get("communes", {}).keys()]
        if len(ign_list) == 0:
            poly_ign = None
        else:
            poly_ign=wmodels.Communes.objects.filter(geom__intersects=bbox).filter(insee_com__in=ign_list).aggregate(Union('geom'))['geom__union']
        if poly_ign is not None:
            bati_c_query = Q(geom__intersects=poly_ign)
        else:
            bati_c_query = None
        ign_bati_list = [x['ign'] for k, x in dataBati.get("batiments", {}).items()]
        if len(ign_bati_list) == 0:
            bati_ign_query = bati_c_query
        else:
            bati_ign_query = Q(geom__intersects=bbox) & Q(id_bat__in=ign_bati_list)
            if bati_c_query is not None:
                bati_ign_query |= bati_c_query

        if bati_ign_query is not None:
            bati_ign=wmodels.Batiments.objects.filter(bati_ign_query).annotate(clipped=Intersection('geom', bbox))
        else:
            bati_ign = []

        bati_osm_query = Q(way__intersects=bbox)

        if poly_ign is not None:
            bati_osm_query &= ~Q(way__intersects=poly_ign)
    
        bati_osm_paied = [x['osm'] for k, x in dataBati.get("batiments", {}).items()]
        if len(bati_osm_paied) > 0:
            bati_osm_query &= ~Q(osm_id__in=bati_osm_paied)
        bati_osm = wmodels.OSMBuildingPolygon.objects.filter(bati_osm_query).annotate(clipped=Intersection('way', bbox))

        for bati in bati_osm:
            bati.clipped.transform(reprojGeom[self.Proj])
        for bati in bati_ign:
            bati.clipped.transform(reprojGeom[self.Proj])
        
        osmFeatures = [
            {
                "geometry": bati.clipped.simplify(pixel, preserve_topology=True).wkt,
                "properties": self._getOSMProps(bati)
            }
            for bati in bati_osm
        ]
        ignFeatures = [
            {
                "geometry": bati.clipped.simplify(pixel, preserve_topology=True).wkt,
                "properties": self._getIGNProps(bati)
            }
            for bati in bati_ign
        ]
        tile = {
            "name": "batiments",
            "features": osmFeatures + ignFeatures,
        }
        vector_tile = mapbox_vector_tile.encode(tile, quantize_bounds=(west, south, east, north))
        return HttpResponse(vector_tile, content_type="application/vnd.mapbox-vector-tile")
        
