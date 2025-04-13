import logging
import logging.config

from starlette.config import Config

config = Config(".env")

DATABASE_URL = config("DATABASE_URL")
LOG_LEVEL = config("LOG_LEVEL", default="INFO")
APP_NAME = config("APP_NAME", default="gym-management")


logging.config.dictConfig(
    {
        "version": 1,
        "formatters": {
            "debugger": {
                "format": "%(levelname)s::%(module)s::%(lineno)d::%(message)s",
            }
        },
        "handlers": {
            "debugger": {
                "class": "logging.StreamHandler",
                "formatter": "debugger",
                "level": LOG_LEVEL,
                "stream": "ext://sys.stdout",
            }
        },
        "loggers": {APP_NAME: {"handlers": ["debugger"], "level": LOG_LEVEL}},
    }
)
