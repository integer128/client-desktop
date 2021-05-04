# JOK4
from __future__ import annotations

from typing import Type, TYPE_CHECKING

from PySide2.QtCore import QObject

from ..config import UserConfig
from ..utils.meta import classproperty
from ..utils.static_list import UserStaticList

if TYPE_CHECKING:
    from typing import Final, Optional
    from ..application import CoreApplication
    from ..language import Locale


class AbstractCurrency:
    _DECIMAL_SIZE = (0, 0)
    _VALUE_BITS = 63  # int64
    _NAME = "YYY"
    _UNIT = "YYY"
    __string_template: Optional[str] = None

    def __init__(self) -> None:
        raise Exception(
            "__init__ disabled for class {}".format(self.__class__.__name__))

    @classproperty
    def name(cls) -> str: # noqa
        return cls._NAME

    @classproperty
    def unit(cls) -> str: # noqa
        return cls._UNIT

    @classproperty
    def decimalSize(cls) -> int: # noqa
        return cls._DECIMAL_SIZE[1]

    @classproperty
    def decimalDivisor(cls) -> int: # noqa
        return 10 ** cls._DECIMAL_SIZE[1]

    @classproperty
    def stringTemplate(cls) -> str: # noqa
        if not cls.__string_template:
            v = len(cls.toString(2 ** cls._VALUE_BITS - 1))
            assert v > 2
            cls.__string_template = "8" * (v + v // 3 - 1)
        return cls.__string_template

    @classmethod
    def isValidValue(cls, value: int) -> bool:
        b = 2 ** cls._VALUE_BITS
        return -b <= value <= (b - 1)

    @classmethod
    def fromString(
            cls,
            source: str,
            *,
            strict: bool = True,
            locale: Optional[Locale] = None) -> Optional[int]:
        if not source:
            return None

        sign = False
        if (
                source[0] == "-" or
                (locale and source[0] == locale.negativeSign())
        ):
            sign = True
            source = source[1:]
        elif (
                source[0] == "+" or
                (locale and source[0] == locale.positiveSign())
        ):
            source = source[1:]

        a = source.rsplit(locale.decimalPoint() if locale else ".")
        if len(a) == 1:
            b = ""
            a = a[0]
        elif len(a) == 2:
            b = a[1]
            a = a[0]
        else:
            return None
        if not a and not b:
            return None

        result = 0
        if a:
            if locale:
                if not strict:
                    a = a.replace(locale.groupSeparator(), '')
                a = locale.stringToInteger(a)
            elif a.isalnum():
                try:
                    a = int(a, base=10)
                except ValueError:
                    a = None
            else:
                a = None
            if a is None or a < 0:
                return None
            result = (-a if sign else a) * cls.decimalDivisor

        if b:
            b_length = len(b)
            if b_length > cls._DECIMAL_SIZE[1]:
                return None
            if b.isalnum():
                try:
                    b = int(b, base=10)
                except ValueError:
                    b = None
            else:
                b = None
            if b is None or b < 0 or b >= cls.decimalDivisor:
                return None
            for _ in range(b_length, cls._DECIMAL_SIZE[1]):
                b *= 10
            result += (-b if sign else b)

        if not cls.isValidValue(result):
            return None
        return result

    @classmethod
    def toString(
            cls,
            value: int,
            *,
            locale: Optional[Locale] = None) -> str:
        if not value or not cls.isValidValue(value):
            return "0"
        if value < 0:
            value = abs(value)
            result = locale.negativeSign() if locale else "-"
        else:
            result = ""

        a, b = divmod(value, cls.decimalDivisor)

        zero_count = 0
        while b and b % 10 == 0:
            b //= 10
            zero_count += 1

        result += locale.integerToString(a) if locale else str(a)
        if b:
            b = str(b)
            zero_count = cls._DECIMAL_SIZE[1] - len(b) - zero_count
            result += locale.decimalPoint() if locale else "."
            result += "0" * zero_count + b

            zero_count += len(b)
            if zero_count < cls._DECIMAL_SIZE[0]:
                result += "0" * (cls._DECIMAL_SIZE[0] - zero_count)

        return result


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


class FiatCurrencyList(UserStaticList):
    ItemType = Type[FiatCurrency]

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
            self._list[self._current_index].unit)


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
