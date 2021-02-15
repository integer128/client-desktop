from __future__ import annotations

from typing import Final, TYPE_CHECKING

from PySide2.QtCore import \
    Property as QProperty, \
    QObject, \
    Signal as QSignal, \
    Slot as QSlot

from . import AbstractModel, AbstractStateModel
from .address import AddressListModel
from .amount import AmountInputModel, AmountModel

if TYPE_CHECKING:
    from ..ui.gui import Application
    from ..wallet.mutable_tx import MutableTransaction


class AbstractTransactionBroadcastStateModel(AbstractStateModel):
    def __init__(
            self,
            application: Application,
            tx: MutableTransaction) -> None:
        super().__init__(application, tx.coin)
        self._tx = tx


class TransactionBroadcastAvailableAmountModel(AmountModel):
    def __init__(
            self,
            application: Application,
            tx: MutableTransaction) -> None:
        super().__init__(application, tx.coin)
        self._tx = tx

    def _getValue(self) -> int:
        return self._tx.source_amount


class TransactionBroadcastAmountModel(AmountInputModel):
    def __init__(
            self,
            application: Application,
            tx: MutableTransaction) -> None:
        super().__init__(application, tx.coin)
        self._tx = tx

    def _getValue(self) -> int:
        return self._tx.amount

    def _setValue(self, value: int) -> bool:
        if value < 0:
            # TODO set _tx invalid value
            return False
        self._tx.amount = value
        return True

    def _setDefaultValue(self) -> bool:
        self._tx.set_max()
        return True


class TransactionBroadcastFeeAmountModel(AmountInputModel):
    __stateChanged = QSignal()

    def __init__(
            self,
            application: Application,
            tx: MutableTransaction) -> None:
        super().__init__(application, tx.coin)
        self._tx = tx

    def refresh(self) -> None:
        super().refresh()
        self.__stateChanged.emit()

    def _getValue(self) -> int:
        return self._tx.fee

    def _setValue(self, value: int) -> bool:
        if value < 0:
            # TODO set _tx invalid value
            return False
        self._tx.fee = value
        return True

    def _setDefaultValue(self) -> bool:
        self._tx.spb = -1  # TODO
        return True

    @QProperty(str, notify=__stateChanged)
    def amountPerKiBHuman(self) -> str:
        return self._toHumanValue(self._tx.spb * 1024, self._coin.currency)

    # noinspection PyTypeChecker
    @QSlot(str, result=bool)
    def setAmountPerKiBHuman(self, value: str) -> bool:
        value = self._fromHumanValue(value, self._coin.currency)
        if value is None or value < 0:
            # TODO set _tx invalid value
            return False
        value //= 1024
        if self._tx.spb != value:
            self._tx.spb = value
            self.refresh()
        return True

    @QProperty(bool, notify=__stateChanged)
    def subtractFromAmount(self) -> bool:
        return self._tx.subtract_fee

    # noinspection PyTypeChecker
    @QSlot(bool, result=bool)
    def setSubtractFromAmount(self, value: bool) -> bool:
        if value != self._tx.subtract_fee:
            self._tx.subtract_fee = value
            self.refresh()
        return True


class TransactionBroadcastChangeAmountModel(AmountModel):
    __stateChanged = QSignal()

    def __init__(
            self,
            application: Application,
            tx: MutableTransaction) -> None:
        super().__init__(application, tx.coin)
        self._tx = tx

    def refresh(self) -> None:
        super().refresh()
        self.__stateChanged.emit()

    def _getValue(self) -> int:
        return self._tx.change

    @QProperty(bool, notify=__stateChanged)
    def toNewAddress(self) -> bool:
        return self._tx.new_address_for_change

    # noinspection PyTypeChecker
    @QSlot(bool, result=bool)
    def setToNewAddress(self, value: bool) -> bool:
        if value != self._tx.new_address_for_change:
            self._tx.new_address_for_change = value
            self.refresh()
        return True


class TransactionBroadcastReceiverModel(AbstractTransactionBroadcastStateModel):
    stateChanged: Final = QSignal()

    @QProperty(str, notify=stateChanged)
    def addressName(self) -> str:
        return self._tx.receiver

    # noinspection PyTypeChecker
    @QSlot(str, result=bool)
    def setAddressName(self, name: str) -> bool:
        if self._tx.setReceiverAddressName(name):
            self.refresh()
            return True
        return False
