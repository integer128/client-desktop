# JOK4
from __future__ import annotations

from os import urandom
from random import randint, shuffle
from typing import TYPE_CHECKING
from unittest import TestCase

from bmnclient.coins.coin_bitcoin import Bitcoin, BitcoinTest
from bmnclient.coins.coin_litecoin import Litecoin
from bmnclient.coins.hd import HdNode
from bmnclient.language import Locale

if TYPE_CHECKING:
    from typing import List, Sequence
    from bmnclient.coins.abstract.coin import AbstractCoin


BITCOIN_ADDRESS_LIST = (
    (
        "1PMycacnJaSqwwJqjawXBErnLsZ7RkXUAs", # noqa
        Bitcoin.Address.Type.PUBKEY_HASH,
        0,
        "f54a5851e9372b87810a8e60cdd2e7cfd80b6e31"
    ), (
        "3Ps86GT6vHg7dCT5QhcECDFkRaUJbBzqXB",
        Bitcoin.Address.Type.SCRIPT_HASH,
        5,
        "f33c134a48d70818bdc2cf09631316ce90f71366"
    ), (
        "BC1QW508D6QEJXTDG4Y5R3ZARVARY0C5XW7KV8F3T4", # noqa
        Bitcoin.Address.Type.WITNESS_V0_KEY_HASH,
        0,
        "751e76e8199196d454941c45d1b3a323f1433bd6"
    ), (
        "bc1qeklep85ntjz4605drds6aww9u0qr46qzrv5xswd35uhjuj8ahfcqgf6hak", # noqa
        Bitcoin.Address.Type.WITNESS_V0_SCRIPT_HASH,
        0,
        "cdbf909e935c855d3e8d1b61aeb9c5e3c03ae8021b286839b1a72f2e48fdba70" # noqa
    ), (
        "bc1sw50qa3jx3s",
        Bitcoin.Address.Type.WITNESS_UNKNOWN,
        16,
        "751e"
    ), (
        "bc1gmk9yu",
        None,
        None,
        None
    ), (
        "BC1QR508D6QEJXTDG4Y5R3ZARVARYV98GJ9P", # noqa
        None,
        None,
        None
    )
)

BITCOIN_TEST_ADDRESS_LIST = (
    (
        "mxVFsFW5N4mu1HPkxPttorvocvzeZ7KZyk", # noqa
        BitcoinTest.Address.Type.PUBKEY_HASH,
        0x6f,
        "ba27f99e007c7f605a8305e318c1abde3cd220ac" # noqa
    ), (
       "n49mqVncWxMYwCmZDHXba3Y9RVPzAFTUoX",
       BitcoinTest.Address.Type.PUBKEY_HASH,
       0x6f,
       "f8496d9390c68a99b96e7c438af90f316739a839"
    ), (
        "2N7EFdToQVZviaVC2Wfkidm6HzntiqtVmDE", # noqa
        BitcoinTest.Address.Type.SCRIPT_HASH,
        0xc4,
        "9962b7013858273326d2e36057bde8c844f831a1"
    ), (
        "tb1qu03l73f3rdcjh0ywnhc8vc3yp5gumvgummhv7f", # noqa
        BitcoinTest.Address.Type.WITNESS_V0_KEY_HASH,
        0,
        "e3e3ff45311b712bbc8e9df07662240d11cdb11c"
    ), (
        "tb1qqqqqp399et2xygdj5xreqhjjvcmzhxw4aywxecjdzew6hylgvsesrxh6hy", # noqa
        BitcoinTest.Address.Type.WITNESS_V0_SCRIPT_HASH,
        0,
        "000000c4a5cad46221b2a187905e5266362b99d5e91c6ce24d165dab93e86433"
    ), (
        "tb1qrp33g0q5c5txsp9arysrx4k6zdkfs4nce4xj0gdcccefvpysxf3q0sl5k7", # noqa
        BitcoinTest.Address.Type.WITNESS_V0_SCRIPT_HASH,
        0,
        "1863143c14c5166804bd19203356da136c985678cd4d27a1b8c6329604903262"
    ), (
        "tb1s424qnvez45", # noqa
        BitcoinTest.Address.Type.WITNESS_UNKNOWN,
        16,
        "aaaa" # noqa
    ),
)

