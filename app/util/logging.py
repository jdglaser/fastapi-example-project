import logging

from app.config import settings


class CustomFormatter(logging.Formatter):
    """Logging Formatter to add colors and count warning / errors"""

    grey = "\x1b[38;21m"
    yellow = "\x1b[33;21m"
    red = "\x1b[31;21m"
    green = "\x1b[0;32m"
    bold_red = "\x1b[31;1m"
    reset = "\x1b[0m"
    format = "%(levelname)s" + reset + ":     %(asctime)s: %(message)s (%(name)s:%(lineno)d)"

    FORMATS = {
        logging.DEBUG: grey + format + reset,
        logging.INFO: green + format + reset,
        logging.WARNING: yellow + format + reset,
        logging.ERROR: red + format + reset,
        logging.CRITICAL: bold_red + format + reset
    }

    def format(self, record):
        log_fmt = self.FORMATS.get(record.levelno)
        formatter = logging.Formatter(log_fmt)
        return formatter.format(record)

def get_logger(name):
    logger = logging.getLogger(name)
    logger.setLevel(settings.log_level)
    # create console handler with a higher log level
    ch = logging.StreamHandler()
    ch.setLevel(settings.log_level)
    ch.setFormatter(CustomFormatter())
    logger.addHandler(ch)
    return logger
