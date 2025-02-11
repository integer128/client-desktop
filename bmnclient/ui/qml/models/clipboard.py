from __future__ import annotations

from typing import TYPE_CHECKING

from PySide6.QtCore import \
    Property as QProperty, \
    QObject, \
    Signal as QSignal
from PySide6.QtGui import QClipboard

if TYPE_CHECKING:
    from .. import QmlApplication


class ClipboardModel(QObject):
    _MODE = QClipboard.Clipboard
    stateChanged = QSignal()

    def __init__(self, application: QmlApplication) -> None:
        super().__init__()
        self._application = application
        # noinspection PyUnresolvedReferences
        self._application.clipboard.changed.connect(self._onChanged)

    @QProperty(str, notify=stateChanged)
    def text(self) -> str:
        return self._application.clipboard.text("plain", self._MODE)

    @text.setter
    def text(self, value: str):
        self._application.clipboard.setText(value, self._MODE)

    def _onChanged(self, mode: QClipboard.Mode):
        if mode == self._MODE:
            # noinspection PyUnresolvedReferences
            self.stateChanged.emit()
