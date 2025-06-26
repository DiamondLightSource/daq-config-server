import logging
from typing import Literal, TextIO

from graypy import GELFTCPHandler
from pydantic import BaseModel, HttpUrl

LogLevel = Literal["NOTSET", "DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]


class GraylogConfig(BaseModel):
    enabled: bool = False
    url: HttpUrl = HttpUrl("http://localhost:5555")


class LoggingConfig(BaseModel):
    level: LogLevel = "INFO"
    graylog: GraylogConfig = GraylogConfig()


def set_up_stream_handler(
    logger: logging.Logger, logging_config: LoggingConfig
) -> logging.StreamHandler[TextIO]:
    """Creates and configures StreamHandler, then attaches to logger.

    Args:
        logger: Logger to attach handler to
        logging_config: LoggingConfig
    """
    stream_handler = logging.StreamHandler()
    stream_handler.setLevel(logging_config.level)

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
    graylog_handler.setLevel(logging_config.level)

    logger.addHandler(graylog_handler)
    return graylog_handler


def set_up_logging(logging_config: LoggingConfig) -> None:
    """Configure root level logger for the config-server.

    Configures root logger. Any other logger will propogate to this logger assuming the
    default `logger.propagate` is True.

    Args:
        logging_config: LoggingConfig
    """

    logger = logging.getLogger()

    logger.setLevel(logging_config.level)

    set_up_stream_handler(logger, logging_config)

    if logging_config.graylog.enabled:
        set_up_graylog_handler(logger, logging_config)
