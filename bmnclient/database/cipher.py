from __future__ import annotations

import base64
import enum
import logging
import struct
from typing import TYPE_CHECKING

from ..key_store import KeyIndex

if TYPE_CHECKING:
    from typing import Any
    from ..application import CoreApplication

log = logging.getLogger(__name__)


class Type(enum.IntEnum):
    TypeText = 1
    TypeBytes = 2
    TypeInt = 3
    TypeBool = 4
    TypeReal = 5


class Cipher:
    def __init__(self, application: CoreApplication) -> None:
        self._cipher = application.keyStore.deriveCipher(
            KeyIndex.WALLET_DATABASE)

    def text_from(self, value: bytes) -> str:
        return value.decode()

    def _decrypt(self, value: bytes) -> Any:
        try:
            if not value:
                return ""
            # leave it for a while
            if value[0] == 76:
                val = self._cipher.decrypt(None, base64.b64decode(value)[1:])
            elif value[0] == 75:
                val = self._cipher.decrypt(None, base64.b64decode(value)[1:])
            else:
                return int(value)
            pref = val[0]
            if Type.TypeText == pref:
                return val[1:].decode()
            if Type.TypeBytes == pref:
                return val[1:]
            if Type.TypeBool == pref:
                return struct.unpack("?", val[1:])[0]
            if Type.TypeInt == pref:
                return struct.unpack("q", val[1:])[0]
            if Type.TypeReal == pref:
                return struct.unpack("d", val[1:])[0]
            raise RuntimeError(f"not implemented type {val}")
        except RuntimeError as re:
            log.fatal(f"{re} +> {value}")
        except Exception as te:
            log.fatal(f"{te} ++> {value}")

    def _encrypt(self, value: Any, type_: Type, strong: bool) -> str:
        try:
            if strong:
                return base64.b64encode(
                    b'+' +
                    self._cipher.encrypt(None, bytes([type_]) + value)).decode()
            else:
                return base64.b64encode(
                    b'-' +
                    self._cipher.encrypt(None, bytes([type_]) + value)).decode()
        except RuntimeError as re:
            log.fatal(f"{re} +> {value}")
        except Exception as te:
            log.fatal(f"{te} ++> {value}")
#

    def encrypt(self, value: Any, strong: bool) -> str:
        if value is None:
            return ""
        return value

    def make_hash(self, value: str) -> str:
        return self._cipher.encrypt(None, value.encode("utf-8")).hex()
