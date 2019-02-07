# Config on DBs
from wattstrat.settings.env import env

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': env('RDS_DB_NAME', default="ener"),
        'USER': env('RDS_USERNAME', default="ener"),
        'PASSWORD': env('RDS_PASSWORD', default="ener"),
        'HOST': env('RDS_HOSTNAME', default="localhost"),
        'PORT': env('RDS_PORT', default="5432")
    },
    # 'migration': {
    #     'ENGINE': 'django.db.backends.postgresql_psycopg2',
    #     'NAME': env('RDS_DB_NAME'),
    #     'USER': env('RDS_USERNAME_MIGRATION'),
    #     'PASSWORD': env('RDS_PASSWORD_MIGRATION'),
    #     'HOST': env('RDS_HOSTNAME'),
    #     'PORT': env('RDS_PORT')
    # },
    'world': {
        'ENGINE': 'django.contrib.gis.db.backends.postgis',
        'NAME': env('RDSWORLD_DB_NAME', default="world"),
        'USER': env('RDSWORLD_USERNAME', default="ener"),
        'PASSWORD': env('RDSWORLD_PASSWORD', default="ener"),
        'HOST': env('RDSWORLD_HOSTNAME', default="localhost"),
        'PORT': env('RDSWORLD_PORT', default="5432")
    }
}

DATABASE_ROUTERS = ['world.dbRouter.WorldDatabaseRouter']
