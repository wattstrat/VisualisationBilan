FILE_LOG_PATH = '/var/log/saas'

from .base import *
from .migrations import *


# Tell django-storages that when coming up with the URL for an item in S3 storage, keep
# it simple - just use this domain plus the path. (If this isn't set, things get complicated).
# This controls how the `static` template tag from `staticfiles` gets expanded, if you're using it.
# We also use it in the next setting.

ALLOWED_HOSTS = ['__PROD_HOSTNAME__']


STATIC_URL = "/static/"
MEDIA_URL = "/media/"

ENVELOPE_EMAIL_RECIPIENTS = (
    '__EMAIL__',
)

EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = '__HOST__'
EMAIL_USE_TLS = True
EMAIL_PORT = 587
EMAIL_HOST_USER = '__HOSTUSER__'
EMAIL_HOST_PASSWORD = '__PASSWORD__'
ENVELOPE_EMAIL_RECIPIENTS = ['__EMAIL__']

WSGI_APPLICATION = 'wattstrat.wsgi.application'

# http://stackoverflow.com/questions/14813314/hosting-a-django-project-behind-proxypass
USE_X_FORWARDED_HOST = True

MAINTENANCE_MODE_IGNORE_SUPERUSER = True
MAINTENANCE_MODE_STATE_FILE_PATH = 'maintenance/maintenance_mode_state.txt'

SIMU_CONFIG_BY_ID = {'bilan2012': {},'bilan2013': {},'bilan2014': {},'bilan2015': {},'bilan2016': {}}
