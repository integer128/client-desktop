# JOK4
from __future__ import annotations

from enum import auto, Enum
from typing import TYPE_CHECKING

from ...crypto.secp256k1 import PrivateKey, PublicKey
from ...utils import filterNotNone
from ...utils.meta import classproperty
from ...utils.serialize import Serializable, serializable
from ...wallet.hd import HdNode

if TYPE_CHECKING:
    from typing import Any, List, Optional, Tuple
    from .coin import AbstractCoin


class _AbstractAddressTypeValue:
    __slots__ = ("_name", "_version", "_size", "_encoding")

    def __init__(
            self,
            *,
            name: str,
            version: int,
            size: int,
            encoding: AbstractCoin.Address.Encoding) -> None:
        self._name = name
        self._version = version
        self._size = size
        self._encoding = encoding

    def __eq__(self, other: _AbstractAddressTypeValue) -> bool:
        return (
                isinstance(other, self.__class__)
                and self._name == other._name
                and self._version == other._version
                and self._size == other._size
                and self._encoding == other._encoding
        )

    def __hash__(self) -> int:
        return hash((
            self._name,
            self._version,
            self._size,
            self._encoding))

    @property
    def name(self) -> str:
        return self._name

    @property
    def version(self) -> int:
        return self._version

    @property
    def size(self) -> int:
        return self._size

    @property
    def encoding(self) -> AbstractCoin.Address.Encoding:
        return self._encoding


