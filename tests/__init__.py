# JOK4
from __future__ import annotations

import logging
import os
import sys
import time
from pathlib import Path
from typing import TYPE_CHECKING

from PySide2.QtWidgets import QApplication

from bmnclient.application import CommandLine, CoreApplication
from bmnclient.utils.class_property import classproperty

if TYPE_CHECKING:
    from typing import Final


class TestApplication(CoreApplication):
    _DATA_PATH: Final = Path(__file__).parent.resolve() / "data"
    _logger_configured = False

    def __init__(self) -> None:
        command_line = CommandLine(["unittest"])
        super().__init__(
            qt_class=QApplication,
            command_line=command_line,
            model_factory=None)

    @classproperty
    def dataPath(cls) -> Path:  # noqa
        return cls._DATA_PATH

    @staticmethod
    def getLogger(name: str) -> logging.Logger:
        return logging.getLogger(name)

    @classmethod
    def configureLogger(cls) -> None:
        if cls._logger_configured:
            return

        class Formatter(logging.Formatter):
            def __init__(self) -> None:
                super().__init__(
                    fmt="%(asctime)s (%(levelname)s) %(thread)016x "
                        "%(name)s[%(funcName)s:%(lineno)s]: " # noqa
                        "%(message)s",
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

        # Disable when running from Makefile
        if "MAKELEVEL" in os.environ:
            logging.disable()

        cls._logger_configured = True


TestApplication.configureLogger()
