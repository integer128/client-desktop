# JOK++
from __future__ import annotations

from enum import Enum
from typing import TYPE_CHECKING

from .address import AbstractAddress
from ..utils.serialize import Serializable, serializable

if TYPE_CHECKING:
    from typing import Any, List, Optional, Tuple
    from .coin import AbstractCoin
    from ..wallet.address import CAddress


class TxStatus(Enum):
    PENDING = 0
    CONFIRMED = 1
    COMPLETE = 2


class AbstractTxIo(AbstractAddress):
    def __init__(
            self,
            coin: AbstractCoin,
            *,
            output_type: str,
            address_type: str,
            address_name: str,
            amount: int) -> None:
        super().__init__(
            coin,
            name=address_name,
            amount=amount)


class TxModelInterface:
    def afterSetHeight(self) -> None:
        raise NotImplementedError

    def afterSetTime(self) -> None:
        raise NotImplementedError


class AbstractTx(Serializable):
    class TxIo(AbstractTxIo):
        pass

    def __init__(
            self,
            address: AbstractAddress,
            *,
            name: str,
            height: int = -1,
            time: int = -1,
            amount: int,
            fee: int,
            coinbase: bool,
            input_list: List[TxIo],
            output_list: List[TxIo]) -> None:
        super().__init__()

        self._address = address
        self._name = name.strip().lower()

        self._height = height
        self._time = time
        self._amount = amount
        self._fee = fee
        self._coinbase = coinbase

        self._input_list = input_list
        self._output_list = output_list

        self._model: Optional[TxModelInterface] = \
            self._address.coin.model_factory(self)

    def __eq__(self, other) -> bool:
        if isinstance(other, AbstractTx):
            # TODO compare self._input_list, self._output_list
            return self._name == other._name
        raise TypeError

    def __hash__(self) -> int:
        return hash(self._name)

    @classmethod
    def _deserialize(cls, args: Tuple[Any], key: str, value: Any) -> Any:
        if isinstance(value, dict):
            if key in ("input_list", "output_list"):
                return cls.TxIo(args[0].coin, **value)
        return super()._deserialize(args, key, value)

    @property
    def model(self) -> Optional[TxModelInterface]:
        return self._model

    @property
    def address(self) -> AbstractAddress:
        return self._address

    @serializable
    @property
    def name(self) -> str:
        return self._name

    @serializable
    @property
    def height(self) -> int:
        return self._height

    @height.setter
    def height(self, value: int) -> None:
        if self._height != value:
            assert self._height == -1
            self._height = value
            if self._model:
                self._model.afterSetHeight()

    @property
    def confirmations(self) -> int:
        if 0 <= self._height <= self._address.coin.height:
            return self._address.coin.height - self._height + 1
        return 0

    @property
    def status(self) -> TxStatus:
        c = self.confirmations
        if c <= 0:
            return TxStatus.PENDING
        if c <= 6:  # TODO const
            return TxStatus.CONFIRMED
        return TxStatus.COMPLETE

    @serializable
    @property
    def time(self) -> int:
        return self._time

    @time.setter
    def time(self, value: int) -> None:
        if self._time != value:
            self._time = value
            if self._model:
                self._model.afterSetTime()

    @serializable
    @property
    def amount(self) -> int:
        return self._amount

    @serializable
    @property
    def fee(self) -> int:
        return self._fee

    @serializable
    @property
    def coinbase(self) -> bool:
        return self._coinbase

    @serializable
    @property
    def inputList(self) -> List[TxIo]:
        return self._input_list

    @serializable
    @property
    def outputList(self) -> List[TxIo]:
        return self._output_list


class AbstractUtxo(Serializable):
    def __init__(
            self,
            address: CAddress,
            *,
            tx_name: str,
            height: int,
            index: int,
            amount: int) -> None:
        super().__init__()
        self._address = address
        self._tx_name = tx_name
        self._height = height
        self._index = index
        self._amount = amount

    @property
    def address(self) -> CAddress:
        return self._address

    @serializable
    @property
    def txName(self) -> str:
        return self._tx_name

    @serializable
    @property
    def height(self) -> int:
        return self._height

    @serializable
    @property
    def index(self) -> int:
        return self._index

    @serializable
    @property
    def amount(self) -> int:
        return self._amount


class AbstractMutableTx:
    def __init__(self, coin: AbstractCoin) -> None:
        self._logger = Logger.getClassLogger(
            __name__,
            self.__class__,
            coin.shortName)
        self._coin = coin
        self._source_list: List[AbstractAddress] = []
        self._source_amount = 0

    def refreshSourceList(self) -> None:
        self._source_list.clear()
        self._source_amount = 0

        for address in self._coin.addressList:
            if address.readOnly:
                continue

            append = False
            for utxo in address.utxoList:
                if utxo.amount > 0:
                    append = True
                    self._source_amount += utxo.amount

            if append:
                self._source_list.append(address)
                self._logger.debug(
                    "Address \"%s\" appended to source list.",
                    address.name)

        # TODO check,filter unique

        self.filter_sources()


