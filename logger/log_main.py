import logging
import sys

from logger.log_level import get_log_level


def get_logger():
    logger = logging.getLogger('chatbot_logger')
    if len(logger.handlers) > 0:
        return logger
    logging.raiseExceptions = False
    formatter = logging.Formatter(
        "%(levelname)s:     %(asctime)s     module:%(module)s     line_no:%(lineno)d     %(message)s",
        '%Y-%m-%dT%H:%M:%S%z')

    logger.setLevel(get_log_level())
    logger.propagate = True

    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)

    logger.addHandler(console_handler)
        
    return logger