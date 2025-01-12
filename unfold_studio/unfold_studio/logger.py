import logging.config
import structlog
import os

import sys

class DebugConsoleHandler(logging.StreamHandler):
    def __init__(self):
        super().__init__(stream = sys.stdout)
    
    def emit(self, record):
        if not record.levelno == logging.DEBUG:
            return
        super().emit(record)

logging.basicConfig(
    stream=sys.stdout,
    level=logging.INFO,
)

LOG_DIR = "../.unfold_studios/logs"
if not os.path.exists(LOG_DIR):
    os.makedirs(LOG_DIR)

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "json_formatter": {
            "()": structlog.stdlib.ProcessorFormatter,
            "processor": structlog.processors.JSONRenderer(),
        },
        "plain_console": {
            "()": structlog.stdlib.ProcessorFormatter,
            "processor": structlog.dev.ConsoleRenderer(),
        },
        "key_value": {
            "()": structlog.stdlib.ProcessorFormatter,
            "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            "datefmt": "%Y-%m-%d %H:%M:%S",
            "processor": structlog.processors.KeyValueRenderer(key_order=['event']),
        },
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "level": "INFO"
        },
        "debug": {
            "class": DebugConsoleHandler,
            "formatter": "key_value"
        },
        "app_logs": {
            "level": "INFO",
            "class": "logging.handlers.TimedRotatingFileHandler",
            "filename": os.path.join(LOG_DIR, 'unfold_studio.log'),
            "when": "midnight",
            "interval": 1,
            "backupCount": 30,
            "formatter": "json_formatter"
        },
        "django_logs": {
            "class": "logging.handlers.TimedRotatingFileHandler",
            "filename": os.path.join(LOG_DIR, 'server.log'),
            "level": "INFO",
            "when": "midnight",
            "interval": 1,
            "backupCount": 30,
            "formatter": "key_value"
        },
        "request_logs": {
            "level": "INFO",
            "class": "logging.handlers.TimedRotatingFileHandler",
            "filename": os.path.join(LOG_DIR, 'requests.log'),
            "when": "midnight",
            "interval": 1,
            "backupCount": 30,
            "formatter": "json_formatter"
        },
        "error_logs": {
            "level": "ERROR",
            "class": "logging.handlers.TimedRotatingFileHandler",
            "filename": os.path.join(LOG_DIR, 'error.log'),
            "when": "midnight",
            "interval": 1,
            "backupCount": 30,
            "formatter": "json_formatter"
        },
    },
    "loggers": {
        "django": {
            "handlers": ["django_logs", "console", "error_logs"],
            "level": "DEBUG",
            "propagate": False
        },
        "django_structlog": {
            "handlers": ["request_logs", "error_logs"],
            "level": "INFO",
            "propagate": False,
        },
        "unfold_studio": {
            "handlers": ["app_logs", "debug", "error_logs"],
            "level": "DEBUG",
            "propagate": False,
        }
    }
}

structlog.configure(
    processors=[
        structlog.contextvars.merge_contextvars,
        structlog.stdlib.filter_by_level,
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.UnicodeDecoder(),
        structlog.stdlib.ProcessorFormatter.wrap_for_formatter,
    ],
    logger_factory=structlog.stdlib.LoggerFactory(),
    wrapper_class=structlog.stdlib.BoundLogger,
    cache_logger_on_first_use=True,
)