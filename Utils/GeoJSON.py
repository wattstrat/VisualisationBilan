import geojson
import json

from scripts.constants import PY_OUT_DIR, SHAPES_OUT_DIR

if __debug__:
    import logging
    logger = logging.getLogger(__name__)


class GeoJSON(object):
    # This is a cache of the ~20Mo dictionnary of geojson features per geocode
    # Load it on the first call to this view to speed up server launching
    geojson_features = None
    def __init__(self, geocodes=None):
        self._geocodes = geocodes

    @staticmethod
    def _load():
        if GeoJSON.geojson_features is None:
            GeoJSON.load_geojson_features()

    @property
    def features(self):
        GeoJSON._load()

        if self._geocodes is None:
            return GeoJSON.geojson_features

        return GeoJSON.get_geojson(self._geocodes)

    @property
    def jsonFeatures(self):
         return geojson.dumps(self.features)
         
    @staticmethod
    def load_geojson_features():
        country = "france"
        GeoJSON.geojson_features = \
            json.load(open(PY_OUT_DIR / country / 'geojson_features.json', encoding='utf-8'))
        # France country is homemade
        FeatureCollection = json.load(open(SHAPES_OUT_DIR / country / 'FR99999.geojson', encoding='utf-8'))
        GeoJSON.geojson_features['FR99999'] = FeatureCollection['features'][0]
        

    @staticmethod
    def get_geojson(geocodes):
        features = []
        for geocode in geocodes:
            features.append(GeoJSON.geojson_features[geocode])
        return geojson.FeatureCollection(features)
