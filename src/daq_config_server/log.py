import logging
from typing import TextIO

from graypy import GELFTCPHandler

from daq_config_server.config import LoggingConfig


def set_up_stream_handler(
    logger: logging.Logger, logging_config: LoggingConfig
) -> logging.StreamHandler[TextIO]:
    """Creates and configures StreamHandler, then attaches to logger.

    Args:
        logger: Logger to attach handler to
        logging_config: LoggingConfig
    """
    stream_handler = logging.StreamHandler()
    stream_handler.setLevel(logging_config.stream_log.level)

    logger.addHandler(stream_handler)
    return stream_handler


def set_up_graylog_handler(
    logger: logging.Logger, logging_config: LoggingConfig
) -> GELFTCPHandler:
    """Creates and configures GELFTCPHandler, then attaches to logger.

    Args:
        logger: Logger to attach handler to
        logging_config: LoggingConfig
    """
    assert logging_config.graylog.url.host is not None, "Graylog URL missing host"
    assert logging_config.graylog.url.port is not None, "Graylog URL missing port"
    graylog_handler = GELFTCPHandler(
        logging_config.graylog.url.host,
        logging_config.graylog.url.port,
    )
    graylog_handler.setLevel(logging_config.graylog.level)

    prefix_formatter = logging.Formatter(
        "[CONFIG-SERVER] %(asctime)s - %(levelname)s - %(message)s"
    )

    graylog_handler.setFormatter(prefix_formatter)

    logger.addHandler(graylog_handler)
    return graylog_handler


def set_up_logging(logging_config: LoggingConfig) -> None:
    """Configure root level logger for the config-server.

    Configures root logger. Any other logger will propogate to this logger

    Args:
        logging_config: LoggingConfig
    """

    logger = logging.getLogger()
    logger.setLevel("DEBUG")

    if logging_config.stream_log.enabled:
        set_up_stream_handler(logger, logging_config)

    if logging_config.graylog.enabled:
        set_up_graylog_handler(logger, logging_config)