LITECOIN_ADDRESS_LIST = (
    (
        "LaMT348PWRnrqeeWArpwQPbuanpXDZGEUz", # noqa
        Litecoin.Address.Type.PUBKEY_HASH,
        0x30,
        "a5f4d12ce3685781b227c1f39548ddef429e9783" # noqa
    ), (
        "MQMcJhpWHYVeQArcZR3sBgyPZxxRtnH441",
        Litecoin.Address.Type.SCRIPT_HASH,
        0x32,
        "b48297bff5dadecc5f36145cec6a5f20d57c8f9b" # noqa
    ), (
        "ltc1q7nlrhuxks5rvc7aumcpzttm3xll3f5zqlp0pyv", # noqa
        Litecoin.Address.Type.WITNESS_V0_KEY_HASH,
        0,
        "f4fe3bf0d68506cc7bbcde0225af7137ff14d040" # noqa
    ), (
        "ltc1q5det08ke2gpet06wczcdfs2v3hgfqllxw28uln8vxxx82qlue6uswceljm", # noqa
        Litecoin.Address.Type.WITNESS_V0_SCRIPT_HASH,
        0,
        "a372b79ed9520395bf4ec0b0d4c14c8dd0907fe6728fcfccec318c7503fcceb9" # noqa
    )
)


