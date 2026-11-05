"""
UALink 2.0 — Common Logger
"""
import logging
import sys

log = logging.getLogger("UALink2")
if not log.handlers:
    log.setLevel(logging.DEBUG)
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s"))
    log.addHandler(handler)
