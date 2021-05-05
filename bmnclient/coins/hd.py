# JOK4
from __future__ import annotations

from collections.abc import Iterator
from typing import TYPE_CHECKING

from ..wallet.address import CAddress

if TYPE_CHECKING:
    from typing import Dict, Optional
    from .abstract.coin import AbstractCoin


class HdAddressIterator(Iterator):
    _EMPTY_ADDRESS_LIMIT = 6

    def __init__(self, coin: AbstractCoin, hd_index: int = 0) -> None:
        self._coin = coin
        self._type_index = -1
        self._last_address: Optional[CAddress] = None
        self._hd_index = hd_index
        self._stop = False

        self._empty_address_counter: Dict[AbstractCoin.Address.Type, int] = {}
        for address_type in self._coin.Address.Type:
            if self.isSupportedAddressType(address_type):
                self._empty_address_counter[address_type] = 0
        assert len(self._empty_address_counter) > 0

    def __iter__(self) -> HdAddressIterator:
        return self

    def __next__(self) -> CAddress:
        if self._coin.hdPath is None or self._stop:
            raise StopIteration

        while True:
            for type_index, address_type in enumerate(self._coin.Address.Type):
                if type_index <= self._type_index:
                    continue

                if not self.isSupportedAddressType(address_type):
                    continue

                self._type_index = type_index
                self._last_address = self._coin.createHdAddress(
                    0,
                    False,
                    self._hd_index,
                    address_type)
                return self._last_address

            self._type_index = -1
            self._hd_index += 1

    @classmethod
    def isSupportedAddressType(
            cls,
            address_type: AbstractCoin.Address.Type) -> bool:
        if address_type.value[1] > 0:
            if address_type.value[2] == "p2pkh":
                return True
            if address_type.value[2] == "p2wpkh":
                return True
        return False

    def markLastAddress(self, empty: bool) -> None:
        if not empty:
            self._empty_address_counter[self._last_address.addressType] = 0
        else:
            self._empty_address_counter[self._last_address.addressType] += 1
            for count in self._empty_address_counter.values():
                if count <= self._EMPTY_ADDRESS_LIMIT:
                    return
            self._stop = True