class TestCoins(TestCase):
    def _test_address_decode(
            self,
            coin: AbstractCoin,
            address_list: Sequence[tuple]) -> None:
        hash_check_count = 0

        # noinspection PyUnusedLocal
        for (address, type_, version, hash_) in address_list:
            address = coin.Address.decode(coin, name=address)
            if type_ is None:
                self.assertIsNone(address)
            else:
                self.assertIsNotNone(address)
                self.assertEqual(type_, address.type)
                if hash_:
                    self.assertEqual(hash_, address.hash.hex())
                    hash_check_count += 1
                else:
                    self.assertEqual(b"", address.hash)
        self.assertTrue(hash_check_count > 0)

    def test_address_decode(self) -> None:
        self._test_address_decode(
            Bitcoin(),
            BITCOIN_ADDRESS_LIST)
        self._test_address_decode(
            BitcoinTest(),
            BITCOIN_TEST_ADDRESS_LIST)
        self._test_address_decode(
            Litecoin(),
            LITECOIN_ADDRESS_LIST)

    def test_string_to_amount(self) -> None:
        b = Bitcoin.Currency
        satoshi_value = 10 ** 8

        for v in ("", "-", "+", "-.", "+.", "."):
            self.assertIsNone(b.fromString(v))

        for v in ("--11", "++11", "-+11", "+-11", " 11", "11 ", "11. "):
            self.assertIsNone(b.fromString(v))

        for (r, v) in (
                (0, "0"),
                (50 * satoshi_value, "50"),
                (-50 * satoshi_value, "-50"),
                (60 * satoshi_value, "60."),
                (-60 * satoshi_value, "-60."),

                (None, "60.123456789"),
                (None, "-60.123456789"),

                (6012345678, "60.12345678"),
                (-6012345678, "-60.12345678"),
                (6010000000, "60.1"),
                (-6010000000, "-60.1"),
                (6010000000, "60.10"),
                (-6010000000, "-60.10"),
                (6012345670, "60.1234567"),
                (-6012345670, "-60.1234567"),
                (12345670, "0.1234567"),
                (-12345670, "-0.1234567"),
                (11234567, ".11234567"),
                (-11234567, "-.11234567"),
                (11234567, "+.11234567"),

                (0, "-0.00000000"),
                (0, "+0.00000000"),

                (-99999999, "-0.99999999"),
                (None, "-0.099999999"),

                (99999999, "0.99999999"),
                (None, "-0.099999999"),

                (-92233720368 * satoshi_value, "-92233720368"),
                (None, "-92233720369"),

                (92233720368 * satoshi_value, "92233720368"),
                (None, "92233720369"),

                (92233720368 * satoshi_value, "+92233720368"),
                (None, "+92233720369"),

                (-(2 ** 63), "-92233720368.54775808"),
                (None, "92233720369"),

                ((2 ** 63) - 1, "92233720368.54775807"),
                (None, "92233720368.54775808"),

                ((2 ** 63) - 1, "+92233720368.54775807"),
        ):
            self.assertEqual(r, b.fromString(v))

    def test_string_to_amount_locale(self) -> None:
        b = BitcoinTest.Currency
        locale = Locale("en_US")
        for (r, v) in (
                (0, "0"),
                (500000012345678, "5000000.12345678"),
                (500000122345678, "5,000,001.22345678"),
                (500000222345678, "+5,000,002.22345678"),
                (-500000322345678, "-5,000,003.22345678"),
                (None, " 5,000,000.32345678"),
                (None, "5,000,000 .42345678"),
                (None, "5.000,000.52345678"),
                (None, "5 000 000.62345678"),
                (99999999, "0.99999999"),
                (-99999999, "-0.99999999"),
        ):
            self.assertEqual(r, b.fromString(v, locale=locale))

    def test_amount_to_string(self) -> None:
        b = Bitcoin.Currency

        self.assertEqual("0", b.toString(0))
        self.assertEqual("-1", b.toString(-1 * 10 ** 8))
        self.assertEqual("1", b.toString(+1 * 10 ** 8))

        for (s, d) in (
                (1, "0.00000001"),
                (10, "0.0000001"),
                (1000, "0.00001"),
                (1200000, "0.012"),
                (880000000, "8.8"),
                (880000001, "8.80000001"),
                (880000010, "8.8000001"),
                (88000000000, "880")
        ):
            self.assertEqual("-" + d, b.toString(-s))
            self.assertEqual(d, b.toString(s))

        self.assertEqual(
            "92233720368.54775807",
            b.toString(9223372036854775807))
        self.assertEqual(
            "0",
            b.toString(9223372036854775808))
        self.assertEqual(
            "-92233720368.54775808",
            b.toString(-9223372036854775808))
        self.assertEqual(
            "0",
            b.toString(-9223372036854775809))

    def test_mempool_address_lists(self) -> None:
        for limit in range(201):
            coin = Bitcoin()
            for i in range(limit):
                address = coin.Address(
                    coin,
                    name="address_{:06d}".format(i),
                    type_=coin.Address.Type.UNKNOWN)
                self.assertTrue(coin.appendAddress(address))

            limit = randint(1, 10)

            # create
            mempool_list = coin.createMempoolAddressLists(limit)
            count = 0
            for v in mempool_list:
                count += len(v["list"])
                self.assertIsInstance(v["local_hash"], bytes)
                self.assertIsNone(v["remote_hash"])
                self.assertLessEqual(len(v["list"]), limit)
            self.assertEqual(count, len(coin.addressList))

            # noinspection PyProtectedMember
            self.assertEqual(len(coin._mempool_cache), len(mempool_list))

            # set result
            for (i, v) in enumerate(mempool_list):
                self.assertTrue(coin.setMempoolAddressListResult(
                    v["local_hash"],
                    "hash_{:06d}".format(i)))

            # create again
            mempool_list = coin.createMempoolAddressLists(limit)
            for (i, v) in enumerate(mempool_list):
                self.assertIsInstance(v["local_hash"], bytes)
                self.assertIsInstance(v["remote_hash"], str)
                self.assertEqual(v["remote_hash"], "hash_{:06d}".format(i))
                self.assertLessEqual(len(v["list"]), limit)

            # noinspection PyProtectedMember
            self.assertEqual(len(coin._mempool_cache), len(mempool_list))

            # check expired
            for i in range(randint(1, 20)):
                address = coin.Address(
                    coin,
                    name="address_new_{:06d}".format(i),
                    type_=coin.Address.Type.UNKNOWN)
                self.assertTrue(coin.appendAddress(address))

                mempool_list = coin.createMempoolAddressLists(limit)
                # noinspection PyProtectedMember
                self.assertEqual(len(coin._mempool_cache), len(mempool_list))

    def test_serialization(self) -> None:
        root_node = HdNode.deriveRootNode(urandom(64))
        self.assertIsNotNone(root_node)

        purpose_node = root_node.deriveChildNode(
            44,
            hardened=True,
            private=True)
        self.assertIsNotNone(purpose_node)

        coin = Bitcoin()
        self.assertTrue(coin.deriveHdNode(purpose_node))
        coin.height = randint(1000, 100000)
        coin.offset = "offset" + str(randint(1000, 100000))
        coin.unverifiedOffset = "u_offset" + str(randint(1000, 100000))
        coin.unverifiedHash = "u_hash" + str(randint(1000, 100000))
        coin.verifiedHeight = randint(1000, 100000)

        for address_index in range(1, 3):
            address = coin.deriveHdAddress(
                account=0,
                is_change=False,
                amount=randint(1000, 100000),
                tx_count=randint(1000, 100000),
                label="address label " + str(address_index),
                comment="address comment " + str(address_index),
                history_first_offset="first_" + str(randint(1000, 100000)),
                history_last_offset="last_" + str(randint(1000, 100000)))
            self.assertIsNotNone(address)

            input_list = []
            for i in range(1, 3):
                input_list.append(coin.Tx.Io(
                    coin,
                    output_type="output_type_" + str(i),
                    address_name=address.name,
                    amount=randint(1000, 100000)))

            output_list = []
            for i in range(1, 3):
                output_list.append(coin.Tx.Io(
                    coin,
                    output_type="output_type_" + str(i),
                    address_name=address.name,
                    amount=randint(1000, 100000)))
            output_list.append(coin.Tx.Io(
                coin,
                output_type="output_type_nulldata",
                address_name=None,
                amount=0))

            for i in range(1, 4):
                address.appendTx(coin.Tx(
                    coin,
                    name="tx_name_" + str(i),
                    height=randint(10000, 1000000),
                    time=randint(10000, 1000000),
                    amount=randint(10000, 1000000),
                    fee_amount=randint(10000, 1000000),
                    coinbase=randint(0, 1) == 1,
                    input_list=input_list,
                    output_list=output_list))

            address.utxoList = [coin.Tx.Utxo(
                coin,
                name="utxo_" + str(i),
                height=randint(10000, 1000000),
                index=randint(10000, 1000000),
                amount=randint(10000, 1000000)) for i in range(1, 3)]

            coin.appendAddress(address)

        data = coin.serialize()
        self.assertIsInstance(data, dict)

        # from pprint import pprint
        # pprint(data, sort_dicts=False)

        coin_new = Bitcoin()
        Bitcoin.deserialize(coin_new, **data)

        # coin compare
        self.assertEqual(coin.name, coin_new.name)
        self.assertEqual(coin.height, coin_new.height)
        self.assertEqual(coin.offset, coin_new.offset)
        self.assertEqual(coin.unverifiedOffset, coin_new.unverifiedOffset)
        self.assertEqual(coin.unverifiedHash, coin_new.unverifiedHash)
        self.assertEqual(coin.verifiedHeight, coin_new.verifiedHeight)

        # address list compare
        self.assertEqual(len(coin.addressList), len(coin_new.addressList))
        for address_index in range(len(coin.addressList)):
            a1 = coin.addressList[address_index]
            a2 = coin_new.addressList[address_index]
            self.assertEqual(a1.name, a2.name)
            self.assertEqual(a1.exportKey(), a2.exportKey())
            self.assertEqual(a1.amount, a2.amount)
            self.assertEqual(a1.txCount, a2.txCount)
            self.assertEqual(a1.label, a2.label)
            self.assertEqual(a1.comment, a2.comment)
            self.assertEqual(a1.historyFirstOffset, a2.historyFirstOffset)
            self.assertEqual(a1.historyLastOffset, a2.historyLastOffset)

            # tx list compare
            self.assertEqual(len(a1.txList), len(a2.txList))
            for tx_index in range(len(a1.txList)):
                t1 = a1.txList[tx_index]
                t2 = a2.txList[tx_index]
                self.assertEqual(t1.name, t2.name)
                self.assertEqual(t1.height, t2.height)
                self.assertEqual(t1.time, t2.time)
                self.assertEqual(t1.amount, t2.amount)
                self.assertEqual(t1.feeAmount, t2.feeAmount)
                self.assertEqual(t1.coinbase, t2.coinbase)

                # io list compare
                self.assertEqual(len(t1.inputList), len(t2.inputList))
                self.assertEqual(len(t1.outputList), len(t2.outputList))
                for io_index in range(len(t1.inputList)):
                    io1 = t1.inputList[io_index]
                    io2 = t2.inputList[io_index]
                    self.assertEqual(io1.outputType, io2.outputType)
                    self.assertEqual(io1.address.name, io2.address.name)
                    self.assertEqual(io1.address.amount, io2.address.amount)
                for io_index in range(len(t1.outputList)):
                    io1 = t1.outputList[io_index]
                    io2 = t2.outputList[io_index]
                    self.assertEqual(io1.outputType, io2.outputType)
                    self.assertEqual(io1.address.name, io2.address.name)
                    self.assertEqual(io1.address.amount, io2.address.amount)

            # utxo list compare
            self.assertEqual(len(a1.utxoList), len(a2.utxoList))
            for utxo_index in range(len(a1.utxoList)):
                u1 = a1.utxoList[utxo_index]
                u2 = a2.utxoList[utxo_index]
                self.assertEqual(u1.name, u2.name)
                self.assertEqual(u1.height, u2.height)
                self.assertEqual(u1.index, u2.index)
                self.assertEqual(u1.amount, u2.amount)


