# JOK++
from __future__ import annotations

from enum import Enum
from typing import Final, Optional

from .address import AbstractAddress
from .coin import AbstractCoin
from ..crypto.base58 import Base58
from ..crypto.bech32 import Bech32
from ..crypto.digest import Ripemd160Digest, Sha256Digest


class BitcoinAddress(AbstractAddress):
    _PUBKEY_HASH_PREFIX_LIST = ("1",)
    _SCRIPT_HASH_PREFIX_LIST = ("3",)
    _HRP = "bc"

    class Type(Enum):
        # Optional[Tuple(version, excepted_size, friendly_name)]
        UNKNOWN: Final = (0xff, 0, "unknown")
        PUBKEY_HASH: Final = (0x00, Ripemd160Digest.SIZE, "p2pkh")
        SCRIPT_HASH: Final = (0x05, Ripemd160Digest.SIZE, "p2sh")
        WITNESS_V0_KEY_HASH: Final = (0x00, Ripemd160Digest.SIZE, "p2wpkh")
        WITNESS_V0_SCRIPT_HASH: Final = (0x00, Sha256Digest.SIZE, "p2wsh")
        WITNESS_UNKNOWN: Final = (0x00, -40, "witness_unknown")

    def __init__(self, type_: Type, version, data) -> None:
        super().__init__(data)
        self._type = type_
        self._version = version

    @property
    def type(self) -> Type:
        return self._type

    @property
    def version(self) -> int:
        return self._version

    @classmethod
    def decode(cls, source: str) -> Optional[BitcoinAddress]:
        if len(source) <= len(cls._HRP) + 1:
            return None

        if source[0] in cls._PUBKEY_HASH_PREFIX_LIST:
            return cls._decode(cls.Type.PUBKEY_HASH, source)
        if source[0] in cls._SCRIPT_HASH_PREFIX_LIST:
            return cls._decode(cls.Type.SCRIPT_HASH, source)

        if source[len(cls._HRP)] != Bech32.SEPARATOR:
            return None

        if len(source) == len(cls._HRP) + 1 + 39:
            return cls._decode(cls.Type.WITNESS_V0_KEY_HASH, source)
        if len(source) == len(cls._HRP) + 1 + 59:
            return cls._decode(cls.Type.WITNESS_V0_SCRIPT_HASH, source)

        return cls._decode(cls.Type.WITNESS_UNKNOWN, source)

    @classmethod
    def _decode(cls, type_: Type, source: str) -> Optional[BitcoinAddress]:
        if not type_.value:
            return None

        if type_ in (
                cls.Type.PUBKEY_HASH,
                cls.Type.SCRIPT_HASH
        ):
            data = Base58.decode(source, True)
            if not data or data[0] != type_.value[0]:
                return None
            version = type_.value[0]
            data = data[1:]
        elif type_ in (
                cls.Type.WITNESS_V0_KEY_HASH,
                cls.Type.WITNESS_V0_SCRIPT_HASH
        ):
            hrp, version, data = Bech32.decode(source)
            if hrp != cls._HRP or version != type_.value[0]:
                return None
        elif type_ == cls.Type.WITNESS_UNKNOWN:
            hrp, version, data = Bech32.decode(source)
            if hrp != cls._HRP:
                return None
            for t in (
                    cls.Type.WITNESS_V0_KEY_HASH,
                    cls.Type.WITNESS_V0_SCRIPT_HASH
            ):
                if version == t.value[0]:
                    return None
        else:
            return None

        if type_.value[1] > 0:
            if type_.value[1] != len(data):
                return None
        elif type_.value[1] < 0:
            if len(data) <= 0 or len(data) > abs(type_.value[1]):
                return None

        return cls(type_, version, data)


class Bitcoin(AbstractCoin):
    _SHORT_NAME = "btc"
    _FULL_NAME = "Bitcoin"

    class _Currency(AbstractCoin._Currency):
        _DECIMAL_SIZE = (0, 8)
        _UNIT = "BTC"

    class _Address(BitcoinAddress):
        pass


class BitcoinTestAddress(BitcoinAddress):
    _PUBKEY_HASH_PREFIX_LIST = ("m", "n")
    _SCRIPT_HASH_PREFIX_LIST = ("2",)
    _HRP = "tb"

    class Type(Enum):
        UNKNOWN: Final = \
            BitcoinAddress.Type.UNKNOWN
        PUBKEY_HASH: Final = \
            (0x6f, ) + BitcoinAddress.Type.PUBKEY_HASH.value[1:]
        SCRIPT_HASH: Final = \
            (0xc4, ) + BitcoinAddress.Type.SCRIPT_HASH.value[1:]
        WITNESS_V0_KEY_HASH: Final = \
            BitcoinAddress.Type.WITNESS_V0_KEY_HASH.value
        WITNESS_V0_SCRIPT_HASH: Final = \
            BitcoinAddress.Type.WITNESS_V0_SCRIPT_HASH.value
        WITNESS_UNKNOWN: Final = \
            BitcoinAddress.Type.WITNESS_UNKNOWN.value


class BitcoinTest(Bitcoin):
    _SHORT_NAME = "btctest"
    _FULL_NAME = "Bitcoin Testnet"

    class _Address(BitcoinTestAddress):
        pass
