# JOK++
from __future__ import annotations

from typing import TYPE_CHECKING

from .parser import \
    AbstractParser, \
    CoinsInfoParser, \
    ParseError, \
    ResponseDataParser, \
    ResponseErrorParser, \
    ResponseMetaParser, \
    SysinfoParser, \
    TxParser
from ..query import AbstractJsonQuery
from ..utils import urlJoin
from ...coins.hd import HdAddressIterator
from ...logger import Logger

if TYPE_CHECKING:
    from typing import Callable, Dict, Optional, Union
    from ...application import CoreApplication
    from ...coins.coin import AbstractCoin
    from ...wallet.address import CAddress


class AbstractServerApiQuery(AbstractJsonQuery):
    _DEFAULT_CONTENT_TYPE = "application/vnd.api+json"
    _DEFAULT_BASE_URL = "https://d1.bitmarket.network:30110/v1"  # TODO dynamic
    _ACTION = ""

    def __init__(
            self,
            application: CoreApplication,
            *,
            name_suffix: Optional[str]) -> None:
        super().__init__(name_suffix=name_suffix)
        self._application = application

    @property
    def url(self) -> Optional[str]:
        return urlJoin(super().url, self._ACTION)

    def _processResponse(self, response: Optional[dict]) -> None:
        try:
            if response is None:
                self._logger.debug("Empty response.")
                self._processData(None, None, None)
                return

            meta = ResponseMetaParser()
            meta.parse(response)
            if meta.timeframe > ResponseMetaParser.SLOW_TIMEFRAME:
                self._logger.warning(
                    "Server response has taken more than %i seconds.",
                    meta.timeframeSeconds)
            del meta

            # The members data and errors MUST NOT coexist in the same
            # document.
            if "errors" in response:
                ResponseErrorParser().parse(response, self._processError)
            elif "data" in response:
                ResponseDataParser().parse(response, self._processData)
            else:
                raise ParseError("empty response")
        except ParseError as e:
            self._logger.error("Invalid server response: %s.", str(e))

    def _processError(self, error: int, message: str) -> None:
        self._logger.error(
            "Server error: %s",
            Logger.errorToString(error, message))

    def _processData(
            self,
            data_id: Optional[str],
            data_type: Optional[str],
            value: Optional[dict]) -> None:
        raise NotImplementedError


class SysinfoApiQuery(AbstractServerApiQuery):
    _ACTION = "sysinfo"

    def __init__(self, application: CoreApplication) -> None:
        super().__init__(application, name_suffix=None)

    def _processData(
            self,
            data_id: Optional[str],
            data_type: Optional[str],
            value: Optional[dict]) -> None:
        if self.statusCode != 200 or value is None:
            return

        parser = SysinfoParser()
        parser.parse(value, self._DEFAULT_BASE_URL)

        self._logger.info(
            "Server version: %s %s (0x%08x).",
            parser.serverData["server_name"],
            parser.serverData["server_version_string"],
            parser.serverData["server_version"])

        for coin in self._application.coinList:
            coin.serverData = {
                **parser.serverData,
                **parser.serverCoinList.get(coin.shortName, {})
            }


class CoinsInfoApiQuery(AbstractServerApiQuery):
    _ACTION = "coins"

    def __init__(self, application: CoreApplication) -> None:
        super().__init__(application, name_suffix=None)

    def _processData(
            self,
            data_id: Optional[str],
            data_type: Optional[str],
            value: Optional[dict]) -> None:
        if self.statusCode != 200 or value is None:
            return

        for coin in self._application.coinList:
            state_hash = coin.stateHash
            parser = CoinsInfoParser()
            if not parser.parse(value, coin.shortName):
                self._logger.warning(
                    "Coin \"%s\" not found in server response.",
                    coin.shortName)
                continue

            # TODO legacy order
            coin.status = parser.status
            coin.unverifiedHash = parser.unverifiedHash
            coin.unverifiedOffset = parser.unverifiedOffset
            coin.offset = parser.offset
            coin.verifiedHeight = parser.verifiedHeight
            coin.height = parser.height

            if coin.stateHash == state_hash:
                continue

            self._logger.debug("Coin state was changed, updating addresses...")
            # TODO
            #    self._application.databaseThread.saveCoin.emit(coin)
            #    for address in coin.addressList:
            #        self._application.networkQueryManager.put(
            #            AddressInfoApiQuery(self._application, address))
            #            self.parent()._run_cmd(AddressInfoApiQuery(a, self.parent()))
            #            self.parent()._run_cmd(AddressHistoryCommand(a, parent=self.parent()))


class AddressInfoApiQuery(AbstractServerApiQuery):
    _ACTION = "coins"

    def __init__(
            self,
            application: CoreApplication,
            address: CAddress) -> None:
        super().__init__(
            application,
            name_suffix="{}:{}".format(address.coin.shortName, address.name))
        self._address = address

    @property
    def url(self) -> Optional[str]:
        return urlJoin(
            super().url,
            self._address.coin.shortName,
            self._address.name)

    def _processData(
            self,
            data_id: Optional[str],
            data_type: Optional[str],
            value: Optional[dict]) -> None:
        if self.statusCode != 200 or value is None:
            return
        print(value)

class HdAddressIteratorApiQuery(AddressInfoApiQuery):
    def __init__(
            self,
            application: CoreApplication,
            coin: AbstractCoin,
            *,
            finished_callback: Callable[
                [HdAddressIteratorApiQuery], None] = None,
            _hd_iterator: Optional[HdAddressIterator] = None,
            _current_address: Optional[CAddress] = None) -> None:
        if _hd_iterator is None:
            _hd_iterator = HdAddressIterator(coin)
        if _current_address is None:
            _current_address = next(_hd_iterator)
        super().__init__(application, _current_address)
        self._hd_iterator = _hd_iterator
        self._finished_callback = finished_callback
        self._next_query: Optional[HdAddressIteratorApiQuery] = None

    def _processData(
            self,
            data_id: Optional[str],
            data_type: Optional[str],
            value: Optional[dict]) -> None:
        if self.statusCode != 200 or value is None:
            return

        self._address.amount = parseItemKey(value, "balance", int)
        tx_count = parseItemKey(value, "number_of_transactions", int)

        if tx_count == 0 and self._address.amount == 0:
            self._hd_iterator.appendAddressToEmptyList(self._address)
        else:
            self._hd_iterator.appendAddressToCoin(self._address)

        try:
            next_address = next(self._hd_iterator)
        except StopIteration:
            self._logger.debug(
                "HD iteration was finished for coin \"%s\".",
                self._address.coin.fullName)
            return

        self._next_query = self.__class__(
            self._application,
            self._address.coin,
            finished_callback=self._finished_callback,
            _hd_iterator=self._hd_iterator,
            _current_address=next_address)

    def _onResponseFinished(self) -> None:
        super()._onResponseFinished()
        if self._next_query is None:
            self._finished_callback(self)
        else:
            self._application.networkQueryManager.put(self._next_query)