class TestSelectUtxo(TestCase):
    def setUp(self) -> None:
        self._coin = Bitcoin()
        root_node = HdNode.deriveRootNode(urandom(64))
        self.assertIsNotNone(root_node)
        self.assertTrue(self._coin.deriveHdNode(root_node))

    def _createUtxoList(
            self,
            address: Bitcoin.Address,
            amount_list: Sequence[int]) -> None:
        utxo_list: List[Bitcoin.Tx.Utxo] = []
        for i in range(len(amount_list)):
            utxo_list.append(Bitcoin.Tx.Utxo(
                self._coin,
                name=i.to_bytes(32, "big").hex(),
                height=100 + i,
                index=0,
                amount=amount_list[i]))
        address.utxoList = utxo_list

    @classmethod
    def _isLowHeightUtxo(
            cls,
            utxo_list: List[Bitcoin.Tx.Utxo],
            utxo):
        result = False
        for far_utxo in utxo_list:
            if far_utxo.amount == utxo.amount:
                if far_utxo is not utxo and far_utxo.height > utxo.height:
                    result = True
        return result

    def test_find_ideal_utxo(self) -> None:
        address = self._coin.deriveHdAddress(account=0, is_change=False)
        self.assertIsNotNone(address)

        # no utxo
        for r in range(100):
            # noinspection PyProtectedMember
            utxo = self._coin.TxFactory._findExactUtxo(address.utxoList, r)
            self.assertIsNone(utxo)

        # single utxo with amount 0, 1
        if True:
            for amount in (0, 1):
                self._createUtxoList(address, (amount, ))
                # noinspection PyProtectedMember
                utxo = self._coin.TxFactory._findExactUtxo(address.utxoList, 0)
                if not amount:
                    self.assertIsNotNone(utxo)
                    self.assertEqual(amount, utxo.amount)
                else:
                    self.assertIsNone(utxo)

                # noinspection PyProtectedMember
                utxo = self._coin.TxFactory._findExactUtxo(address.utxoList, 1)
                if not amount:
                    self.assertIsNone(utxo)
                else:
                    self.assertIsNotNone(utxo)
                    self.assertEqual(amount, utxo.amount)

                # noinspection PyProtectedMember
                utxo = self._coin.TxFactory._findExactUtxo(address.utxoList, 2)
                self.assertIsNone(utxo)

        # multiple utxo
        if True:
            self._createUtxoList(address, (0, 1, 2, 3, 4, 5, 6, 6))

            # noinspection PyProtectedMember
            utxo = self._coin.TxFactory._findExactUtxo(address.utxoList, 7)
            self.assertIsNone(utxo)

            # noinspection PyProtectedMember
            utxo = self._coin.TxFactory._findExactUtxo(address.utxoList, 6)
            self.assertIsNotNone(utxo)
            self.assertEqual(6, utxo.amount)
            self.assertTrue(self._isLowHeightUtxo(address.utxoList, utxo))

            # noinspection PyProtectedMember
            utxo = self._coin.TxFactory._findExactUtxo(address.utxoList, 4)
            self.assertIsNotNone(utxo)
            self.assertEqual(4, utxo.amount)

    def test_find_single_address_single_utxo(self) -> None:
        address = self._coin.deriveHdAddress(account=0, is_change=False)
        self.assertIsNotNone(address)

        # find same amount
        if True:
            amount_list = [x for x in range(1000)]
            shuffle(amount_list)
            self._createUtxoList(address, amount_list)
            self.assertEqual(1000, len(address.utxoList))
            for i in range(len(address.utxoList)):
                # noinspection PyProtectedMember
                l, a = self._coin.TxFactory._findOptimalUtxoList(
                    address.utxoList,
                    i)
                self.assertEqual(1, len(l))
                self.assertEqual(i, a)

        # find nearest amount + height test
        if True:
            amount_list = list(range(1, 1000, 2)) + list(range(1, 1000, 2))
            shuffle(amount_list)
            self._createUtxoList(address, amount_list)
            self.assertEqual(500 * 2, len(address.utxoList))
            for i in range(0, 1000, 2):
                # noinspection PyProtectedMember
                l, a = self._coin.TxFactory._findOptimalUtxoList(
                    address.utxoList,
                    i)
                self.assertEqual(1, len(l))
                self.assertEqual(i + 1, a)
                self.assertTrue(self._isLowHeightUtxo(address.utxoList, l[0]))

    def test_find_single_address_multiple_utxo(self) -> None:
        address = self._coin.deriveHdAddress(account=0, is_change=False)
        self.assertIsNotNone(address)

        amount_list = list(range(0, 10)) * 4
        shuffle(amount_list)
        self._createUtxoList(address, amount_list)
        self.assertEqual(40, len(address.utxoList))

        test_list = (
            (9, 9, 1),
            (10, 10, 2),
            (21, 21, 3),
            (28, 28, 4),
            (29, 29, 4),
            (100, 102, 13),
            (200, 0, 0),
        )

        for (amount, result_amount, utxo_count) in test_list:
            # noinspection PyProtectedMember
            l, a = self._coin.TxFactory._findOptimalUtxoList(
                address.utxoList,
                amount)
            self.assertEqual(utxo_count, len(l))
            self.assertEqual(result_amount, a)

        amount_list = list(range(1, 10))
        shuffle(amount_list)
        self._createUtxoList(address, amount_list)
        self.assertEqual(9, len(address.utxoList))

        test_list = (
            (9, 9, 1),
            (10, 11, 2),
            (20, 21, 3),
            (45, 45, 9),
        )

        for (amount, result_amount, utxo_count) in test_list:
            # noinspection PyProtectedMember
            l, a = self._coin.TxFactory._findOptimalUtxoList(
                address.utxoList,
                amount)
            self.assertEqual(utxo_count, len(l))
            self.assertEqual(result_amount, a)