class AbstractAddress(Serializable):
    _NULLDATA_NAME = "NULL_DATA"
    _HRP = "hrp"

    class Interface:
        def __init__(
                self,
                *args,
                address: AbstractCoin.Address,
                **kwargs) -> None:
            super().__init__(*args, **kwargs)
            self._address = address

        def afterSetAmount(self) -> None:
            raise NotImplementedError

        def afterSetLabel(self) -> None:
            raise NotImplementedError

        def afterSetComment(self) -> None:
            raise NotImplementedError

        def afterSetTxCount(self) -> None:
            raise NotImplementedError

        def beforeAppendTx(self, tx: AbstractCoin.Tx) -> None:
            raise NotImplementedError

        def afterAppendTx(self, tx: AbstractCoin.Tx) -> None:
            raise NotImplementedError

        def afterSetUtxoList(self) -> None:
            raise NotImplementedError

        def afterSetHistoryFirstOffset(self) -> None:
            raise NotImplementedError

        def afterSetHistoryLastOffset(self) -> None:
            raise NotImplementedError

    class Encoding(Enum):
        NONE = auto()
        BASE58 = auto()
        BECH32 = auto()

    class TypeValue(_AbstractAddressTypeValue):
        pass

    class Type(Enum):
        pass

    def __init__(
            self,
            coin: AbstractCoin,
            *,
            name: Optional[str],
            type_: AbstractCoin.Address.Type,
            data: bytes = b"",
            key: Optional[HdNode, PrivateKey, PublicKey] = None,
            amount: int = 0,
            tx_count: int = 0,
            label: str = "",
            comment: str = "",
            tx_list: Optional[List[AbstractCoin.Tx]] = None,
            utxo_list: Optional[List[AbstractCoin.Tx.Utxo]] = None,
            history_first_offset: str = "",
            history_last_offset: str = "") -> None:
        super().__init__()

        self._coin = coin
        self._name = name or self._NULLDATA_NAME
        self._type = type_
        self._data = data
        self._key = key
        self._amount = amount
        self._label = label
        self._comment = comment
        self._tx_count = tx_count  # not linked with self._tx_list

        self._tx_list: List[AbstractCoin.Tx] = \
            [] if tx_list is None else list(filterNotNone(tx_list))
        self._utxo_list: List[AbstractCoin.Tx.Utxo] = \
            [] if tx_list is None else list(filterNotNone(utxo_list))

        if history_first_offset and history_last_offset:
            self._history_first_offset = history_first_offset
            self._history_last_offset = history_last_offset
        else:
            self._history_first_offset = ""
            self._history_last_offset = ""

        self._model: Optional[AbstractCoin.Address.Interface] = \
            self._coin.model_factory(self)

    def __eq__(self, other: AbstractCoin.Address) -> bool:
        return (
                isinstance(other, self.__class__)
                and self._coin == other.coin
                and self._name == other.name
                and self._type == other._type
        )

    def __hash__(self) -> int:
        return hash((
            self.coin,
            self._name,
            self._type
        ))

    @classmethod
    def deserialize(cls, *args, **kwargs) -> Optional[AbstractCoin.Address]:
        return super().deserialize(
            *args,
            deserialize_create=cls.decode,
            **kwargs)

    @classmethod
    def _deserializeProperty(
            cls,
            args: Tuple[Any],
            key: str,
            value: Any) -> Any:
        if isinstance(value, str) and key == "key":
            return cls.importPrivateKey(value)
        if isinstance(value, dict) and key == "tx_list":
            coin: AbstractCoin = args[0]
            return coin.Tx.deserialize(coin, **value)
        if isinstance(value, dict) and key == "utxo_list":
            coin: AbstractCoin = args[0]
            return coin.Tx.Utxo.deserialize(coin, **value)
        return super()._deserializeProperty(args, key, value)

    def _serializeProperty(self, key: str, value: Any) -> Any:
        if key == "key":
            return self.exportPrivateKey()
        return super()._serializeProperty(key, value)

    @classproperty
    def hrp(cls) -> str:  # noqa
        return cls._HRP

    @property
    def model(self) -> Optional[AbstractCoin.Address.Interface]:
        return self._model

    @property
    def coin(self) -> AbstractCoin:
        return self._coin

    @serializable
    @property
    def name(self) -> str:
        return self._name

    @property
    def type(self) -> AbstractCoin.Address.Type:
        return self._type

    @classmethod
    def decode(
            cls,
            coin: AbstractCoin,
            **kwargs) -> Optional[AbstractCoin.Address]:
        raise NotImplementedError

    @classmethod
    def createNullData(
            cls,
            coin: AbstractCoin,
            **kwargs) -> AbstractCoin.Address:
        raise NotImplementedError

    @property
    def isNullData(self) -> bool:
        raise NotImplementedError

    @property
    def data(self) -> bytes:
        return self._data

    @property
    def publicKey(self) -> Optional[PublicKey]:
        if isinstance(self._key, HdNode):
            value = self._key.publicKey
        elif isinstance(self._key, PrivateKey):
            value = self._key.publicKey
        elif isinstance(self._key, PublicKey):
            value = self._key
        else:
            value = None
        return value

    @property
    def privateKey(self) -> Optional[PrivateKey]:
        if isinstance(self._key, HdNode):
            value = self._key.privateKey
        elif isinstance(self._key, PrivateKey):
            value = self._key
        else:
            value = None
        return value

    @serializable
    @property
    def key(self) -> Optional[HdNode, PrivateKey, PublicKey]:
        return self._key

    def exportPrivateKey(self) -> str:
        if isinstance(self._private_key, HdNode):
            value = self._private_key.extended_key
        elif isinstance(self._private_key, PrivateKey):
            value = self._private_key.to_wif
        else:
            value = ""
        return value

    @classmethod
    def importPrivateKey(cls, value: str) -> Optional[HdNode, PrivateKey]:
        if value:
            try:
                return HDNode.from_extended_key(value)
            except HDError:
                return PrivateKey.from_wif(value)
        return None

    @property
    def hdIndex(self) -> int:
        if isinstance(self._key, HdNode):
            index = self._key.index
            if index >= 0:
                return index
        return -1

    @serializable
    @property
    def amount(self) -> int:
        return self._amount

    @amount.setter
    def amount(self, value: int) -> None:
        if self._amount != value:
            self._amount = value
            if self._model:
                self._model.afterSetAmount()
            self._coin.refreshAmount()

    @serializable
    @property
    def label(self) -> str:
        return self._label

    @label.setter
    def label(self, value: str) -> None:
        if self._label != value:
            self._label = value
            if self._model:
                self._model.afterSetLabel()

    @serializable
    @property
    def comment(self) -> str:
        return self._comment

    @comment.setter
    def comment(self, value: str) -> None:
        if self._comment != value:
            self._comment = value
            if self._model:
                self._model.afterSetComment()

    @property
    def isReadOnly(self) -> bool:
        return self.privateKey is None

    @serializable
    @property
    def txCount(self) -> int:
        return self._tx_count

    @txCount.setter
    def txCount(self, value: int) -> None:
        if self._tx_count != value:
            self._tx_count = value
            if self._model:
                self._model.afterSetTxCount()

    @serializable
    @property
    def txList(self) -> List[AbstractCoin.Tx]:
        return self._tx_list

    def appendTx(self, tx: AbstractCoin.Tx) -> bool:
        for etx in self._tx_list:
            if tx.name != etx.name:
                continue
            if etx.height == -1:
                etx.height = tx.height
                etx.time = tx.time
                # TODO compare/replace input/output list
                return True
            return False

        if self._model:
            self._model.beforeAppendTx(tx)
        self._tx_list.append(tx)
        if self._model:
            self._model.afterAppendTx(tx)
        return True

    @serializable
    @property
    def utxoList(self) -> List[AbstractCoin.Tx.Utxo]:
        return self._utxo_list

    @utxoList.setter
    def utxoList(self, utxo_list: List[AbstractCoin.Tx.Utxo]) -> None:
        if self._utxo_list == utxo_list:
            return

        for utxo in utxo_list:
            utxo.address = self
        self._utxo_list = utxo_list

        if self._model:
            self._model.afterSetUtxoList()
        self._coin.refreshUtxoList()

        self.amount = sum(map(lambda u: u.amount, self._utxo_list))

    @serializable
    @property
    def historyFirstOffset(self) -> str:
        return self._history_first_offset

    @historyFirstOffset.setter
    def historyFirstOffset(self, value: str):
        if self._history_first_offset != value:
            if not value:
                self._clearHistoryOffsets()
            else:
                self._history_first_offset = value
                if self._model:
                    self._model.afterSetHistoryFirstOffset()

    @serializable
    @property
    def historyLastOffset(self) -> str:
        return self._history_last_offset

    @historyLastOffset.setter
    def historyLastOffset(self, value: str):
        if self._history_last_offset != value:
            if not value:
                self._clearHistoryOffsets()
            else:
                self._history_last_offset = value
                if self._model:
                    self._model.afterSetHistoryLastOffset()

    def _clearHistoryOffsets(self) -> None:
        self._history_first_offset = ""
        self._history_last_offset = ""
        if self._model:
            self._model.afterSetHistoryFirstOffset()
            self._model.afterSetHistoryLastOffset()
