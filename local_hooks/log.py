import logging
import sys
from typing import Any


class ANSIColor:
    def __init__(self, color_enabled: bool) -> None:
        self._color_enabled: bool = color_enabled
        self._colors: dict[str, str] = {
            "RESET": "\033[0m",
            "DIM": "\033[2m",
            "RED": "\033[31m",
            "BOLD_RED": "\033[1;31m",
            "BOLD_UNDERLINE_RED": "\033[1;4;31m",
            "GREEN": "\033[32m",
            "YELLOW": "\033[33m",
            "BLUE": "\033[34m",
            "MAGENTA": "\033[35m",
        }

    def __getattr__(self, name: str) -> str:
        if name in self._colors:
            return self._get_color(name)
        else:
            raise AttributeError

    def _get_color(self, name: str) -> str:
        if not self._color_enabled:
            return ""
        return self._colors[name]


class ColorFilter(logging.Filter):
    def __init__(self, *args: Any, color: bool = True, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self.ansi_colors = ANSIColor(color)

        self.level_colors = {
            logging.DEBUG: self.ansi_colors.DIM,
            logging.INFO: self.ansi_colors.RESET,
            logging.WARNING: self.ansi_colors.YELLOW,
            logging.ERROR: self.ansi_colors.BOLD_RED,
            logging.CRITICAL: self.ansi_colors.BOLD_UNDERLINE_RED,
            logging.NOTSET: self.ansi_colors.BOLD_UNDERLINE_RED,
        }

    def filter(self, record: logging.LogRecord) -> bool:
        record.color = self.level_colors.get(record.levelno, "")
        record.reset = self.ansi_colors.RESET
        return True


def add_stream_handler(logger: logging.Logger, debug: bool = False, color: bool = True) -> None:
    """
    Adds a stream handler to the logger passed in to this function.

    The stream handler is constructed based on the other arguments.
    """

    # Use a plain formatter for console
    console_format = "{color}{message}{reset}" if color else "{levelname:8} - {message}"
    console_formatter = logging.Formatter(fmt=console_format, style="{")

    # INFO and lower should log to stdout
    stdout = logging.StreamHandler(sys.stdout)
    stdout.setLevel(logging.DEBUG if debug else logging.INFO)
    stdout.setFormatter(console_formatter)
    stdout.addFilter(lambda record: record.levelno <= logging.INFO)
    stdout.addFilter(ColorFilter(color=color))
    logger.addHandler(stdout)

    # WARNING and higher should log to stderr
    stderr = logging.StreamHandler(sys.stderr)
    stderr.setLevel(logging.WARNING)
    stderr.setFormatter(console_formatter)
    stderr.addFilter(ColorFilter(color=color))
    logger.addHandler(stderr)


_configured = False


def configure_logger(debug: bool = False, color: bool = True) -> logging.Logger:
    global _configured
    logger = logging.getLogger()

    if _configured:
        return logger

    _configured = True
    add_stream_handler(logger, debug=debug, color=color)
    return logger


logger = configure_logger()

__all__ = ["logger"]
