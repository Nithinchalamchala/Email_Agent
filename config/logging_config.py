import logging
from config.settings import settings

def setup_logger(name: str) -> logging.Logger:
    """
    Sets up and returns a logger with the configured log level.
    """
    logger = logging.getLogger(name)
    if not logger.handlers:
        logger.setLevel(settings.LOG_LEVEL)
        ch = logging.StreamHandler()
        formatter = logging.Formatter("[%(asctime)s] [%(levelname)s] %(name)s: %(message)s")
        ch.setFormatter(formatter)
        logger.addHandler(ch)
    return logger
