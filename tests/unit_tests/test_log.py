import logging
from unittest.mock import MagicMock, patch

import pytest

from daq_config_server.config import GraylogConfig
from daq_config_server.log import LoggingConfig, set_up_logging


@pytest.fixture
def mock_graylog_emit():
    with patch("daq_config_server.log.GELFTCPHandler.emit") as graylog_emit:
        yield graylog_emit


def test_default_logger_does_not_emit_to_graylog(mock_graylog_emit: MagicMock):
    logger = logging.getLogger()
    mock_graylog_emit.assert_not_called()
    logger.info("FOO")
    mock_graylog_emit.assert_not_called()


def test_graylog_logger_does_emit_to_graylog(mock_graylog_emit: MagicMock):
    set_up_logging(LoggingConfig(graylog=GraylogConfig(enabled=True)))
    logger = logging.getLogger()
    mock_graylog_emit.assert_not_called()
    logger.info("FOO")
    mock_graylog_emit.assert_called_once()
