# JOK4
from __future__ import annotations

from typing import TYPE_CHECKING

from .coins.abstract.coin import AbstractCoin
from .network.api_v1.query import \
    AddressTxIteratorApiQuery, \
    AddressUtxoIteratorApiQuery

if TYPE_CHECKING:
    from .wallet.mtx_impl import Mtx
    from .network.query_scheduler import NetworkQueryScheduler
    from .database.db_wrapper import Database


class _AbstractInterface:
    def __init__(
            self,
            *args,
            query_scheduler: NetworkQueryScheduler,
            database: Database,
            **kwargs):
        super().__init__(*args, **kwargs)
        self._query_scheduler = query_scheduler
        self._database = database


class CoinInterface(_AbstractInterface, AbstractCoin.Interface):
    def afterSetHeight(self) -> None:
        pass

    def afterSetStatus(self) -> None:
        pass

    def afterSetFiatRate(self) -> None:
        pass

    def afterRefreshAmount(self) -> None:
        pass

    def beforeAppendAddress(self, address: AbstractCoin.Address) -> None:
        pass

    def afterAppendAddress(self, address: AbstractCoin.Address) -> None:
        if self._database.isLoaded:
            self._database.writeCoinAddress(address)

        self._query_scheduler.manager.put(AddressTxIteratorApiQuery(
            address,
            query_manager=self._query_scheduler.manager))
        self._query_scheduler.manager.put(AddressUtxoIteratorApiQuery(
            address,
            query_manager=self._query_scheduler.manager))

        # self._run_cmd(net_cmd.AddressInfoApiQuery(wallet, self)) TODO

    def afterSetServerData(self) -> None:
        pass

    def afterStateChanged(self) -> None:
        if self._database.isLoaded:
            self._database.writeCoin(self._coin)

        for address in self._coin.addressList:
            pass
            # TODO
            # AddressInfoApiQuery(self._application, address))
            # AddressHistoryCommand()


class AddressInterface(_AbstractInterface, AbstractCoin.Address.Interface):
    def afterSetAmount(self) -> None:
        if self._database.isLoaded:
            self._database.writeCoinAddress(self._address)

        # TODO
        # if balance != self._address.amount or \
        #        txCount != self._address.txCount or \
        #        type_ != self._address.type:
        #    self._address.type = type_
        #    database.writeCoinAddress(self._address)
        #    diff = txCount - len(self._address.txList)
        #    if diff > 0 and not self._address.is_going_update:
        #       AddressHistoryCommand(self._address, parent=self)
        pass

    def afterSetLabel(self) -> None:
        if self._database.isLoaded:
            self._database.writeCoinAddress(self._address)

    def afterSetComment(self) -> None:
        if self._database.isLoaded:
            self._database.writeCoinAddress(self._address)

    def afterSetTxCount(self) -> None:
        if self._database.isLoaded:
            self._database.writeCoinAddress(self._address)

    def beforeAppendTx(self, tx: AbstractCoin.Tx) -> None:
        pass

    def afterAppendTx(self, tx: AbstractCoin.Tx) -> None:
        if self._database.isLoaded:
            self._database.writeCoinTx(tx)

        # TODO
        # self._application.uiManager.process_incoming_tx(tx)
        pass


class TxInterface(_AbstractInterface, AbstractCoin.Tx.Interface):
    def afterSetHeight(self) -> None:
        pass

    def afterSetTime(self) -> None:
        pass


class MutableTxInterface(_AbstractInterface, AbstractCoin.MutableTx.Interface):

    def onBroadcast(self, tx: Mtx) -> None:
        from .network.api_v1.query import TxBroadcastApiQuery
        query = TxBroadcastApiQuery(tx)
        self._query_scheduler.manager.put(query, high_priority=True)
        # TODO force mempool

        # TODO
        # if parser.txName != self._tx.name:
        #     self._logger.warning(
        #         "Server gives transaction: \'%s\", but was sent \"%s\".",
        #         parser.txName,
        #         self._tx.name)
