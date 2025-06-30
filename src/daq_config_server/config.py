from typing import Literal

from pydantic import AnyUrl, BaseModel

LogLevel = Literal["NOTSET", "DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]


class GraylogConfig(BaseModel):
    enabled: bool = False
    level: LogLevel = "INFO"
    url: AnyUrl = AnyUrl("tcp://localhost:5555")


class StreamLogConfig(BaseModel):
    enabled: bool = True
    level: LogLevel = "DEBUG"


class LoggingConfig(BaseModel):
    graylog: GraylogConfig = GraylogConfig()
    stream_log: StreamLogConfig = StreamLogConfig()


class Config(BaseModel):
    logging_config: LoggingConfig = LoggingConfig()
