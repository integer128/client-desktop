# JOK+
from __future__ import annotations

from PySide2.QtCore import Qt, QLocale, QMetaObject, QObject, Slot as QSlot
from PySide2.QtGui import QIcon, QGuiApplication

from bmnclient.signal_handler import SignalHandler
from bmnclient import version, resources
from bmnclient.logger import getClassLogger
from bmnclient.config import UserConfig


class CoreApplication(QObject):
    _instance = None

    def __init__(self, qt_class, argv) -> None:
        assert self.__class__._instance is None

        CoreApplication._instance = self
        self._logger = getClassLogger(__name__, self.__class__)
        self._title = "{} {}".format(version.NAME, version.VERSION_STRING)
        self._icon = None
        self._language = None
        self._quit_code = 0
        self._on_quit_called = False

        self._user_config = UserConfig()
        self._user_config.load()

        # Prepare QApplication
        QLocale.setDefault(QLocale.c())

        qt_class.setAttribute(Qt.AA_EnableHighDpiScaling)
        qt_class.setAttribute(Qt.AA_UseHighDpiPixmaps)
        qt_class.setAttribute(Qt.AA_DisableShaderDiskCache)
        qt_class.setAttribute(Qt.AA_DisableWindowContextHelpButton)

        qt_class.setApplicationName(version.NAME)
        qt_class.setApplicationVersion(version.VERSION_STRING)
        qt_class.setOrganizationName(version.MAINTAINER)
        qt_class.setOrganizationDomain(version.MAINTAINER_DOMAIN)

        # QApplication
        self._qt_application = qt_class(argv)
        super().__init__()

        if issubclass(qt_class, QGuiApplication):
            self._icon = QIcon(str(resources.ICON_FILE_PATH))
            qt_class.setWindowIcon(self._icon)

        # We recommend that you connect clean-up code to the aboutToQuit()
        # signal, instead of putting it in your application's main() function
        # because on some platforms the exec() call may not return.
        self._qt_application.aboutToQuit.connect(
            self.__onAboutToQuit,
            Qt.DirectConnection)

        # SignalHandler
        self._signal_handler = SignalHandler(self)
        self._signal_handler.SIGINT.connect(
            self.setQuitEvent,
            Qt.QueuedConnection)
        self._signal_handler.SIGQUIT.connect(
            self.setQuitEvent,
            Qt.QueuedConnection)
        self._signal_handler.SIGTERM.connect(
            self.setQuitEvent,
            Qt.QueuedConnection)

    def run(self) -> int:
        QMetaObject.invokeMethod(self, "_onRunPrivate", Qt.QueuedConnection)

        assert not self._on_quit_called
        self._quit_code = self._qt_application.exec_()
        assert self._on_quit_called

        if self._quit_code == 0:
            self._logger.info(
                "%s terminated successfully.",
                version.NAME)
        else:
            self._logger.warning(
                "%s terminated with error.",
                version.NAME)
        return self._quit_code

    def setQuitEvent(self, code: int = 0) -> None:
        self._qt_application.exit(code)

    @classmethod
    def instance(cls) -> CoreApplication:
        return cls._instance

    @property
    def quitCode(self) -> int:
        return self._quit_code

    @property
    def userConfig(self) -> UserConfig:
        return self._user_config

    @property
    def title(self) -> str:
        return self._title

    @property
    def icon(self) -> QIcon:
        return self._icon

    @QSlot()
    def _onRunPrivate(self) -> None:
        self._onRun()

    def _onRun(self) -> None:
        pass

    def __onAboutToQuit(self) -> None:
        self._logger.debug("Shutting down...");
        # for w in QGuiApplication.topLevelWindows():
        #     w.close()
        self._onQuit()

    def _onQuit(self) -> None:
        assert not self._on_quit_called
        self._on_quit_called = True
        self._signal_handler.close()
