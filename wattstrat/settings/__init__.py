# In production set the environment variable like this
# $ export DJANGO_SETTINGS_MODULE=wattstrat.settings.production
import logging
logger = logging.getLogger(__name__)

try:
    from .development import *
except ImportError as e:
    logger.warning("Warning : settings.development is not imported\n%s", str(e))
    pass
