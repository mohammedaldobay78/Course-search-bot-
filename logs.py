# logs.py
import logging
from logging.handlers import RotatingFileHandler
from config import LOG_FILE

logger = logging.getLogger("course_bot")
logger.setLevel(logging.INFO)
if not logger.handlers:
    handler = RotatingFileHandler(LOG_FILE, maxBytes=2*1024*1024, backupCount=3)
    fmt = "%(asctime)s - %(levelname)s - %(message)s"
    handler.setFormatter(logging.Formatter(fmt))
    logger.addHandler(handler)