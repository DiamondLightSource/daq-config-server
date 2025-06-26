import logging


# See https://github.com/DiamondLightSource/daq-config-server/issues/73
# for making the logging configurable
def get_default_logger(name: str = __name__) -> logging.Logger:
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)

    # Prevent adding handlers multiple times
    if not logger.handlers:
        console_handler = logging.StreamHandler()
        formatter = logging.Formatter(
            "%(asctime)s - %(levelname)s - %(message)s", datefmt="%Y-%m-%d %H:%M:%S"
        )
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)

    return logger


# For now use a basic console-writing logger. Integrate properly with kubernetes in the
# future
LOGGER = get_default_logger("daq-config-server")
