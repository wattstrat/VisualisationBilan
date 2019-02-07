"""
Django settings for wattstrat project.

For more information on this file, see
https://docs.djangoproject.com/en/dev/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/dev/ref/settings/
"""
import os
from django.core.exceptions import ImproperlyConfigured
from .env import env
from .components.dir import *
from .components.db import *
from .components.auth import *
from .components.log import *
from .components.simulation import *
from .components.wattstrat import *

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/dev/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
# Raises ImproperlyConfigured exception if SECRET_KEY not in os.environ
SECRET_KEY = env('SECRET_KEY')

ALLOWED_HOSTS = []
DOMAIN = "__DOMAIN__"

# Application definition

INSTALLED_APPS = (
    'django_admin_bootstrapped',

    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.postgres',
    'django.contrib.gis',
    'djng',

    'rest_framework',
    'authtools',
    'bootstrap3',
    'crispy_forms',
    'easy_thumbnails',
    'envelope',
    'storages',
    'maintenance_mode',
#    'djgeojson',
#    'leaflet',

    'world',

    'wattstrat.accounts',
    'wattstrat.simulation',
)

MIDDLEWARE_CLASSES = (
    'djng.middleware.AngularUrlMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.auth.middleware.SessionAuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'maintenance_mode.middleware.MaintenanceModeMiddleware',
)

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',

                'wattstrat.context_processor.simulation',
            ],
        },
    }]

ROOT_URLCONF = 'wattstrat.urls'

# Database
# https://docs.djangoproject.com/en/dev/ref/settings/#databases

try:
    DATABASES = {
        'default': env.db(),
    }
except ImproperlyConfigured:
    DATABASES = {}


# Internationalization
# https://docs.djangoproject.com/en/dev/topics/i18n/

LANGUAGE_CODE = 'fr'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True

DEFAULT_FROM_EMAIL = "ws@wattstrat.com"

# Crispy Form Theme - Bootstrap 3
CRISPY_TEMPLATE_PACK = 'bootstrap3'

# For Bootstrap 3, change error alert to 'danger'
from django.contrib import messages
MESSAGE_TAGS = {
    messages.ERROR: 'danger'
}

THUMBNAIL_EXTENSION = 'png'  # Or any extn for your thumbnails

# URL du wiki interne
WIKI_UPSTREAM = 'http://wiki.guide.wattstrat.com/guide/'

# no other DB for results
MONGO_CONFIG_BY_ID = {}
# Special simulation settings
SIMU_CONFIG_BY_ID = {}
