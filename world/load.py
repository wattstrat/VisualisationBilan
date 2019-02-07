import os
from django.contrib.gis.utils import LayerMapping
from .models import WorldBorder, Cantons, Departements, Communes, Arrondissements, Batiments, OSMRegions, OSMCommunes, OSMArrondissements, OSMDepartements

world_mapping = {
    'fips' : 'FIPS',
    'iso2' : 'ISO2',
    'iso3' : 'ISO3',
    'un' : 'UN',
    'name' : 'NAME',
    'area' : 'AREA',
    'pop2005' : 'POP2005',
    'region' : 'REGION',
    'subregion' : 'SUBREGION',
    'lon' : 'LON',
    'lat' : 'LAT',
    'geom' : 'MULTIPOLYGON',
}

world_shp = os.path.abspath(
    os.path.join(os.path.dirname(__file__), 'datas', 'TM_WORLD_BORDERS-0.3.shp'),
)

def world_run(verbose=True):
    lm = LayerMapping(
        WorldBorder, world_shp, world_mapping,
        transform=False, encoding='iso-8859-1',
    )
    lm.save(strict=True, verbose=verbose)

cantons_mapping = {
    'id_geofla' : 'ID_GEOFLA',
    'code_cant' : 'CODE_CANT',
    'code_chf' : 'CODE_CHF',
    'nom_chf' : 'NOM_CHF',
    'x_chf_lieu' : 'X_CHF_LIEU',
    'y_chf_lieu' : 'Y_CHF_LIEU',
    'x_centroid' : 'X_CENTROID',
    'y_centroid' : 'Y_CENTROID',
    'code_arr' : 'CODE_ARR',
    'code_dept' : 'CODE_DEPT',
    'nom_dept' : 'NOM_DEPT',
    'code_reg' : 'CODE_REG',
    'nom_reg' : 'NOM_REG',
    'geom' : 'MULTIPOLYGON',
}

cantons_shp = os.path.abspath(
    os.path.join(os.path.dirname(__file__), 'datas', 'France', 'Cantons', 'CANTON.SHP'),
)

def cantons_run(verbose=True):
    lm = LayerMapping(
        Cantons, cantons_shp, cantons_mapping,
        transform=False, encoding='iso-8859-1',
    )
    lm.save(strict=True, verbose=verbose)

departements_mapping = {
    'id_geofla' : 'ID_GEOFLA',
    'code_dept' : 'CODE_DEPT',
    'nom_dept' : 'NOM_DEPT',
    'code_chf' : 'CODE_CHF',
    'nom_chf' : 'NOM_CHF',
    'x_chf_lieu' : 'X_CHF_LIEU',
    'y_chf_lieu' : 'Y_CHF_LIEU',
    'x_centroid' : 'X_CENTROID',
    'y_centroid' : 'Y_CENTROID',
    'code_reg' : 'CODE_REG',
    'nom_reg' : 'NOM_REG',
    'geom' : 'MULTIPOLYGON',
}

departements_shp = os.path.abspath(
    os.path.join(os.path.dirname(__file__), 'datas', 'France', 'Departements', 'DEPARTEMENT.shp'),
)

def departements_run(verbose=True):
    lm = LayerMapping(
        Departements, departements_shp, departements_mapping,
        transform=False, encoding='iso-8859-1',
    )
    lm.save(strict=True, verbose=verbose)

communes_mapping = {
    'id_geofla' : 'ID_GEOFLA',
    'code_com' : 'CODE_COM',
    'insee_com' : 'INSEE_COM',
    'nom_com' : 'NOM_COM',
    'statut' : 'STATUT',
    'x_chf_lieu' : 'X_CHF_LIEU',
    'y_chf_lieu' : 'Y_CHF_LIEU',
    'x_centroid' : 'X_CENTROID',
    'y_centroid' : 'Y_CENTROID',
    'z_moyen' : 'Z_MOYEN',
    'superficie' : 'SUPERFICIE',
    'population' : 'POPULATION',
    'code_arr' : 'CODE_ARR',
    'code_dept' : 'CODE_DEPT',
    'nom_dept' : 'NOM_DEPT',
    'code_reg' : 'CODE_REG',
    'nom_reg' : 'NOM_REG',
    'geom' : 'MULTIPOLYGON',
}

communes_shp = os.path.abspath(
    os.path.join(os.path.dirname(__file__), 'datas', 'France', 'Communes', 'COMMUNE.shp'),
)

def communes_run(verbose=True):
    lm = LayerMapping(
        Communes, communes_shp, communes_mapping,
        transform=False, encoding='iso-8859-1',
    )
    lm.save(strict=True, verbose=verbose)


