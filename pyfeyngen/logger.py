import logging
logger = logging.getLogger('pyfeyngen')
def setup_logging(debug=False):
    level = logging.DEBUG if debug else logging.INFO
    if not logger.hasHandlers():
        handler = logging.StreamHandler()
        formatter = logging.Formatter('%(levelname)s - %(name)s - %(message)s')
        handler.setFormatter(formatter)
        logger.addHandler(handler)
    logger.setLevel(level)
    if debug:
        logger.debug("DEBUG mode enabled")