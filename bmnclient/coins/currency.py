# JOK4
from __future__ import annotations

from typing import TYPE_CHECKING

from PySide2.QtCore import QObject

from .abstract.currency import AbstractCurrency
from ..config import UserConfig, UserConfigStaticList

if TYPE_CHECKING:
    from typing import Final, Iterator, Optional, Type, Union
    from ..application import CoreApplication


class FiatCurrency(AbstractCurrency):
    _DECIMAL_SIZE = (2, 2)


class NoneFiatCurrency(FiatCurrency):
    _NAME: Final = QObject().tr("-- None --")
    _UNIT: Final = "N/A"


class UsdFiatCurrency(FiatCurrency):
    _NAME: Final = QObject().tr("US Dollar")
    _UNIT: Final = "USD"


class EuroFiatCurrency(FiatCurrency):
    _NAME: Final = QObject().tr("Euro")
    _UNIT: Final = "EUR"


class FiatCurrencyList(UserConfigStaticList):
    def __init__(self, application: CoreApplication) -> None:
        super().__init__(
            application.userConfig,
            UserConfig.KEY_SERVICES_FIAT_CURRENCY,
            (
                UsdFiatCurrency,
                EuroFiatCurrency
            ),
            default_index=0,
            item_property="unit")
        self._logger.debug(
            "Current fiat currency is \"%s\".",
            self.current.unit)

    def __iter__(self) -> Iterator[Type[FiatCurrency]]:
        return super().__iter__()

    def __getitem__(
            self,
            value: Union[str, int]) -> Optional[Type[FiatCurrency]]:
        return super().__getitem__(value)

    @property
    def current(self) -> Type[FiatCurrency]:
        return super().current


class FiatRate:
    def __init__(self, value: int, currency: Type[FiatCurrency]) -> None:
        self._value = value
        self._currency = currency

    @property
    def value(self) -> int:
        return self._value

    @property
    def currency(self) -> Type[FiatCurrency]:
        return self._currency
