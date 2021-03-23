from __future__ import annotations

import logging
from datetime import datetime
from typing import List, Optional, TYPE_CHECKING, Union

import PySide2.QtCore as qt_core

from . import hd, key, mtx_impl
from ..coins.address import AbstractAddress

if TYPE_CHECKING:
    from ..coins.coin import AbstractCoin
    from ..coins.tx import AbstractTx

log = logging.getLogger(__name__)


def offset_less(left: str, right: str) -> bool:
    if not left:
        return True
    l = left.partition('.')
    r = right.partition('.')
    # equality matters
    if int(l[0]) <= int(r[0]):
        return True
    if l[0] == r[0]:
        return int(l[2]) < int(r[2])
    return False


class AddressError(Exception):
    pass


class CAddress(AbstractAddress):
    balanceChanged = qt_core.Signal()
    labelChanged = qt_core.Signal()
    useAsSourceChanged = qt_core.Signal()
    txCountChanged = qt_core.Signal()

    def __init__(
            self,
            coin: AbstractCoin,
            **kwargs):
        if kwargs["name"] is None:
            kwargs["name"] = "null"
        assert coin is not None

        super().__init__(coin, **kwargs)

        self.__created = None
        self.__first_offset = None
        self.__last_offset = None
        self.__type = key.AddressType.P2PKH
        # use as source in current tx
        self.__use_as_source = True
        self.__unspents_time = qt_core.QTime()
        # for back
        self.__going_to_update = False
        # for ui .. this is always ON when goint_to_update ON but conversely
        self.__updating_history = False
        # to stop network stuff
        self.__deleted = False
        #
        self.__key = None
        # from server!!
        self.__tx_count = 0
        self.__local__tx_count = 0
        #
        self.__valid = True
        # this map can be updated before each transaction
        self.__unspents = []

    def create(self):
        self.__created = datetime.now()

    # no getter for it for security reasons
    def set_prv_key(self, value: Union[hd.HDNode, key.PrivateKey]) -> None:
        self.__key = value

    @classmethod
    def make_from_hd(cls, hd__key: hd.HDNode, coin, type_: key.AddressType,
                     witver=0) -> "CAddress":
        res = cls(coin, name=hd__key.to_address(type_, witver))
        res.create()
        res.__key = hd__key
        res.type = type_
        return res

    @property
    def deleted(self) -> bool:
        return self.__deleted

    @property
    def hd_index(self) -> Optional[int]:
        if self.__key and isinstance(self.__key, hd.HDNode):
            return self.__key.index

    @property
    def type(self) -> key.AddressType:
        return self.__type

    @type.setter
    def type(self, val: Union[str, key.AddressType]):
        if isinstance(val, (int, key.AddressType)):
            self.__type = val
        else:
            self.__type = key.AddressType.make(val)

    @property
    def unspents(self) -> List[mtx_impl.UTXO]:
        return self.__unspents

    @unspents.setter
    def unspents(self, utxos: List[mtx_impl.UTXO]) -> None:
        self.__unspents = utxos
        self.__unspents_time.restart()

        def summ(u):
            u.address = self
            return int(u.amount)
        amount = sum(map(summ, self.__unspents))
        if amount != self._amount:
            log.debug(
                f"Balance of {self} updated from {self._amount} to {amount}. Processed: {len(self.__unspents)} utxo")
            # strict !!! remember notifiers
            self.amount = amount

    @property
    def wants_update_unspents(self) -> bool:
        return self.__unspents_time.isNull() or self.__unspents_time.elapsed() > 60000

    def process_unspents(self, unspents: List[dict]) -> None:
        def mapper(table):
            ux = mtx_impl.UTXO.from_net(
                amount=table["amount"],
                txindex=table["index"],
                txid=table["tx"],
                type=key.AddressType(self.__type).lower,
                address=self,
            )
            if ux.amount > 0:
                return ux
        self.unspents = [u for u in map(mapper, unspents) if u]

    def from_args(self, arg_iter: iter):
        try:
            self.rowId = next(arg_iter)
            self.label = next(arg_iter)
            self.comment = next(arg_iter)
            #
            self.__created = datetime.fromtimestamp(next(arg_iter))
            self.__type = next(arg_iter)
            self._amount = next(arg_iter)
            #
            self.__tx_count = next(arg_iter)
            # use setters !!
            self.first_offset = next(arg_iter)
            self.last_offset = next(arg_iter)
            #
            self.import_key(next(arg_iter))
        except StopIteration as si:
            raise StopIteration(
                f"Too few arguments for address {self}") from si

    def is_receiver(self, tx: AbstractTx) -> bool:
        return any(self.name == o.address for o in tx.output_iter)

    def _get_first_offset(self) -> int:
        return self.__first_offset

    def _set_first_offset(self, bh: int):
        self.__first_offset = str(bh)

    def update_tx_list(self, first_offset: Optional[int], clear_tx_from: Optional[int], verbose: bool):
        self.__first_offset = first_offset
        if clear_tx_from is not None:
            to_remove = []
            for k in self._tx_list:
                if k.height > clear_tx_from:
                    to_remove += [k]
                else:
                    break
            if to_remove:
                from ..application import CoreApplication
                CoreApplication.instance().databaseThread.removeTxList.emit(to_remove)
                with self.model.txList.lockRemoveRows(0, len(to_remove)):
                    # TODO
                    #self._tx_list.remove(0, len(to_remove))
                    pass
                self.txCount -= len(to_remove)
                if verbose:
                    log.debug(
                        f"{len(to_remove)} tx were removed and {len(self._tx_list)} left in {self} ")

    def _get_last_offset(self) -> str:
        return self.__last_offset

    def _set_last_offset(self, bh):
        if not bh or 'None' == bh:
            return
        if bh == self.__last_offset:
            return
        if isinstance(bh, str):
            if not self.__last_offset or offset_less(bh, self.__last_offset):
                self.__last_offset = bh
                return
        else:
            raise TypeError(type(bh))
        log.warning("Offsset skipped")

    @property
    def realTxCount(self) -> int:
        return len(self._tx_list)

    @property
    def txCount(self) -> int:
        return self.__tx_count + self.__local__tx_count

    @txCount.setter
    def _set_tx_count(self, txc: int):
        if txc == self.__tx_count:
            return
        self.__tx_count = txc
        self.txCountChanged.emit()

    def __bool__(self) -> bool:
        return self is not None

    def __hash__(self):
        return hash(self._name)

    def __eq__(self, other: "CAddress") -> bool:
        if other is None or not isinstance(other, CAddress):
            return False
        return self._name == other.name and \
            self.__type == other.type and \
            self.__last_offset == other.last_offset and \
            self.__first_offset == other.first_offset and \
            True

    def _get_valid(self) -> bool:
        return self.__valid

    def _set_valid(self, val: bool):
        self.__valid = val

    def clear(self):
        self._tx_list.clear()
        self.__first_offset = None
        self.__last_offset = None
        self.__tx_count = 0
        self.__deleted = True

    @property
    def private_key(self) -> str:
        if isinstance(self.__key, hd.HDNode):
            return self.__key.key
        if isinstance(self.__key, key.PrivateKey):
            return self.__key

    def export_key(self) -> str:
        if self.__key:
            if isinstance(self.__key, hd.HDNode):
                return self.__key.extended_key
            if isinstance(self.__key, key.PrivateKey):
                return self.__key.to_wif
            log.warn(f"Unknown key type {type(self.__key)} in {self}")
        return ""

    def import_key(self, txt: str):
        if txt:
            try:
                self.__key = hd.HDNode.from_extended_key(txt, self)
                assert self._coin.hd_node is None or self.__key.p_fingerprint == self._coin.hd_node.fingerprint
            except hd.HDError:
                self.__key = key.PrivateKey.from_wif(txt)
            # log.debug(f"new key created for {self} => {self.__key}")
            adrr = self.__key.to_address(self.__type)
            if self._name != adrr:
                log.critical(f"ex key: {txt} type: {self.__type}")
                raise AddressError(
                    f"HD generation failed: wrong result address: {adrr} != {self._name} for {self}")

    # qml bindings
    @property
    def isUpdating(self) -> bool:
        self.__deleted = False
        return self.__updating_history

    @isUpdating.setter
    def isUpdating(self, val: bool) -> None:
        if val:
            self.__going_to_update = True
        if val == self.__updating_history:
            return
        self.__updating_history = bool(val)
        ##self._state_model.refresh()

    @property
    def is_going_update(self) -> bool:
        return self.__going_to_update

    @is_going_update.setter
    def is_going_update(self, val: bool) -> None:
        self.__going_to_update = val

    @property
    def useAsSource(self) -> bool:
        return self.__use_as_source

    @property
    def public_key(self) -> str:
        if self.private_key:
            return self.private_key.public__key.to_hex

    @property
    def to_wif(self) -> str:
        if self.private_key:
            return self.private_key.to_wif

    @property
    def canSend(self) -> bool:
        return not self.readOnly and self._amount > 0

    @property
    def created(self) -> datetime:
        return self.__created

    @useAsSource.setter
    def _set_use_as_source(self, on: bool):
        if on == self.__use_as_source:
            return
        log.debug(f"{self} used as source => {on}")
        self.__use_as_source = on
        self.useAsSourceChanged.emit()

    # @qt_core.Property('QVariantList', constant=True)
    @property
    def tx_list(self) -> List:
        return list(self._tx_list)

    @property
    def readOnly(self) -> bool:
        return self.__key is None or \
            isinstance(self.__key, key.PublicKey)

    def save(self):
        from ..application import CoreApplication
        CoreApplication.instance().databaseThread.save_address(self)

    def __len__(self):
        return len(self._tx_list)

    def __getitem__(self, val: int) -> AbstractTx:
        return self._tx_list[val]

    first_offset = property(_get_first_offset, _set_first_offset)
    last_offset = property(_get_last_offset, _set_last_offset)
    valid = property(_get_valid, _set_valid)
