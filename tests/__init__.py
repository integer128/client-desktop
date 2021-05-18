# JOK4
from __future__ import annotations

import logging
import os
import sys
import time
from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing import Final

_logger_configured = False


def getLogger(name: str) -> logging.Logger:
    global _logger_configured
    if not _logger_configured:
        class Formatter(logging.Formatter):
            def __init__(self) -> None:
                super().__init__(
                    fmt='%(asctime)s (%(levelname)s) '
                        '%(name)s[%(funcName)s:%(lineno)s]-%(threadName)s: ' # noqa
                        '%(message)s',
                    datefmt=None)

            def formatTime(self, record, datefmt=None) -> str:
                return time.strftime(
                    "%Y-%m-%d %H:%M:%S.{0:03.0f} %z".format(record.msecs),
                    self.converter(record.created))

        handler = logging.StreamHandler(stream=sys.stderr)
        handler.setFormatter(Formatter())

        kwargs = {
            "level": logging.DEBUG,
            "handlers": (handler, )
        }
        logging.basicConfig(**kwargs)
        _logger_configured = True

        # Disable when running from Makefile
        if "MAKELEVEL" in os.environ:
            logging.disable()

    return logging.getLogger(name)


TEST_DATA_PATH: Final = Path(__file__).parent.resolve() / "data"
