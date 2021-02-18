from __future__ import annotations

from abc import ABCMeta
from typing import Optional, Sequence, TYPE_CHECKING

from PySide2.QtCore import \
    Property as QProperty, \
    QObject, \
    Signal as QSignal

from . import AbstractModel, AbstractStateModel, ValidStatus
from .amount import AmountInputModel, AmountModel
from .tx import TransactionIoListModel

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


class AbstractTransactionAmountModel(AmountModel, metaclass=ABCMeta):
    def __init__(
            self,
            application: Application,
            tx: MutableTransaction) -> None:
        super().__init__(application, tx.coin)
        self._tx = tx


class AbstractTransactionAmountInputModel(AmountInputModel, metaclass=ABCMeta):
    def __init__(
            self,
            application: Application,
            tx: MutableTransaction) -> None:
        super().__init__(application, tx.coin)
        self._tx = tx


class TransactionBroadcastAvailableAmountModel(AbstractTransactionAmountModel):
    def _getValue(self) -> Optional[int]:
        return self._tx.source_amount


class TransactionBroadcastAmountModel(AbstractTransactionAmountInputModel):
    def _getValue(self) -> Optional[int]:
        return None if self._tx.amount < 0 else self._tx.amount  # TODO

    def _setValue(self, value: Optional[int]) -> bool:
        if value is None or value < 0:
            self._tx.amount = -1   # TODO
            return False
        self._tx.amount = value
        return True

    def _getDefaultValue(self) -> Optional[int]:
        v = self._tx.get_max_amount()
        return None if v < 0 else v   # TODO

    def _getValidStatus(self) -> ValidStatus:
        if self._tx.amount >= 0:   # TODO
            return ValidStatus.Accept
        else:
            return ValidStatus.Reject


class TransactionBroadcastFeeAmountModel(AbstractTransactionAmountModel):
    __stateChanged = QSignal()

    def _getValue(self) -> Optional[int]:
        return None if self._tx.spb < 0 else self._tx.fee  # TODO

    @QProperty(bool, notify=__stateChanged)
    def subtractFromAmount(self) -> bool:
        return self._tx.subtract_fee

    @subtractFromAmount.setter
    def _setSubtractFromAmount(self, value: bool) -> None:
        if value != self._tx.subtract_fee:
            self._tx.subtract_fee = value
            self.refresh()


class TransactionBroadcastKibFeeAmountModel(
        AbstractTransactionAmountInputModel):
    def _getValue(self) -> Optional[int]:
        return None if self._tx.spb < 0 else (self._tx.spb * 1024)  # TODO

    def _setValue(self, value: Optional[int]) -> bool:
        if value is None or value < 0:
            self._tx.spb = -1
            return False
        self._tx.spb = value // 1024
        return True

    def _getDefaultValue(self) -> Optional[int]:
        v = self._tx.spb_default()
        return None if v < 0 else (v * 1024)

    def _getValidStatus(self) -> ValidStatus:
        if self._tx.spb >= 0:  # TODO
            return ValidStatus.Accept
        else:
            return ValidStatus.Reject


class TransactionBroadcastChangeAmountModel(AbstractTransactionAmountModel):
    __stateChanged = QSignal()

    def _getValue(self) -> Optional[int]:
        return self._tx.change

    @QProperty(bool, notify=__stateChanged)
    def toNewAddress(self) -> bool:
        return self._tx.new_address_for_change

    @toNewAddress.setter
    def _setToNewAddress(self, value: bool) -> None:
        if value != self._tx.new_address_for_change:
            self._tx.new_address_for_change = value
            self.refresh()


class TransactionBroadcastReceiverModel(AbstractTransactionBroadcastStateModel):
    __stateChanged = QSignal()

    def __init__(
            self,
            application: Application,
            tx: MutableTransaction) -> None:
        super().__init__(application, tx)
        self._first_use = True

    @QProperty(str, notify=__stateChanged)
    def addressName(self) -> str:
        return self._tx.receiver

    @addressName.setter
    def _setAddressName(self, value: str) -> None:
        self._tx.setReceiverAddressName(value)
        self._first_use = False
        self.refresh()

    def _getValidStatus(self) -> ValidStatus:
        if self._tx.receiver_valid:
            return ValidStatus.Accept
        elif self._first_use:
            return ValidStatus.Unset
        return ValidStatus.Reject


class TransactionBroadcastInputListModel(TransactionIoListModel):
    __stateChanged = QSignal()

    def __init__(self, application: Application, source_list: Sequence) -> None:
        super().__init__(application, source_list)
        self.rowsInserted.connect(lambda **_: self.__stateChanged.emit())
        self.rowsRemoved.connect(lambda **_: self.__stateChanged.emit())

    @QProperty(bool, notify=__stateChanged)
    def useAllInputs(self) -> bool:
        for i in range(0, self.rowCount()):
            state = self.data(self.index(i), self.Role.STATE)
            if not state.useAsTransactionInput:
                return False
        return True

    @useAllInputs.setter
    def _setUseAllInputs(self, value: bool) -> None:
        changed = False
        for i in range(0, self.rowCount()):
            state = self.data(self.index(i), self.Role.STATE)
            if state.useAsTransactionInput != value:
                state.useAsTransactionInput = value
                changed = True
        if changed:
            self.__stateChanged.emit()


class TransactionBroadcastModel(AbstractModel):
    def __init__(
            self,
            application: Application,
            tx: MutableTransaction) -> None:
        super().__init__(application)
        self._tx = tx

        self._available_amount = TransactionBroadcastAvailableAmountModel(
            self._application,
            self._tx)
        self.connectModelRefresh(self._available_amount)

        self._amount = TransactionBroadcastAmountModel(
            self._application,
            self._tx)
        self.connectModelRefresh(self._amount)

        self._fee_amount = TransactionBroadcastFeeAmountModel(
            self._application,
            self._tx)
        self.connectModelRefresh(self._fee_amount)

        self._kib_fee_amount = TransactionBroadcastKibFeeAmountModel(
            self._application,
            self._tx)
        self.connectModelRefresh(self._kib_fee_amount)

        self._change_amount = TransactionBroadcastChangeAmountModel(
            self._application,
            self._tx)
        self.connectModelRefresh(self._change_amount)

        self._receiver = TransactionBroadcastReceiverModel(
            self._application,
            self._tx)
        self.connectModelRefresh(self._receiver)

        self._input_list = TransactionBroadcastInputListModel(
            self._application,
            self._tx.sources)

    @QProperty(QObject, constant=True)
    def availableAmount(self) -> TransactionBroadcastAvailableAmountModel:
        return self._available_amount

    @QProperty(QObject, constant=True)
    def amount(self) -> TransactionBroadcastAmountModel:
        return self._amount

    @QProperty(QObject, constant=True)
    def feeAmount(self) -> TransactionBroadcastFeeAmountModel:
        return self._fee_amount

    @QProperty(QObject, constant=True)
    def kibFeeAmount(self) -> TransactionBroadcastKibFeeAmountModel:
        return self._kib_fee_amount

    @QProperty(QObject, constant=True)
    def changeAmount(self) -> TransactionBroadcastChangeAmountModel:
        return self._change_amount

    @QProperty(QObject, constant=True)
    def receiver(self) -> TransactionBroadcastReceiverModel:
        return self._receiver

    @QProperty(QObject, constant=True)
    def inputList(self) -> TransactionBroadcastInputListModel:
        return self._input_list
