import math
import mapbox_vector_tile
import mercantile
from django.contrib.gis.db.models.functions import Intersection
from django.contrib.gis.geos import Polygon
from django.http import HttpResponse, Http404
from world import models as wmodels
from django.contrib.gis.gdal import SpatialReference, CoordTransform



Proj = {
    2154: SpatialReference(2154),
    3857: SpatialReference(3857),
    4326: SpatialReference(4326),
}

coordsToBBOX = {
    2154: CoordTransform(Proj[3857], Proj[2154]),
    4326: CoordTransform(Proj[3857], Proj[4326]),
}
reprojGeom = {
    2154: CoordTransform(Proj[2154], Proj[3857]),
    4326: CoordTransform(Proj[4326], Proj[3857]),
}
def pixel_length(zoom):
    RADIUS = 6378137
    CIRCUM = 2 * math.pi * RADIUS
    SIZE = 512
    return CIRCUM / SIZE / 2 ** int(zoom)

def tile_view(request, layer, zoom, x, y):
    proj=2154
    classLayers = {
        'departements': wmodels.Departements,
        'communes': wmodels.Communes,
        'arrondissements': wmodels.Arrondissements,
        'batiments': wmodels.Batiments,
        'cantons': wmodels.Cantons,
        'world': wmodels.WorldBorder,
        'osm-building-roads': wmodels.OSMBuildingRoads,
        'osm-building-line': wmodels.OSMBuildingLine,
        'osm-building-point': wmodels.OSMBuildingPoint,
        'osm-building-polygon': wmodels.OSMBuildingPolygon,
        'departements-osm': wmodels.OSMDepartements,
        'communes-osm': wmodels.OSMCommunes,
        'arrondissements-osm': wmodels.OSMArrondissements,
    }
    classLayer = classLayers.get(layer)
    if classLayer is None:
        raise Http404("layer %s does not exist" % layer)
    bounds = mercantile.bounds(int(x), int(y), int(zoom))
    west, south = mercantile.xy(bounds.west, bounds.south)
    east, north = mercantile.xy(bounds.east, bounds.north)
    pixel = pixel_length(zoom)
    buffer = 4 * pixel
    bbox = Polygon.from_bbox((west - buffer, south - buffer, east + buffer, north + buffer))
    if layer[-4:] == '-osm':
        proj=4326

    if proj in coordsToBBOX:
        bbox.transform(coordsToBBOX[proj])
        
    if layer[0:4] == 'osm-':
        layerVals = classLayer.objects.filter(way__intersects=bbox)
        layerVals = layerVals.annotate(clipped=Intersection('way', bbox))

    else:
        layerVals = classLayer.objects.filter(geom__intersects=bbox)
        layerVals = layerVals.annotate(clipped=Intersection('geom', bbox))
    

    if proj in reprojGeom:
        for layerVal in layerVals:
            layerVal.clipped.transform(reprojGeom[proj])
            
    tile = {
        "name": layer,
        "features": [
            {
                "geometry": layerVal.clipped.simplify(pixel, preserve_topology=True).wkt,
                "properties": {f.name: getattr(layerVal, f.name) for f in layerVal._meta.get_fields() if f.name not in ["geom", 'way'] and getattr(layerVal, f.name, None) is not None },
            }
            for layerVal in layerVals
        ],
    }
    vector_tile = mapbox_vector_tile.encode(tile, quantize_bounds=(west, south, east, north))
    return HttpResponse(vector_tile, content_type="application/vnd.mapbox-vector-tile")
