from path import Path

# Build paths inside the project like this: BASE_DIR / ...
SETTINGS_DIR = Path(__file__).parent.parent
BASE_DIR = SETTINGS_DIR.parent.parent

STATICFILES_DIRS = (
    BASE_DIR / 'static',
)
# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/dev/howto/static-files/
STATIC_URL = '/static/'

LOCALE_PATHS = (
    BASE_DIR / 'locale',
)

MEDIA_ROOT = BASE_DIR / 'media'
MEDIA_URL = "/media/"

FILERESULTS_ROOT = BASE_DIR / 'filesdownload'
FILERESULTS_URL = r'^filesdownload/.*$'