class TestMutableTx(TestCase):
    def setUp(self) -> None:
        self._coin = Bitcoin()
        root_node = HdNode.deriveRootNode(urandom(64))
        self.assertIsNotNone(root_node)
        self.assertTrue(self._coin.deriveHdNode(root_node))

    def _createInput(
            self,
            coin: AbstractCoin,
            *,
            name: str,
            index: int,
            private_key: str,
            address_type: AbstractCoin.Address.Type,
            script_type: AbstractCoin.Script.Type,
            amount: int,
            sequence: int) -> AbstractCoin.TxFactory.MutableTx.Input:
        private_key = coin.Address.importKey(coin, private_key)
        self.assertIsNotNone(private_key)

        address = coin.Address.createAddress(
            self._coin,
            type_=address_type,
            key=private_key)
        self.assertIsNotNone(address)

        utxo = coin.Tx.Utxo(
            coin,
            name=bytes.fromhex(name)[::-1].hex(),
            height=1,
            index=index,
            amount=amount,
            script_type=script_type)
        utxo.address = address
        return coin.TxFactory.MutableTx.Input(utxo, sequence=sequence)

    @classmethod
    def _createOutput(
            cls,
            coin: AbstractCoin,
            *,
            address_name: str,
            address_type: AbstractCoin.Address.Type,
            amount: int) -> AbstractCoin.TxFactory.MutableTx.Output:
        address = coin.Address(
            coin,
            name=address_name,
            type_=address_type)
        return coin.TxFactory.MutableTx.Output(address, amount)

    def test_p2pkh(self) -> None:
        input_list = [
            self._createInput(
                self._coin,
                name="8878399d83ec25c627cfbf753ff9ca3602373eac437ab2676154a3c2da23adf3", # noqa
                index=1,
                private_key="L3jsepcttyuJK3HKezD4qqRKGtwc8d2d1Nw6vsoPDX9cMcUxqqMv", # noqa
                # noqa
                address_type=self._coin.Address.Type.PUBKEY_HASH,
                script_type=self._coin.Script.Type.P2PKH,
                amount=83727960,
                sequence=0xfffffffe),
        ]
        output_list = [
            self._createOutput(
                self._coin,
                address_name="1N8QYQNAD8PLEJjmCGGR8iN1iuR9yXtY1x",  # noqa
                address_type=self._coin.Address.Type.PUBKEY_HASH,
                amount=50000
            ),
            self._createOutput(
                self._coin,
                address_name="1ELReFsTCUY2mfaDTy32qxYiT49z786eFg",  # noqa
                address_type=self._coin.Address.Type.PUBKEY_HASH,
                amount=83658760
            )
        ]
        mtx = self._coin.TxFactory.MutableTx(
            self._coin,
            input_list,
            output_list)
        self.assertTrue(mtx.sign())
        self.assertEqual(
            "b8eab75158fc3f3bd8479005a02eef5a13c5d80e364ab155a4ebdb19d418b331",  # noqa
            mtx.name)
        self.assertEqual(
            "01000000018878399d83ec25c627cfbf753ff9ca3602373eac437ab2676154a3c2"  # noqa
            "da23adf3010000006b483045022100b167dd5c560454a8c7e6425aebde64723311"  # noqa
            "0158acf84b1b81a9ed98b2c613a20220551d562999009596a0c1c12b2a77861cc9"  # noqa
            "150bc77c025ed5309ff77d39bc889f0121033d5c2875c9bd116875a71a5db64cff"  # noqa
            "cb13396b163d039b1d9327824891804334feffffff0250c30000000000001976a9"  # noqa
            "14e7c1345fc8f87c68170b3aa798a956c2fe6a9eff88ac0888fc04000000001976"  # noqa
            "a91492461bde6283b461ece7ddf4dbf1e0a48bd113d888ac00000000",  # noqa
            mtx.serialize().hex())

    # https://github.com/bitcoin/bips/blob/master/bip-0143.mediawiki#native-p2wpkh
    def test_native_p2wpkh(self) -> None:
        input_list = [
            self._createInput(
                self._coin,
                name="fff7f7881a8099afa6940d42d1e7f6362bec38171ea3edf433541db4e4ad969f",  # noqa
                index=0,
                private_key="bbc27228ddcb9209d7fd6f36b02f7dfa6252af40bb2f1cbc7a557da8027ff866",  # noqa
                address_type=self._coin.Address.Type.PUBKEY_HASH,
                script_type=self._coin.Script.Type.P2PK,
                amount=625000000,
                sequence=0xffffffee),
            self._createInput(
                self._coin,
                name="ef51e1b804cc89d182d279655c3aa89e815b1b309fe287d9b2b55d57b90ec68a",  # noqa
                index=1,
                private_key="619c335025c7f4012e556c2a58b2506e30b8511b53ade95ea316fd8c3286feb9",  # noqa
                address_type=self._coin.Address.Type.WITNESS_V0_KEY_HASH,
                script_type=self._coin.Script.Type.P2WPKH,
                amount=600000000,
                sequence=0xffffffff),
        ]
        output_list = [
            self._createOutput(
                self._coin,
                address_name="1Cu32FVupVCgHkMMRJdYJugxwo2Aprgk7H",  # noqa
                address_type=self._coin.Address.Type.PUBKEY_HASH,
                amount=112340000
            ),
            self._createOutput(
                self._coin,
                address_name="16TZ8J6Q5iZKBWizWzFAYnrsaox5Z5aBRV",  # noqa
                address_type=self._coin.Address.Type.PUBKEY_HASH,
                amount=223450000)
        ]

        mtx = self._coin.TxFactory.MutableTx(
            self._coin,
            input_list,
            output_list,
            lock_time=0x11)
        self.assertTrue(mtx.sign())
        self.assertEqual(
            "e8151a2af31c368a35053ddd4bdb285a8595c769a3ad83e0fa02314a602d4609",  # noqa
            mtx.name)

        self.assertEqual(
            "01000000000102fff7f7881a8099afa6940d42d1e7f6362bec38171ea3edf43354"  # noqa
            "1db4e4ad969f00000000494830450221008b9d1dc26ba6a9cb62127b02742fa9d7"  # noqa
            "54cd3bebf337f7a55d114c8e5cdd30be022040529b194ba3f9281a99f2b1c0a19c"  # noqa
            "0489bc22ede944ccf4ecbab4cc618ef3ed01eeffffffef51e1b804cc89d182d279"  # noqa
            "655c3aa89e815b1b309fe287d9b2b55d57b90ec68a0100000000ffffffff02202c"  # noqa
            "b206000000001976a9148280b37df378db99f66f85c95a783a76ac7a6d5988ac90"  # noqa
            "93510d000000001976a9143bde42dbee7e4dbe6a21b2d50ce2f0167faa815988ac"  # noqa
            "000247304402203609e17b84f6a7d30c80bfa610b5b4542f32a8a0d5447a12fb13"  # noqa
            "66d7f01cc44a0220573a954c4518331561406f90300e8f3358f51928d43c212a8c"  # noqa
            "aed02de67eebee0121025476c2e83188368da1ff3e292e7acafcdb3566bb0ad253"  # noqa
            "f62fc70f07aeee635711000000",  # noqa
            mtx.serialize().hex())

    # https://github.com/bitcoin/bips/blob/master/bip-0143.mediawiki#p2sh-p2wpkh
    def test_p2sh_p2wpkh(self) -> None:
        input_list = [
            self._createInput(
                self._coin,
                name="db6b1b20aa0fd7b23880be2ecbd4a98130974cf4748fb66092ac4d3ceb1a5477",  # noqa
                index=1,
                private_key="eb696a065ef48a2192da5b28b694f87544b30fae8327c4510137a922f32c6dcf",  # noqa
                address_type=self._coin.Address.Type.WITNESS_V0_KEY_HASH,
                script_type=self._coin.Script.Type.P2SH_P2WPKH,
                amount=1000000000,
                sequence=0xfffffffe),
        ]
        output_list = [
            self._createOutput(
                self._coin,
                address_name="1Fyxts6r24DpEieygQiNnWxUdb18ANa5p7",  # noqa
                address_type=self._coin.Address.Type.PUBKEY_HASH,
                amount=199996600),
            self._createOutput(
                self._coin,
                address_name="1Q5YjKVj5yQWHBBsyEBamkfph3cA6G9KK8",  # noqa
                address_type=self._coin.Address.Type.PUBKEY_HASH,
                amount=800000000)
        ]

        mtx = self._coin.TxFactory.MutableTx(
            self._coin,
            input_list,
            output_list,
            lock_time=0x492)
        self.assertTrue(mtx.sign())
        self.assertEqual(
            "ef48d9d0f595052e0f8cdcf825f7a5e50b6a388a81f206f3f4846e5ecd7a0c23",  # noqa
            mtx.name)

        self.assertEqual(
            "01000000000101db6b1b20aa0fd7b23880be2ecbd4a98130974cf4748fb66092ac"  # noqa
            "4d3ceb1a5477010000001716001479091972186c449eb1ded22b78e40d009bdf00"  # noqa
            "89feffffff02b8b4eb0b000000001976a914a457b684d7f0d539a46a45bbc043f3"  # noqa
            "5b59d0d96388ac0008af2f000000001976a914fd270b1ee6abcaea97fea7ad0402"  # noqa
            "e8bd8ad6d77c88ac02473044022047ac8e878352d3ebbde1c94ce3a10d057c2417"  # noqa
            "5747116f8288e5d794d12d482f0220217f36a485cae903c713331d877c1f64677e"  # noqa
            "3622ad4010726870540656fe9dcb012103ad1d8e89212f0b92c74d23bb710c0066"  # noqa
            "2ad1470198ac48c43f7d6f93a2a2687392040000",
            mtx.serialize().hex())
