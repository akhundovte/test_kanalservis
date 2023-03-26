import os
from logging import Filter

from pathlib import Path
from sqlalchemy.engine.url import URL
from datetime import timedelta

from .utils import get_config


BASE_DIR = Path(__file__).parent.parent.parent
SETTINGS_DIR = Path(__file__).parent

LOGS_DIR = BASE_DIR.joinpath('logs')
LOGS_DIR.mkdir(exist_ok=True, parents=True)

config_key = os.environ.get('CONFIG', 'dev')

configs_dir = SETTINGS_DIR / 'configs'
config_path = configs_dir / f'config_{config_key}.yaml'

config = get_config(config_path)

TIME_ZONE = config['timezone']

DEBUG = config['debug']

CONFIG_DB = {
    'drivername': config['db']['drivername'],
    'username': config['db']['username'],
    'password': config['db']['password'],
    'host': config['db']['host'],
    'port': config['db'].get('port'),
    'database': config['db']['database'],
    }
DB_URI = URL.create(**CONFIG_DB)
DB_SCHEMA = config['db']['schema']
DB_DRIVER_ECHO = config['db']['echo']

GOOGLE_KEY_PATH = SETTINGS_DIR.joinpath('configs', config['google_filename_key'])

JOB_PERIODIC_START_OFFSET = timedelta(seconds=5)

# APScheduler
PARAMS_PERIODIC_JOB_TRIG = {
    # for IntervalTrigger
    # 'seconds': 30,
    'minutes': 15,
    }


class RequireDebugTrue(Filter):
    def filter(self, record):
        return DEBUG


class RequireDebugFalse(Filter):
    def filter(self, record):
        return not DEBUG


def get_settings_logging(filename):
    return {
        'version': 1,
        'disable_existing_loggers': False,
        'filters': {
            'require_debug_false': {
                '()': RequireDebugFalse,
            },
            'require_debug_true': {
                '()': RequireDebugTrue,
            },
            },
        'formatters': {
            'default': {
                'format': '(%(asctime)s; %(filename)s:%(lineno)d)'
                          '%(levelname)s:%(name)s: %(message)s ',
                'datefmt': "%Y-%m-%d %H:%M:%S",
                },
            },
        'handlers': {
            'console': {
                'level': 'DEBUG',
                'filters': ['require_debug_true'],
                'class': 'logging.StreamHandler',
                },
            'logfile': {
                'level': 'INFO',
                'filters': ['require_debug_false'],
                'class': 'logging.handlers.RotatingFileHandler',
                'filename': LOGS_DIR.joinpath(f'{filename}.log'),
                'maxBytes': 1024 * 1024 * 50,  # 50 MB
                'backupCount': 50,
                'formatter': 'default',
                },
            'logfile_debug': {
                'level': 'DEBUG',
                'filters': ['require_debug_true'],
                'class': 'logging.handlers.RotatingFileHandler',
                'filename': LOGS_DIR.joinpath(f'{filename}_debug.log'),
                'maxBytes': 1024 * 1024 * 10,  # 10 MB
                'backupCount': 20,
                'formatter': 'default',
                },
            },
        'loggers': {
            '': {
                'handlers': ['console', 'logfile', 'logfile_debug'],
                'level': "DEBUG",
                },
            'services': {
                'handlers': ['console', 'logfile', 'logfile_debug'],
                'level': "DEBUG",
                'propagate': False,
                },
            }
        }