arrondissements_mapping = {
    'id_geofla' : 'ID_GEOFLA',
    'code_arr' : 'CODE_ARR',
    'code_chf' : 'CODE_CHF',
    'nom_chf' : 'NOM_CHF',
    'x_chf_lieu' : 'X_CHF_LIEU',
    'y_chf_lieu' : 'Y_CHF_LIEU',
    'x_centroid' : 'X_CENTROID',
    'y_centroid' : 'Y_CENTROID',
    'code_dept' : 'CODE_DEPT',
    'nom_dept' : 'NOM_DEPT',
    'code_reg' : 'CODE_REG',
    'nom_reg' : 'NOM_REG',
    'geom' : 'MULTIPOLYGON',
}

arrondissements_shp = os.path.abspath(
    os.path.join(os.path.dirname(__file__), 'datas', 'France', 'Arrondissements', 'ARRONDISSEMENT.shp'),
)

def arrondissements_run(verbose=True):
    lm = LayerMapping(
        Arrondissements, arrondissements_shp, arrondissements_mapping,
        transform=False, encoding='iso-8859-1',
    )
    lm.save(strict=True, verbose=verbose)

batiments_mapping = {
    'id_bat' : 'ID',
    'prec_plani' : 'PREC_PLANI',
    'prec_alti' : 'PREC_ALTI',
    'origin_bat' : 'ORIGIN_BAT',
    'hauteur' : 'HAUTEUR',
    'z_min' : 'Z_MIN',
    'z_max' : 'Z_MAX',
    'nature' : 'NATURE',
    'superficie' : 'SUPERFICIE',
    'etage' : 'ETAGE',
    's_tot' : 'S_TOT',
    'type_batim' : 'TYPE_BATIM',
    'e' : 'E',
    's_tot_2' : 's_tot_2',
    'e_surface' : 'E_surface',
    'e_bat' : 'E_BAT',
    'geom' : 'MULTIPOLYGON25D',
}

batiments_shp = os.path.abspath(
    os.path.join(os.path.dirname(__file__), 'datas', 'Bat', 'batiment_energie.shp'),
)

def batiments_run(verbose=True):
    lm = LayerMapping(
        Batiments, batiments_shp, batiments_mapping,
        transform=False, encoding='iso-8859-1',
    )
    lm.save(strict=True, verbose=verbose)

osmregions_mapping = {
    'insee' : 'insee',
    'nom' : 'nom',
    'wikipedia' : 'wikipedia',
    'wikidata' : 'wikidata',
    'surf_ha' : 'surf_ha',
    'geom' : 'MULTIPOLYGON',
}

osmregions_shp = os.path.abspath(
    os.path.join(os.path.dirname(__file__), 'datas', 'OSM', 'regions-20170102.shp'),
)

def osmregions_run(verbose=True):
    lm = LayerMapping(
        OSMRegions, osmregions_shp, osmregions_mapping,
        transform=False, encoding='utf-8',
    )
    lm.save(strict=True, verbose=verbose)


osmarrondissements_mapping = {
    'insee_ar' : 'insee_ar',
    'nom' : 'nom',
    'wikipedia' : 'wikipedia',
    'nb_comm' : 'nb_comm',
    'surf_km2' : 'surf_km2',
    'geom' : 'MULTIPOLYGON',
}
osmarrondissements_shp = os.path.abspath(
    os.path.join(os.path.dirname(__file__), 'datas', 'OSM', 'arrondissements-20131220-5m.shp'),
)

def osmarrondissements_run(verbose=True):
    lm = LayerMapping(
        OSMArrondissements, osmarrondissements_shp, osmarrondissements_mapping,
        transform=False, encoding='utf-8',
    )
    lm.save(strict=True, verbose=verbose)


osmcommunes_mapping = {
    'insee' : 'insee',
    'nom' : 'nom',
    'wikipedia' : 'wikipedia',
    'surf_m2' : 'surf_m2',
    'geom' : 'MULTIPOLYGON',
}
osmcommunes_shp = os.path.abspath(
    os.path.join(os.path.dirname(__file__), 'datas', 'OSM', 'communes-20150101-5m.shp'),
)

def osmcommunes_run(verbose=True):
    lm = LayerMapping(
        OSMCommunes, osmcommunes_shp, osmcommunes_mapping,
        transform=False, encoding='utf-8',
    )
    lm.save(strict=True, verbose=verbose)

osmdepartements_mapping = {
    'code_insee' : 'code_insee',
    'nom' : 'nom',
    'nuts3' : 'nuts3',
    'wikipedia' : 'wikipedia',
    'wikidata' : 'wikidata',
    'surf_ha' : 'surf_ha',
    'geom' : 'MULTIPOLYGON',
}
osmdepartements_shp = os.path.abspath(
    os.path.join(os.path.dirname(__file__), 'datas', 'OSM', 'departements-20170102.shp'),
)

def osmdepartements_run(verbose=True):
    lm = LayerMapping(
        OSMDepartements, osmdepartements_shp, osmdepartements_mapping,
        transform=False, encoding='utf-8',
    )
    lm.save(strict=True, verbose=verbose)
