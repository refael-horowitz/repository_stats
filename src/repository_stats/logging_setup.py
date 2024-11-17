import logging
import logging.config
from enum import Enum
from pathlib import Path

from yaml import safe_load


class LogLevel(Enum):
    """ Represents the different logging levels. """
    CRITICAL = 'CRITICAL'
    ERROR = 'ERROR'
    WARNING = 'WARNING'
    INFO = 'INFO'
    DEBUG = 'DEBUG'
    NOTSET = 'NOTSET'


def setup_logging(logging_yaml: Path, debug_mode: bool = False, log_to_file: bool = False) -> None:
    """ Configure the loggers with the logging config when using the project as main.

    :param Path logging_yaml: Path to the logging config file.
    :param str debug_mode: Indicates whether to enable debug mode (`DEBUG` logging level),
                       otherwise `INFO` logging level is applied.
    :param bool log_to_file: Indicates whether to enable logging to a file.
    """
    config = safe_load(logging_yaml.read_text())
    if debug_mode:
        _update_logger_level(config, LogLevel.DEBUG.value)
    if log_to_file:
        _update_logger_file_handler(config)
    logging.config.dictConfig(config)


def _update_logger_level(logger_config: dict, log_level: str) -> None:
    logger_config['loggers']['repository_stats']['level'] = log_level
    logger_config['root']['level'] = log_level


def _update_logger_file_handler(logger_config: dict) -> None:
    logger_config['loggers']['repository_stats']['handlers'] = ['file']
    logger_config['root']['handlers'] = ['file']
