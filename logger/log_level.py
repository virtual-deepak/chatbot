from enum import Enum
import global_settings
import logging

class LogLevel(Enum):
    """
    This enum specifies the log levels
    """
    CRITICAL = 0,
    ERROR = 1,
    WARNING = 2
    INFO = 3,
    DEBUG = 4


def get_log_level():
    """
    This function sets the log level
    :return: None
    """
    if global_settings.LOG_LEVEL.upper() == LogLevel.CRITICAL.name:
        return logging.CRITICAL
    elif global_settings.LOG_LEVEL.upper() == LogLevel.ERROR.name:
        return logging.ERROR
    elif global_settings.LOG_LEVEL.upper() == LogLevel.WARNING.name:
        return logging.WARNING
    elif global_settings.LOG_LEVEL.upper() == LogLevel.INFO.name:
        return logging.INFO
    else:
        return logging.DEBUG