# maintenance.py
from logs import logger

MAINT = {"active": False, "reason": ""}

def enable(reason=""):
    MAINT["active"] = True
    MAINT["reason"] = reason
    logger.info("Maintenance enabled: %s", reason)

def disable():
    MAINT["active"] = False
    MAINT["reason"] = ""
    logger.info("Maintenance disabled")

def is_active():
    return MAINT["active"]