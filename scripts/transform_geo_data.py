#!/usr/bin/python3
import json
from collections import namedtuple

from path import Path
import geojson
import copy
import itertools
import utils

from constants import FRANCE_COUNTIES_PER_PROVINCE, GEO_DATA_INPUT_DIR, PY_OUT_DIR
from constants import SHAPES_OUT_DIR, GEOCODES_OUT_DIR, COUNTRY, COUNTIES, CITIES, TERRITORY_SCALES

Country = namedtuple('Country', ['name', 'prefix'])
France = Country('france', 'FR')


class GeoDataTransformer(object):

    def __init__(self, country):
        self.country = country
        self.country_geocode = self.make_geocode('99', scale=COUNTRY)

        self.geocodes = {
            COUNTRY: {'geocode': self.country_geocode, 'label': country.name.capitalize()},
            COUNTIES: [],
            CITIES: []
        }

        # geocode -> geojson
        self.all_geojsons = {}

        # geocode -> geojson feature
        self.geojson_features = {}

        # geocode -> label
        self.geocode_labels = {}

        # county geocode --> [city geocode, city_geocode...]
        self.cities_per_county = {}

    def read_resources(self):
        geojson_input_dir = GEO_DATA_INPUT_DIR / self.country.name / 'geojson'

        # TODO : move file provisionning in a country-agnostic code block

        # Read the "counties in the country" file
        self.current_scale = COUNTIES
        geojson_file = geojson_input_dir / 'departements.geojson'
        geojson = self.read_geojson_file(geojson_file)
        self.all_geojsons[self.country_geocode] = geojson

        # Read the "cities in one county" files
        self.current_scale = CITIES
        for county_dir in (geojson_input_dir / 'departements').dirs():
            county_id = str(county_dir.basename())
            if self.should_skip_county(county_id):
                continue

            geojson_file = county_dir / 'communes.geojson'
            geojson = self.read_geojson_file(geojson_file)
            county_geocode = self.make_geocode(county_id, COUNTIES)
            self.all_geojsons[county_geocode] = geojson

        headers = None
        self.geodetails = {'france': {}}
        with open(GEO_DATA_INPUT_DIR / self.country.name / 'geodetails.csv', encoding='utf-8') as f:
            for line in f:
                if headers is None:
                    headers = line.split(";")[1::]
                else:
                    data = line.split(";")
                    self.geodetails[self.country.name][data[0]] = dict(zip(headers, data[1::]))

    def should_skip_county(self, county_id):
        return county_id.upper() in ["2A", "2B"]

    def read_geojson_file(self, geojson_file):
        geodata = geojson.load(geojson_file.open())
        indexes_to_remove = []
        for i, feature in enumerate(geodata.features):
            label = feature.properties['nom']
            territory_id = feature.properties['code']
            del feature.properties['nom']
            del feature.properties['code']

            # Remove undesired counties from the country map
            if self.current_scale == COUNTIES and self.should_skip_county(territory_id):
                # Add highest indexes first, so we'll remove them from higher to lower
                indexes_to_remove.insert(0, i)
                continue

            geocode = self.make_geocode(territory_id)

            feature.properties['name'] = label
            feature.properties['geocode'] = geocode

            # 2/ Make geocode for autocompletion
            self.geocodes[self.current_scale].append({
                'geocode': geocode,
                'label': self.make_geocode_label(geocode, label)
            })

            # 3/ Make geocode mapping for python
            if self.current_scale == CITIES:
                county_id = territory_id[:2]
                county_geocode = self.make_geocode(county_id, COUNTIES)
                self.cities_per_county.setdefault(county_geocode, []).append(geocode)

            self.geocode_labels[geocode] = label

            # 4/ Make geojson mapping for python (for dynamig geojson FeatureCollections)
            self.geojson_features[geocode] = feature

        # Remove skipped features
        for index in indexes_to_remove:
            del geodata.features[index]

        return geodata

    def make_geocode(self, territory_id, scale=None):
        if not scale:
            scale = self.current_scale

        geocode = self.country.prefix
        if scale == COUNTRY:
            geocode += '999'
        elif scale == COUNTIES:
            geocode += '992'
        elif scale == CITIES:
            # The 9 first department have their INSEE in the form 1500 instead of 01500
            if len(territory_id) == 4:
                territory_id = '0' + territory_id

        geocode += territory_id
        return geocode

    def make_geocode_label(self, geocode, label):
        if self.current_scale == COUNTIES:
            label = "{} - {}".format(label, geocode[-2:])
        elif self.current_scale == CITIES:
            label = "{} ({})".format(label, geocode[2:4])
        return label

    def write_files(self):
        shapes_out_dir = SHAPES_OUT_DIR / self.country.name
        shapes_out_dir.makedirs_p()
        GEOCODES_OUT_DIR.makedirs_p()

        for geocode, geojson in self.all_geojsons.items():
            geojson_file = shapes_out_dir / "sub" + geocode + ".geojson"
            self.write_json(geojson_file, geojson)
            # Split all cities
            for geocity in geojson["features"]:
                geocodecity = geocity["properties"]["geocode"]
                geojsoncity = {"type": "FeatureCollection","features": [geocity]}
                geojsoncity_file = shapes_out_dir / geocodecity + ".geojson"
                self.write_json(geojsoncity_file, geojsoncity)

        # Geocodes
        # Postal
        for geo in self.geocodes["counties"]:
            geo["postal"] = geo["geocode"][-2:]
        for geo in self.geocodes["cities"]:
            geo["postal"] = self.geodetails[self.country.name][geo["geocode"][-5:]]["postal_code"]
        self.geocodes["country"]["postal"] = "FR"

        # Write country info
        self.write_json(GEOCODES_OUT_DIR / (self.country.name + '.country.json'), self.geocodes["country"])


        # Python mappings
        py_out_dir = PY_OUT_DIR / self.country.name
        py_out_dir.makedirs_p()

        geocode_mapping = {
            self.country_geocode: list(self.cities_per_county.keys())
        }

        # Label for geocode country is missing : add it
        self.geocode_labels['FR99999'] = 'France'
        
        geocode_mapping.update(self.cities_per_county)
        content = "'''Auto-generated content, do not edit'''\n\n"
        content += "geocode_mapping = {}\n".format(str(geocode_mapping))
        content += "geocode_labels = {}".format(str(self.geocode_labels))

        # Write python mappings
        (py_out_dir / 'geocode_mapping.py').write_text(content, encoding='utf-8', linesep='\n')

        # Write GeoJSON features
        self.write_json((py_out_dir / 'geojson_features.json'), self.geojson_features)
        geo = {g['geocode']: g for g in itertools.chain(iter([self.geocodes["country"]]), iter(self.geocodes["counties"]), iter(self.geocodes["cities"]))}
        for g, dG in geo.items():
            dG["name"] = self.geocode_labels[g]
            dG["sub"] = geocode_mapping.get(g, [g])
            dG["includes"] = geocode_mapping.get(g, [g])
            dG["labelmatch"] = utils.latinize(dG["label"]).replace("-", " ").lower()
            
            if g == 'FR99999':
                dG["order"] = 10
            elif g[0:5] == 'FR992':
                dG["order"] = 20
            else:
                dG["order"] = 30
            # Real geocode
            dG["_type"] = 0
            
        # Write Geocode Info            
        self.write_json(GEOCODES_OUT_DIR / (self.country.name + '.json'), geo)

    def write_json(self, file, dict):
        file.write_text(json.dumps(dict, ensure_ascii=False), encoding='utf-8')


def transform_all():
    transformer = GeoDataTransformer(France)
    transformer.read_resources()
    transformer.write_files()

if __name__ == '__main__':
    transform_all()
