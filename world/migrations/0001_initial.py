# -*- coding: utf-8 -*-
# Generated by Django 1.11.4 on 2017-10-12 13:59
from __future__ import unicode_literals

import django.contrib.gis.db.models.fields
import django.contrib.postgres.fields
import django.contrib.postgres.fields.hstore
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='OSMBuildingLine',
            fields=[
                ('osm_id', models.BigIntegerField(primary_key=True, serialize=False)),
                ('access', models.TextField(blank=True, null=True)),
                ('addr_housename', models.TextField(blank=True, db_column='addr:housename', null=True)),
                ('addr_housenumber', models.TextField(blank=True, db_column='addr:housenumber', null=True)),
                ('addr_interpolation', models.TextField(blank=True, db_column='addr:interpolation', null=True)),
                ('admin_level', models.TextField(blank=True, null=True)),
                ('aerialway', models.TextField(blank=True, null=True)),
                ('aeroway', models.TextField(blank=True, null=True)),
                ('amenity', models.TextField(blank=True, null=True)),
                ('area', models.TextField(blank=True, null=True)),
                ('barrier', models.TextField(blank=True, null=True)),
                ('bicycle', models.TextField(blank=True, null=True)),
                ('brand', models.TextField(blank=True, null=True)),
                ('bridge', models.TextField(blank=True, null=True)),
                ('boundary', models.TextField(blank=True, null=True)),
                ('building', models.TextField(blank=True, null=True)),
                ('construction', models.TextField(blank=True, null=True)),
                ('covered', models.TextField(blank=True, null=True)),
                ('culvert', models.TextField(blank=True, null=True)),
                ('cutting', models.TextField(blank=True, null=True)),
                ('denomination', models.TextField(blank=True, null=True)),
                ('disused', models.TextField(blank=True, null=True)),
                ('embankment', models.TextField(blank=True, null=True)),
                ('foot', models.TextField(blank=True, null=True)),
                ('generator_source', models.TextField(blank=True, db_column='generator:source', null=True)),
                ('harbour', models.TextField(blank=True, null=True)),
                ('highway', models.TextField(blank=True, null=True)),
                ('historic', models.TextField(blank=True, null=True)),
                ('horse', models.TextField(blank=True, null=True)),
                ('intermittent', models.TextField(blank=True, null=True)),
                ('junction', models.TextField(blank=True, null=True)),
                ('landuse', models.TextField(blank=True, null=True)),
                ('layer', models.TextField(blank=True, null=True)),
                ('leisure', models.TextField(blank=True, null=True)),
                ('lock', models.TextField(blank=True, null=True)),
                ('man_made', models.TextField(blank=True, null=True)),
                ('military', models.TextField(blank=True, null=True)),
                ('motorcar', models.TextField(blank=True, null=True)),
                ('name', models.TextField(blank=True, null=True)),
                ('natural', models.TextField(blank=True, null=True)),
                ('office', models.TextField(blank=True, null=True)),
                ('oneway', models.TextField(blank=True, null=True)),
                ('operator', models.TextField(blank=True, null=True)),
                ('place', models.TextField(blank=True, null=True)),
                ('population', models.TextField(blank=True, null=True)),
                ('power', models.TextField(blank=True, null=True)),
                ('power_source', models.TextField(blank=True, null=True)),
                ('public_transport', models.TextField(blank=True, null=True)),
                ('railway', models.TextField(blank=True, null=True)),
                ('ref', models.TextField(blank=True, null=True)),
                ('religion', models.TextField(blank=True, null=True)),
                ('route', models.TextField(blank=True, null=True)),
                ('service', models.TextField(blank=True, null=True)),
                ('shop', models.TextField(blank=True, null=True)),
                ('sport', models.TextField(blank=True, null=True)),
                ('surface', models.TextField(blank=True, null=True)),
                ('toll', models.TextField(blank=True, null=True)),
                ('tourism', models.TextField(blank=True, null=True)),
                ('tower_type', models.TextField(blank=True, db_column='tower:type', null=True)),
                ('tracktype', models.TextField(blank=True, null=True)),
                ('tunnel', models.TextField(blank=True, null=True)),
                ('water', models.TextField(blank=True, null=True)),
                ('waterway', models.TextField(blank=True, null=True)),
                ('wetland', models.TextField(blank=True, null=True)),
                ('width', models.TextField(blank=True, null=True)),
                ('wood', models.TextField(blank=True, null=True)),
                ('z_order', models.IntegerField(blank=True, null=True)),
                ('way_area', models.FloatField(blank=True, null=True)),
                ('tags', django.contrib.postgres.fields.hstore.HStoreField(blank=True, null=True)),
                ('way', django.contrib.gis.db.models.fields.LineStringField(blank=True, null=True, srid=2154)),
            ],
            options={
                'db_table': 'osm_building_line',
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='OSMBuildingNodes',
            fields=[
                ('id', models.BigIntegerField(primary_key=True, serialize=False)),
                ('lat', models.IntegerField()),
                ('lon', models.IntegerField()),
                ('tags', django.contrib.postgres.fields.hstore.HStoreField(blank=True, null=True)),
            ],
            options={
                'db_table': 'osm_building_nodes',
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='OSMBuildingPoint',
            fields=[
                ('osm_id', models.BigIntegerField(primary_key=True, serialize=False)),
                ('access', models.TextField(blank=True, null=True)),
                ('addr_housename', models.TextField(blank=True, db_column='addr:housename', null=True)),
                ('addr_housenumber', models.TextField(blank=True, db_column='addr:housenumber', null=True)),
                ('addr_interpolation', models.TextField(blank=True, db_column='addr:interpolation', null=True)),
                ('admin_level', models.TextField(blank=True, null=True)),
                ('aerialway', models.TextField(blank=True, null=True)),
                ('aeroway', models.TextField(blank=True, null=True)),
                ('amenity', models.TextField(blank=True, null=True)),
                ('area', models.TextField(blank=True, null=True)),
                ('barrier', models.TextField(blank=True, null=True)),
                ('bicycle', models.TextField(blank=True, null=True)),
                ('brand', models.TextField(blank=True, null=True)),
                ('bridge', models.TextField(blank=True, null=True)),
                ('boundary', models.TextField(blank=True, null=True)),
                ('building', models.TextField(blank=True, null=True)),
                ('capital', models.TextField(blank=True, null=True)),
                ('construction', models.TextField(blank=True, null=True)),
                ('covered', models.TextField(blank=True, null=True)),
                ('culvert', models.TextField(blank=True, null=True)),
                ('cutting', models.TextField(blank=True, null=True)),
                ('denomination', models.TextField(blank=True, null=True)),
                ('disused', models.TextField(blank=True, null=True)),
                ('ele', models.TextField(blank=True, null=True)),
                ('embankment', models.TextField(blank=True, null=True)),
                ('foot', models.TextField(blank=True, null=True)),
                ('generator_source', models.TextField(blank=True, db_column='generator:source', null=True)),
                ('harbour', models.TextField(blank=True, null=True)),
                ('highway', models.TextField(blank=True, null=True)),
                ('historic', models.TextField(blank=True, null=True)),
                ('horse', models.TextField(blank=True, null=True)),
                ('intermittent', models.TextField(blank=True, null=True)),
                ('junction', models.TextField(blank=True, null=True)),
                ('landuse', models.TextField(blank=True, null=True)),
                ('layer', models.TextField(blank=True, null=True)),
                ('leisure', models.TextField(blank=True, null=True)),
                ('lock', models.TextField(blank=True, null=True)),
                ('man_made', models.TextField(blank=True, null=True)),
                ('military', models.TextField(blank=True, null=True)),
                ('motorcar', models.TextField(blank=True, null=True)),
                ('name', models.TextField(blank=True, null=True)),
                ('natural', models.TextField(blank=True, null=True)),
                ('office', models.TextField(blank=True, null=True)),
                ('oneway', models.TextField(blank=True, null=True)),
                ('operator', models.TextField(blank=True, null=True)),
                ('place', models.TextField(blank=True, null=True)),
                ('population', models.TextField(blank=True, null=True)),
                ('power', models.TextField(blank=True, null=True)),
                ('power_source', models.TextField(blank=True, null=True)),
                ('public_transport', models.TextField(blank=True, null=True)),
                ('railway', models.TextField(blank=True, null=True)),
                ('ref', models.TextField(blank=True, null=True)),
                ('religion', models.TextField(blank=True, null=True)),
                ('route', models.TextField(blank=True, null=True)),
                ('service', models.TextField(blank=True, null=True)),
                ('shop', models.TextField(blank=True, null=True)),
                ('sport', models.TextField(blank=True, null=True)),
                ('surface', models.TextField(blank=True, null=True)),
                ('toll', models.TextField(blank=True, null=True)),
                ('tourism', models.TextField(blank=True, null=True)),
                ('tower_type', models.TextField(blank=True, db_column='tower:type', null=True)),
                ('tunnel', models.TextField(blank=True, null=True)),
                ('water', models.TextField(blank=True, null=True)),
                ('waterway', models.TextField(blank=True, null=True)),
                ('wetland', models.TextField(blank=True, null=True)),
                ('width', models.TextField(blank=True, null=True)),
                ('wood', models.TextField(blank=True, null=True)),
                ('z_order', models.IntegerField(blank=True, null=True)),
                ('tags', django.contrib.postgres.fields.hstore.HStoreField(blank=True, null=True)),
                ('way', django.contrib.gis.db.models.fields.PointField(blank=True, null=True, srid=2154)),
            ],
            options={
                'db_table': 'osm_building_point',
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='OSMBuildingPolygon',
            fields=[
                ('osm_id', models.BigIntegerField(primary_key=True, serialize=False)),
                ('access', models.TextField(blank=True, null=True)),
                ('addr_housename', models.TextField(blank=True, db_column='addr:housename', null=True)),
                ('addr_housenumber', models.TextField(blank=True, db_column='addr:housenumber', null=True)),
                ('addr_interpolation', models.TextField(blank=True, db_column='addr:interpolation', null=True)),
                ('admin_level', models.TextField(blank=True, null=True)),
                ('aerialway', models.TextField(blank=True, null=True)),
                ('aeroway', models.TextField(blank=True, null=True)),
                ('amenity', models.TextField(blank=True, null=True)),
                ('area', models.TextField(blank=True, null=True)),
                ('barrier', models.TextField(blank=True, null=True)),
                ('bicycle', models.TextField(blank=True, null=True)),
                ('brand', models.TextField(blank=True, null=True)),
                ('bridge', models.TextField(blank=True, null=True)),
                ('boundary', models.TextField(blank=True, null=True)),
                ('building', models.TextField(blank=True, null=True)),
                ('construction', models.TextField(blank=True, null=True)),
                ('covered', models.TextField(blank=True, null=True)),
                ('culvert', models.TextField(blank=True, null=True)),
                ('cutting', models.TextField(blank=True, null=True)),
                ('denomination', models.TextField(blank=True, null=True)),
                ('disused', models.TextField(blank=True, null=True)),
                ('embankment', models.TextField(blank=True, null=True)),
                ('foot', models.TextField(blank=True, null=True)),
                ('generator_source', models.TextField(blank=True, db_column='generator:source', null=True)),
                ('harbour', models.TextField(blank=True, null=True)),
                ('highway', models.TextField(blank=True, null=True)),
                ('historic', models.TextField(blank=True, null=True)),
                ('horse', models.TextField(blank=True, null=True)),
                ('intermittent', models.TextField(blank=True, null=True)),
                ('junction', models.TextField(blank=True, null=True)),
                ('landuse', models.TextField(blank=True, null=True)),
                ('layer', models.TextField(blank=True, null=True)),
                ('leisure', models.TextField(blank=True, null=True)),
                ('lock', models.TextField(blank=True, null=True)),
                ('man_made', models.TextField(blank=True, null=True)),
                ('military', models.TextField(blank=True, null=True)),
                ('motorcar', models.TextField(blank=True, null=True)),
                ('name', models.TextField(blank=True, null=True)),
                ('natural', models.TextField(blank=True, null=True)),
                ('office', models.TextField(blank=True, null=True)),
                ('oneway', models.TextField(blank=True, null=True)),
                ('operator', models.TextField(blank=True, null=True)),
                ('place', models.TextField(blank=True, null=True)),
                ('population', models.TextField(blank=True, null=True)),
                ('power', models.TextField(blank=True, null=True)),
                ('power_source', models.TextField(blank=True, null=True)),
                ('public_transport', models.TextField(blank=True, null=True)),
                ('railway', models.TextField(blank=True, null=True)),
                ('ref', models.TextField(blank=True, null=True)),
                ('religion', models.TextField(blank=True, null=True)),
                ('route', models.TextField(blank=True, null=True)),
                ('service', models.TextField(blank=True, null=True)),
                ('shop', models.TextField(blank=True, null=True)),
                ('sport', models.TextField(blank=True, null=True)),
                ('surface', models.TextField(blank=True, null=True)),
                ('toll', models.TextField(blank=True, null=True)),
                ('tourism', models.TextField(blank=True, null=True)),
                ('tower_type', models.TextField(blank=True, db_column='tower:type', null=True)),
                ('tracktype', models.TextField(blank=True, null=True)),
                ('tunnel', models.TextField(blank=True, null=True)),
                ('water', models.TextField(blank=True, null=True)),
                ('waterway', models.TextField(blank=True, null=True)),
                ('wetland', models.TextField(blank=True, null=True)),
                ('width', models.TextField(blank=True, null=True)),
                ('wood', models.TextField(blank=True, null=True)),
                ('z_order', models.IntegerField(blank=True, null=True)),
                ('way_area', models.FloatField(blank=True, null=True)),
                ('tags', django.contrib.postgres.fields.hstore.HStoreField(blank=True, null=True)),
                ('way', django.contrib.gis.db.models.fields.GeometryField(blank=True, null=True, srid=2154)),
            ],
            options={
                'db_table': 'osm_building_polygon',
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='OSMBuildingRels',
            fields=[
                ('id', models.BigIntegerField(primary_key=True, serialize=False)),
                ('way_off', models.SmallIntegerField(blank=True, null=True)),
                ('rel_off', models.SmallIntegerField(blank=True, null=True)),
                ('parts', django.contrib.postgres.fields.ArrayField(base_field=models.BigIntegerField(), blank=True, null=True, size=None)),
                ('members', django.contrib.postgres.fields.ArrayField(base_field=models.TextField(), blank=True, null=True, size=None)),
                ('tags', django.contrib.postgres.fields.ArrayField(base_field=models.TextField(), blank=True, null=True, size=None)),
            ],
            options={
                'db_table': 'osm_building_rels',
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='OSMBuildingRoads',
            fields=[
                ('osm_id', models.BigIntegerField(primary_key=True, serialize=False)),
                ('access', models.TextField(blank=True, null=True)),
                ('addr_housename', models.TextField(blank=True, db_column='addr:housename', null=True)),
                ('addr_housenumber', models.TextField(blank=True, db_column='addr:housenumber', null=True)),
                ('addr_interpolation', models.TextField(blank=True, db_column='addr:interpolation', null=True)),
                ('admin_level', models.TextField(blank=True, null=True)),
                ('aerialway', models.TextField(blank=True, null=True)),
                ('aeroway', models.TextField(blank=True, null=True)),
                ('amenity', models.TextField(blank=True, null=True)),
                ('area', models.TextField(blank=True, null=True)),
                ('barrier', models.TextField(blank=True, null=True)),
                ('bicycle', models.TextField(blank=True, null=True)),
                ('brand', models.TextField(blank=True, null=True)),
                ('bridge', models.TextField(blank=True, null=True)),
                ('boundary', models.TextField(blank=True, null=True)),
                ('building', models.TextField(blank=True, null=True)),
                ('construction', models.TextField(blank=True, null=True)),
                ('covered', models.TextField(blank=True, null=True)),
                ('culvert', models.TextField(blank=True, null=True)),
                ('cutting', models.TextField(blank=True, null=True)),
                ('denomination', models.TextField(blank=True, null=True)),
                ('disused', models.TextField(blank=True, null=True)),
                ('embankment', models.TextField(blank=True, null=True)),
                ('foot', models.TextField(blank=True, null=True)),
                ('generator_source', models.TextField(blank=True, db_column='generator:source', null=True)),
                ('harbour', models.TextField(blank=True, null=True)),
                ('highway', models.TextField(blank=True, null=True)),
                ('historic', models.TextField(blank=True, null=True)),
                ('horse', models.TextField(blank=True, null=True)),
                ('intermittent', models.TextField(blank=True, null=True)),
                ('junction', models.TextField(blank=True, null=True)),
                ('landuse', models.TextField(blank=True, null=True)),
                ('layer', models.TextField(blank=True, null=True)),
                ('leisure', models.TextField(blank=True, null=True)),
                ('lock', models.TextField(blank=True, null=True)),
                ('man_made', models.TextField(blank=True, null=True)),
                ('military', models.TextField(blank=True, null=True)),
                ('motorcar', models.TextField(blank=True, null=True)),
                ('name', models.TextField(blank=True, null=True)),
                ('natural', models.TextField(blank=True, null=True)),
                ('office', models.TextField(blank=True, null=True)),
                ('oneway', models.TextField(blank=True, null=True)),
                ('operator', models.TextField(blank=True, null=True)),
                ('place', models.TextField(blank=True, null=True)),
                ('population', models.TextField(blank=True, null=True)),
                ('power', models.TextField(blank=True, null=True)),
                ('power_source', models.TextField(blank=True, null=True)),
                ('public_transport', models.TextField(blank=True, null=True)),
                ('railway', models.TextField(blank=True, null=True)),
                ('ref', models.TextField(blank=True, null=True)),
                ('religion', models.TextField(blank=True, null=True)),
                ('route', models.TextField(blank=True, null=True)),
                ('service', models.TextField(blank=True, null=True)),
                ('shop', models.TextField(blank=True, null=True)),
                ('sport', models.TextField(blank=True, null=True)),
                ('surface', models.TextField(blank=True, null=True)),
                ('toll', models.TextField(blank=True, null=True)),
                ('tourism', models.TextField(blank=True, null=True)),
                ('tower_type', models.TextField(blank=True, db_column='tower:type', null=True)),
                ('tracktype', models.TextField(blank=True, null=True)),
                ('tunnel', models.TextField(blank=True, null=True)),
                ('water', models.TextField(blank=True, null=True)),
                ('waterway', models.TextField(blank=True, null=True)),
                ('wetland', models.TextField(blank=True, null=True)),
                ('width', models.TextField(blank=True, null=True)),
                ('wood', models.TextField(blank=True, null=True)),
                ('z_order', models.IntegerField(blank=True, null=True)),
                ('way_area', models.FloatField(blank=True, null=True)),
                ('tags', django.contrib.postgres.fields.hstore.HStoreField(blank=True, null=True)),
                ('way', django.contrib.gis.db.models.fields.LineStringField(blank=True, null=True, srid=2154)),
            ],
            options={
                'db_table': 'osm_building_roads',
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='OSMBuildingWays',
            fields=[
                ('id', models.BigIntegerField(primary_key=True, serialize=False)),
                ('nodes', django.contrib.postgres.fields.ArrayField(base_field=models.BigIntegerField(), size=None)),
                ('tags', django.contrib.postgres.fields.ArrayField(base_field=models.TextField(), blank=True, null=True, size=None)),
            ],
            options={
                'db_table': 'osm_building_ways',
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='Arrondissements',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('id_geofla', models.CharField(max_length=24)),
                ('code_arr', models.CharField(max_length=1)),
                ('code_chf', models.CharField(max_length=3)),
                ('nom_chf', models.CharField(max_length=50)),
                ('x_chf_lieu', models.IntegerField()),
                ('y_chf_lieu', models.IntegerField()),
                ('x_centroid', models.IntegerField()),
                ('y_centroid', models.IntegerField()),
                ('code_dept', models.CharField(max_length=2)),
                ('nom_dept', models.CharField(max_length=30)),
                ('code_reg', models.CharField(max_length=2)),
                ('nom_reg', models.CharField(max_length=35)),
                ('geom', django.contrib.gis.db.models.fields.MultiPolygonField(srid=2154)),
            ],
        ),
        migrations.CreateModel(
            name='Batiments',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('id_bat', models.CharField(max_length=24)),
                ('geocode_com', models.CharField(default='', max_length=7)),
                ('prec_plani', models.FloatField()),
                ('prec_alti', models.FloatField()),
                ('origin_bat', models.CharField(max_length=8)),
                ('hauteur', models.IntegerField()),
                ('z_min', models.FloatField()),
                ('z_max', models.FloatField()),
                ('nature', models.CharField(max_length=51)),
                ('superficie', models.FloatField()),
                ('etage', models.BigIntegerField()),
                ('s_tot', models.FloatField()),
                ('type_batim', models.CharField(max_length=254)),
                ('e', models.CharField(max_length=254)),
                ('s_tot_2', models.CharField(max_length=254)),
                ('e_surface', models.CharField(max_length=254)),
                ('e_bat', models.FloatField()),
                ('geom', django.contrib.gis.db.models.fields.MultiPolygonField(srid=2154)),
            ],
        ),
        migrations.CreateModel(
            name='Cantons',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('id_geofla', models.CharField(max_length=24)),
                ('code_cant', models.CharField(max_length=2)),
                ('code_chf', models.CharField(max_length=3)),
                ('nom_chf', models.CharField(max_length=50)),
                ('x_chf_lieu', models.IntegerField()),
                ('y_chf_lieu', models.IntegerField()),
                ('x_centroid', models.IntegerField()),
                ('y_centroid', models.IntegerField()),
                ('code_arr', models.CharField(max_length=1)),
                ('code_dept', models.CharField(max_length=2)),
                ('nom_dept', models.CharField(max_length=30)),
                ('code_reg', models.CharField(max_length=2)),
                ('nom_reg', models.CharField(max_length=30)),
                ('geom', django.contrib.gis.db.models.fields.MultiPolygonField(srid=2154)),
            ],
        ),
        migrations.CreateModel(
            name='Communes',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('id_geofla', models.CharField(max_length=24)),
                ('code_com', models.CharField(max_length=3)),
                ('insee_com', models.CharField(max_length=5)),
                ('nom_com', models.CharField(max_length=50)),
                ('statut', models.CharField(max_length=30)),
                ('x_chf_lieu', models.IntegerField()),
                ('y_chf_lieu', models.IntegerField()),
                ('x_centroid', models.IntegerField()),
                ('y_centroid', models.IntegerField()),
                ('z_moyen', models.IntegerField()),
                ('superficie', models.BigIntegerField()),
                ('population', models.BigIntegerField()),
                ('code_arr', models.CharField(max_length=1)),
                ('code_dept', models.CharField(max_length=2)),
                ('nom_dept', models.CharField(max_length=30)),
                ('code_reg', models.CharField(max_length=2)),
                ('nom_reg', models.CharField(max_length=35)),
                ('geom', django.contrib.gis.db.models.fields.MultiPolygonField(srid=2154)),
            ],
        ),
        migrations.CreateModel(
            name='Departements',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('id_geofla', models.CharField(max_length=24)),
                ('code_dept', models.CharField(max_length=2)),
                ('nom_dept', models.CharField(max_length=30)),
                ('code_chf', models.CharField(max_length=3)),
                ('nom_chf', models.CharField(max_length=50)),
                ('x_chf_lieu', models.IntegerField()),
                ('y_chf_lieu', models.IntegerField()),
                ('x_centroid', models.IntegerField()),
                ('y_centroid', models.IntegerField()),
                ('code_reg', models.CharField(max_length=2)),
                ('nom_reg', models.CharField(max_length=35)),
                ('geom', django.contrib.gis.db.models.fields.MultiPolygonField(srid=2154)),
            ],
        ),
        migrations.CreateModel(
            name='WorldBorder',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50)),
                ('area', models.IntegerField()),
                ('pop2005', models.IntegerField(verbose_name='Population 2005')),
                ('fips', models.CharField(max_length=2, verbose_name='FIPS Code')),
                ('iso2', models.CharField(max_length=2, verbose_name='2 Digit ISO')),
                ('iso3', models.CharField(max_length=3, verbose_name='3 Digit ISO')),
                ('un', models.IntegerField(verbose_name='United Nations Code')),
                ('region', models.IntegerField(verbose_name='Region Code')),
                ('subregion', models.IntegerField(verbose_name='Sub-Region Code')),
                ('lon', models.FloatField()),
                ('lat', models.FloatField()),
                ('geom', django.contrib.gis.db.models.fields.MultiPolygonField(srid=4326)),
            ],
        ),
    ]
