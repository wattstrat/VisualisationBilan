FILE_LOG_PATH = './log/'
from .base import *

ALLOWED_HOSTS = ['127.0.0.1', 'localhost']

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

for template in TEMPLATES:
    template['OPTIONS'].update({'debug': True})
    template['OPTIONS']['context_processors'].append(
        'django.template.context_processors.debug')

#TEMPLATE_DEBUG = True
# Show thumbnail generation errors
THUMBNAIL_DEBUG = True

try:
    DATABASES = {
        'default': {'ENGINE': 'django.db.backends.sqlite3',
                    'NAME': os.path.join(BASE_DIR, 'db.sqlite3')},
        'world': {
            'ENGINE': 'django.contrib.gis.db.backends.postgis',
            'NAME': 'world',
            'USER': 'worlduser',
            'PASSWORD': 'worldpassword',
            'HOST': '127.0.0.1',
            'PORT': '5432',
        },
    }
except ImproperlyConfigured:
    DATABASES = {}


def show_toolbar(request):
    host = request.META.get('HTTP_HOST')

    if host in ALLOWED_HOSTS:
        return True

    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')

    if ip == "127.0.0.1":
        return True
    return False


DEBUG_TOOLBAR_CONFIG = {
    "SHOW_TOOLBAR_CALLBACK": show_toolbar,
}

MONGO_HOST = '127.0.0.1'
MONGO_PORT = 27017

# Django Debug Toolbar
INSTALLED_APPS += ('debug_toolbar.apps.DebugToolbarConfig',)
MIDDLEWARE_CLASSES += ('debug_toolbar.middleware.DebugToolbarMiddleware',)

# Show emails to console in DEBUG mode

EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = '__SMTP_HOST__'
EMAIL_USE_TLS = True
EMAIL_PORT = 587
EMAIL_HOST_USER = '__SMTP_USER__'
EMAIL_HOST_PASSWORD = '__SMTP_PASSWORD__'
ENVELOPE_EMAIL_RECIPIENTS = ['__EMAIL_RECIPIENT__']


