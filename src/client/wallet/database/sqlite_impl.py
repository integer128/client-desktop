
import logging
from typing import Any
import threading
import hashlib
import struct
import base64
import binascii
import sys
import sqlite3 as sql
from ... import meta
from . import encrypt_proxy

log = logging.getLogger(__name__)


class Connection (sql.Connection):
    pass


class DummyCursor:
    def close(self) -> None:
        pass


class SqLite:
    """
    To encrypt sqlite we use hashing for names and aes for data
    but consider using native convertors
    * sqlite3.register_converter(typename, callable)
    * sqlite3.register_adapter(type, callable)
    """
    """
    TABLES:
        * meta
            - id , key , value
        * coins
            - id , name, visible, height , \
                offset, \
                unverified_offset, unverified_signature, verified_height \
                rate_usd
        * wallets
            # we keep both offsets otherwise we loose old tansactions in case user breaks servert tx chain
            - id , address, coin_id , label , message , created , type, balance , tx_count , \
                first_offset, last_offset, \
                key
        * transactions
            # status - detectable field
            - id , name , wallet_id , height , time , amount , fee ,  status , receiver , target
        * inputs (outputs also here )
            - id , address , tx_id , amount , type ( 0 - input , 1 - output )
    """

    # i still need it.. it's hard to distinguish encoded columns
    COLUMN_NAMES = [
        "key",
        "value",
        "name",
        "visible",
        "address",
        "label",
        "message",
        "created",
        "coin_id",
        "type",
        "balance",
        "tx_count",
        "offset",
        "unverified_offset",
        "unverified_signature",
        "verified_height",
        "first_offset",
        "last_offset",
        "key",
        "height",
        "status",
        "time",
        "amount",
        "fee",
        "wallet_id",
        "tx_id",
        "type",
        "rate_usd",
        "receiver",
        "target",
    ]
    TABLE_NAMES = [
        "meta",
        "coins",
        "private_keys",
        "coins",
        "wallets",
        "transactions",
        "inputs",
    ]
    DEBUG = True

    def __init__(self, parent):
        # dont' touch !!
        if parent is None:
            super().__init__()
        self._query_count = 0
        self._mutex = threading.Lock()
        self._conn = None
        self._proxy = None

    def connect_impl(self, db_name: str, password: str, nonce: bytes) -> None:
        self._proxy = encrypt_proxy.EncryptProxy(password,nonce)
        self._conn = sql.connect(
            db_name,
            timeout=3,
            # detect_types=sql.PARSE_DECLTYPES,
            detect_types=sql.PARSE_COLNAMES,
            check_same_thread=True,
            cached_statements=100,
            # factory=Connection,
        )
        self._exec_("PRAGMA foreign_keys=ON")
        sql.enable_callback_tracebacks(self.DEBUG)
        self._conn.text_factory = self._proxy.text_from

    def _exec_script(self, query) -> None:
        try:
            cursor = self._conn.cursor()
            cursor.executescript(query)
            self._conn.commit()
            +self
            return cursor
        except sql.OperationalError as oe:
            log.fatal(f'SQL exception {oe} in {query}')
            sys.exit(1)

    def _exec_(self, query: str, *args) -> None:
        if self._conn is None:
            return DummyCursor()
        try:
            cursor = self._conn.cursor()
            cursor.execute(query, *args)
            self._conn.commit()
            +self
            return cursor
        except sql.OperationalError as oe:
            log.warning(f'SQL exception {oe} in {query}')
            raise oe from oe

    def _exec_many(self, query: str, *args) -> None:
        try:
            cursor = self._conn.cursor()
            cursor.executemany(query, *args)
            self._conn.commit()
            +self
            return cursor
        except sql.OperationalError as oe:
            log.fatal(f'SQL exception {oe} in {query}')
            sys.exit(1)

    def create_tables(self) -> None:
        integer = "TEXT" if encrypt_proxy.EncryptProxy.ENCRYPT else "INTEGER"
        real = "TEXT" if encrypt_proxy.EncryptProxy.ENCRYPT else "REAL"
        query = f"""
        CREATE TABLE IF NOT EXISTS {self.meta_table}
            (id INTEGER PRIMARY KEY,
            {self.key_column}   TEXT NOT NULL UNIQUE,
            {self.value_column} TEXT
            );
        CREATE TABLE IF NOT EXISTS {self.coins_table}
            (id INTEGER PRIMARY KEY ,
            {self.name_column}  TEXT NOT NULL UNIQUE,
            {self.visible_column}       {integer} ,
            {self.height_column}        {integer} ,
            {self.verified_height_column}        {integer},
            {self.offset_column}        TEXT,
            {self.unverified_offset_column}        TEXT,
            {self.unverified_signature_column}        TEXT,
            {self.rate_usd_column}      {real}
            );
        CREATE TABLE IF NOT EXISTS {self.wallets_table}
            (id INTEGER PRIMARY KEY,
            {self.address_column}   TEXT NOT NULL,
            {self.coin_id_column}   {integer} NOT NULL,
            {self.label_column}     TEXT,
            {self.message_column}     TEXT,
            {self.created_column}     {integer} NOT NULL,
            {self.type_column}      {integer} NOT NULL,
            {self.balance_column}   {integer},
            {self.tx_count_column}  {integer},
            {self.first_offset_column}      TEXT,
            {self.last_offset_column}       TEXT,
            {self.key_column}       TEXT,
            FOREIGN KEY ({self.coin_id_column}) REFERENCES {self.coins_table} (id) ON DELETE CASCADE,
            UNIQUE({self.address_column}, {self.coin_id_column})
            );
        CREATE TABLE IF NOT EXISTS {self.transactions_table}
            (id INTEGER PRIMARY KEY,
            {self.name_column}   TEXT NOT NULL,
            {self.wallet_id_column} {integer} NOT NULL,
            {self.height_column} {integer} NOT NULL,
            {self.time_column}   {integer} NOT NULL,
            {self.amount_column} {integer} NOT NULL,
            {self.fee_column}    {integer} NOT NULL,
            {self.status_column}    {integer} NOT NULL,
            {self.receiver_column}    TEXT,
            {self.target_column}    TEXT,
            FOREIGN KEY ({self.wallet_id_column}) REFERENCES {self.wallets_table} (id) ON DELETE CASCADE,
            UNIQUE({self.name_column}, {self.wallet_id_column})
            );
        CREATE TABLE IF NOT EXISTS {self.inputs_table} (id INTEGER PRIMARY KEY,
            {self.address_column}   TEXT NOT NULL,
            {self.tx_id_column}     {integer} NOT NULL,
            {self.amount_column}    {integer} NOT NULL,
            {self.type_column}      {integer} NOT NULL,
            FOREIGN KEY ({self.tx_id_column}) REFERENCES {self.transactions_table} (id) ON DELETE CASCADE
            );
        """
        c = self._exec_script(query)
        c.close()

    def test_table(self, table_name: str) -> bool:
        enc_table_name = self._make_title(table_name)
        query = f'''
        SELECT name FROM sqlite_master WHERE name='{enc_table_name}';
        '''
        c = self._exec_(query)
        recs = c.fetchall()
        c.close()
        return recs is not None

    def _make_title(self, name: str) -> str:
        if encrypt_proxy.EncryptProxy.ENCRYPT:
            if not self._proxy:
                return "-"
            return meta.setdefaultattr(
                self,
                name + "_title_",
                # may be slow
                # f"_{base64.b32encode(hashlib.new('ripemd160', (name + self._aes.password).encode()).digest())}",
                # too long
                # f"_{hashlib.new('ripemd160', (name + self._aes.password).encode()).hexdigest()}",
                # f"_{hashlib.md5(name.encode()).hexdigest()}",
                f"_{self._proxy.make_hash(name)}",
            )
        return name

    def __getattr__(self, attr: str) -> str:
        if attr.endswith("_column"):
            if attr[:-7] in self.COLUMN_NAMES:
                return self._make_title(attr[:-7])
        elif attr.endswith("_table"):
            if attr[:-6] in self.TABLE_NAMES:
                return self._make_title(attr[:-6])
        else:
            raise AttributeError(attr)
        raise AttributeError(f"Bad table or column:{attr}.")

    def __call__(self, data: Any, strong: bool = False, key: str = None):
        """
        key for debugging only!
        """
        if not self._proxy:
            return "-"
        # if key:
            # log.debug(f"encrypt {key} strong:{strong}")
        return self._proxy.encrypt(data, strong)

    def __pos__(self):
        # TODO: i feel like this stuff is redundant. I supposed there is similiar stuff in python/sqlite module
        with self._mutex:
            self._query_count += 1

    @property
    def query_count(self) -> int:
        with self._mutex:
            return self._query_count
