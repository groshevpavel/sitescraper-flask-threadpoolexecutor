import logging.config


LOGGER_NAME = 'timeweb-scraper'
LOG_LEVEL = 'DEBUG'

LOGGING_CONFIG = {
    'version': 1,

    'formatters': {
        'default': {
            'format': '%(levelname)s::%(asctime)s:%(name)s.%(funcName)s\n%(message)s\n',
            'datefmt': '%Y-%m-%d %H:%M:%S',
        },
    },
    'handlers': {
        'console': {
            'level': LOG_LEVEL,
            'class': 'logging.StreamHandler',
            'formatter': 'default',
            'stream': 'ext://sys.stdout',
        },
    },
    'loggers': {
        LOGGER_NAME: {
            'level': LOG_LEVEL,
            'handlers': (['console']),
        },
    },
    'disable_existing_loggers': False,
}


def init_logging():
    logging.config.dictConfig(LOGGING_CONFIG)


def get_logger():
    return logging.getLogger(LOGGER_NAME)
