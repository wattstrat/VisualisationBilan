#================
# ERROR LOGGING
#================
from .dir import BASE_DIR
from ..env import env
import path

FILE_LOG_DIR = path.Path(env('FILE_LOG_DIR'))
FILE_LOG_PATH = FILE_LOG_DIR / 'error.log'

if not FILE_LOG_DIR.exists():
    FILE_LOG_DIR.makedirs()

LOGGING = {
    'version': 1,
    'disable_existing_loggers': True,
    'formatters': {
        'verbose': {
            'format': '%(asctime)s %(levelname)s %(filename)s %(funcName)s:%(lineno)d %(message)s'
        },
        'simple': {
            'format': '%(levelname)s %(message)s'
        },
    },
    'filters': {
        'require_debug_false': {
            '()': 'django.utils.log.RequireDebugFalse',
        },
        'require_debug_true': {
            '()': 'django.utils.log.RequireDebugTrue',
        },
    },
    'handlers': {
        'null': {
            'level': 'DEBUG',
            'class': 'logging.NullHandler',
        },
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'filters': ['require_debug_true'],
            'formatter': 'simple'
        },
        'mail_admins': {
            'level': 'ERROR',
            'class': 'django.utils.log.AdminEmailHandler',
            'filters': ['require_debug_false'],
            'formatter': 'simple'
        },
        'write_file': {
            'level': 'INFO',
            'class': 'logging.handlers.TimedRotatingFileHandler',
            'formatter': 'verbose',
            'filename': FILE_LOG_PATH,
            'when': 'W0',
            'interval': 1
        }
    },
    'loggers': {
        'django': {
            'handlers': ['console', 'null'],
            'propagate': True,
            'level': 'INFO',
        },
        'django.request': {
            'handlers': ['console', 'mail_admins', 'write_file'],
            'level': 'INFO',
            'propagate': False,
        },
        'wattstrat': {
            'handlers': ['console', 'write_file', 'mail_admins'],
            'level': 'INFO',
        },
        'rocket': {
            'handlers': ['console'],
            'level': 'INFO',
        },
    }
}
