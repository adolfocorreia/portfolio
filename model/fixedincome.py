# Original: https://github.com/wilsonfreitas/python-fixedincome

import re
from abc import ABC, abstractmethod
from datetime import date, datetime
from math import exp, pow
from typing import Callable, override

from bizdays import Calendar  # pyright: ignore[reportMissingTypeStubs]


class Frequency:
    # Frequency to time unit mapping
    _units: dict[str, str] = {
        # adjective: noun
        "annual": "year",
        "semi-annual": "half-year",
        "quarterly": "quarter",
        "monthly": "month",
        "daily": "day",
    }
    names: tuple[str, ...] = tuple(_units.keys())
    time_units: tuple[str, ...] = tuple(_units.values())

    def __init__(self, name: str):
        if name not in self.names:
            raise Exception("Invalid frequency: %s" % name)
        self._name: str = name

    @override
    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Frequency):
            return False
        return self._name == other._name

    @override
    def __repr__(self) -> str:
        return f"{self.__class__!r}({self.__dict__!r})"

    @property
    def name(self):
        return self._name

    def unit(self) -> str:
        return self._units[self.name]


type Compounder = Callable[[float, float], float]


class Compounding:
    @staticmethod
    def simple(r: float, t: float) -> float:
        return 1.0 + r * t

    @staticmethod
    def exponential(r: float, t: float) -> float:
        return pow(1.0 + r, t)

    @staticmethod
    def continuous(r: float, t: float) -> float:
        return exp(r * t)

    _funcs: dict[str, Compounder] = {
        "simple": simple,
        "exponential": exponential,
        "continuous": continuous,
    }

    names: tuple[str, ...] = tuple(_funcs.keys())

    def __init__(self, name: str):
        if name not in self.names:
            raise Exception("Invalid compounding: %s" % name)
        self._name: str = name

    def __call__(self, r: float, t: float) -> float:
        return self._funcs[self.name](r, t)

    @override
    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Compounding):
            return False
        return self.name == other.name

    @property
    def name(self):
        return self._name


class GenericPeriod(ABC):
    """
    This class accommodates methods for time computing.
    """

    def __init__(self, unit: str):
        self.unit: str = unit

    @abstractmethod
    def size(self) -> float:
        pass

    @override
    def __str__(self):
        return "{:.1f} {}{}".format(self.size(), self.unit, ("", "s")[self.size() > 1])

    @override
    def __repr__(self) -> str:
        return f"{self.__class__!r}({self.__dict__!r})"


class FixedTimePeriod(GenericPeriod):
    """
    Examples:
    period('1 year')
    period('1 half-year')
    period('1 quarter')
    period('1 month')
    period('1 day')
    """

    def __init__(self, size: float, unit: str):
        super().__init__(unit)
        self._size: float = size

    @override
    def size(self) -> float:
        """Return the quantity related to the fixed period."""
        return self._size


class DateRangePeriod(GenericPeriod):
    """
    Examples:
    d1 = "2012-07-12"
    d2 = "2012-07-27"
    period((d1, d2))
    period('2012-07-12:2012-07-16')

    For now, we can consider only the *day* time unit, but we should be completely
    open to other time units such as *month* and *year* or even *quarter*.
    For example:
    period('2012-04:2012-12') -> from April 2012 to December 2012: 9 months
    period('2012:2012') -> from 2012 to 2012: 1 year
    period('2012-1:2012-3') -> from 2012 first quarter to 2012 third one: 3 quarters

    I still don't know how to handle that!

    This procedure includes starting and ending points.
    """

    def __init__(self, dates: list[date], unit: str = "day"):
        assert all(isinstance(d, date) and not isinstance(d, datetime) for d in dates)
        super().__init__(unit)
        if dates[0] > dates[1]:
            raise Exception(
                "Invalid period: the starting date must be greater than the ending date."
            )
        self.dates: list[date] = dates

    @override
    def size(self) -> float:
        """Return the total amount of days between two dates"""
        return (self.dates[1] - self.dates[0]).days


class CalendarRangePeriod(DateRangePeriod):
    """
    A CalendarRangePeriod is a DateRangePeriod which uses a Calendar to
    compute the amount of days contained into the underlying period.
    """

    def __init__(self, period: DateRangePeriod, calendar: Calendar):
        super().__init__(period.dates, unit="day")
        self.calendar: Calendar = calendar

    @override
    def size(self) -> float:
        """Return the amount of working days into period."""
        d1 = self.dates[0].isoformat()
        d2 = self.dates[1].isoformat()
        days = self.calendar.bizdays(  # pyright: ignore[reportUnknownMemberType, reportUnknownVariableType]
            d1, d2
        )
        assert isinstance(days, int)
        return float(days)


class DayCount:
    """
    DayCount conventions.

    References:
    - https://en.wikipedia.org/wiki/Day_count_convention
    - https://www.eclipsesoftware.biz/DayCountConventions.html
    - https://strata.opengamma.io/day_counts
    - https://www.quantlib.org/reference/group__daycounters.html
    - https://felipenoris.github.io/InterestRates.jl

    Implementation references:
    - https://github.com/OpenGamma/Strata/blob/main/modules/basics/src/main/java/com/opengamma/strata/basics/date/StandardDayCounts.java
    - https://github.com/OpenGamma/Strata/blob/main/modules/basics/src/main/java/com/opengamma/strata/basics/date/Business252DayCount.java
    - https://github.com/OpenGamma/Strata/blob/main/modules/basics/src/test/java/com/opengamma/strata/basics/date/DayCountTest.java
    - https://github.com/OpenGamma/Strata/blob/main/modules/basics/src/test/java/com/opengamma/strata/basics/date/Business252DayCountTest.java
    """

    # TODO: test implementation of each convention
    _day_counts: dict[str, int] = {
        "30/360": -1,
        "30/360 US": -1,
        "30E/360 ISDA": -1,
        "30E+/360": -1,
        "actual/365": 365,
        "actual/360": 360,
        "actual/364": 364,
        "actual/365L": 365,
        "business/252": 252,
    }
    names: tuple[str, ...] = tuple(_day_counts.keys())

    def __init__(self, dc: str):
        if dc not in self.names:
            raise Exception("Invalid day count: %s" % dc)
        self._name: str = dc
        self._day_count: str = dc
        self._days_in_base: int = self._day_counts[dc]
        self._unit_size: dict[str, int] = {  # frequency multiplier
            "year": 1,
            "half-year": 2,
            "quarter": 4,
            "month": 12,
            "day": self._days_in_base,
        }
        self._unit_convert: dict[str, dict[str, float]] = {
            "year": {
                "day": self._days_in_base,
                "month": 12.0,
                "quarter": 4.0,
                "half-year": 2.0,
                "year": 1.0,
            },
            "half-year": {
                "day": self._days_in_base / 2.0,
                "month": 6.0,
                "quarter": 2.0,
                "half-year": 1.0,
                "year": 0.5,
            },
            "quarter": {
                "day": self._days_in_base / 4.0,
                "month": 3.0,
                "quarter": 1.0,
                "half-year": 0.5,
                "year": 1.0 / 4.0,
            },
            "month": {
                "day": self._days_in_base / 12.0,
                "month": 1.0,
                "quarter": 3.0,
                "half-year": 6.0,
                "year": 12.0,
            },
            "day": {
                "day": 1.0,
                "month": 12.0 / self._days_in_base,
                "quarter": 4.0 / self._days_in_base,
                "half-year": 2.0 / self._days_in_base,
                "year": 1.0 / self._days_in_base,
            },
        }

    @property
    def days_in_base(self):
        return self._days_in_base

    @property
    def name(self):
        return self._name

    @override
    def __eq__(self, other: object) -> bool:
        if not isinstance(other, DayCount):
            return False
        return self._day_count == other._day_count

    def in_unit(self, period: GenericPeriod, unit: str) -> float:
        """
        Returns the size of the period converted to the given unit.
        """
        return period.size() * self._unit_convert[period.unit][unit]

    def day(self, period: GenericPeriod) -> float:
        """
        Returns the size of the period converted to the given unit.
        """
        return period.size() * self._unit_convert[period.unit]["day"]

    def month(self, period: GenericPeriod) -> float:
        """
        Returns the size of the period converted to the given unit.
        """
        return period.size() * self._unit_convert[period.unit]["month"]

    def quarter(self, period: GenericPeriod) -> float:
        """
        Returns the size of the period converted to the given unit.
        """
        return period.size() * self._unit_convert[period.unit]["quarter"]

    def half_year(self, period: GenericPeriod) -> float:
        """
        Returns the size of the period converted to the given unit.
        """
        return period.size() * self._unit_convert[period.unit]["half-year"]

    def year(self, period: GenericPeriod) -> float:
        """
        Returns the size of the period converted to the given unit.
        """
        return period.size() * self._unit_convert[period.unit]["year"]

    def days_in_unit(self, unit: str) -> float:
        """
        Returns the amount of days in base, for a given time
        unit (year, month, day, ...). For example, the business/252 day count
        rule has 252 days in base, so if you have a period of time with a time
        unit of month then you use 21 days for each month.
        """
        return float(self.days_in_base) / self.unit_size(unit)

    def unit_size(self, unit: str) -> float:
        """
        Returns the amount of time for one year related to a unit and
        to this day count rule.
        """
        return self._unit_size[unit]

    def time_factor(self, period: GenericPeriod) -> float:
        """
        Returns a year fraction regarding period definition.
        This function always returns year's fraction.
        """
        days = period.size() * self.days_in_unit(period.unit)
        return float(days) / self.days_in_base

    def time_freq(self, period: GenericPeriod, frequency: Frequency) -> float:
        """
        Returns the amount of time contained into the period adjusted
        to the given frequency.
        """
        tf = self.time_factor(period)
        return tf * self.unit_size(frequency.unit())


class InterestRate:
    """
    This class receives a calendar instance in its constructor's parameter list
    because in some cases it's fairly common to user provide that information.
    Despite having a default calendar set either into the system or for a
    given market, we are likely to handle the situation where interest rate
    has its own calendar and that calendar must be used to discount the
    cashflows.
    """

    # TODO: write conversion functions: given other settings, generate a different rate
    def __init__(
        self,
        rate: float,
        frequency: Frequency,
        compounding: Compounding,
        day_count: DayCount,
        calendar: Calendar | None = None,
    ):
        self.rate: float = rate
        self.frequency: Frequency = frequency
        self.compounding: Compounding = compounding
        self.day_count: DayCount = day_count
        self.calendar: Calendar | None = calendar
        if self.calendar and not self.day_count.name.startswith("business"):
            raise Exception("%s DayCount cannot accept calendar" % self.day_count.name)

    def discount(self, period: DateRangePeriod) -> float:
        """Return the discount factor"""
        return 1.0 / self.compound(period)

    def compound(self, period: DateRangePeriod) -> float:
        """Return the compounding factor"""
        if self.calendar:
            period = CalendarRangePeriod(period, self.calendar)

        t = self.day_count.time_freq(period, self.frequency)
        return self.compounding(self.rate, t)

    @override
    def __repr__(self) -> str:
        return f"{self.__class__!r}({self.__dict__!r})"


def ir(ir_spec: str) -> InterestRate:
    """
    Return a InterestRate object for a given interest rate specification.
    The interest rate specification is a string like:

    '0.06 annual simple actual/365'
    '0.09 annual exponential business/252 calANBIMA'
    '0.06 annual continuous 30/360'

    The specification must contain all information required to instantiate a
    InterestRate object. The InterestRate constructor requires:
    - rate
    - frequency
    - compounding
    - day count
    and depending on which day count is used the calendar must be set. Otherwise,
    it defaults to None.
    """
    rate = frequency = compounding = day_count = calendar = None
    tokens = ir_spec.split()
    for tok in tokens:
        m = re.match(r"^(\d+)(\.\d+)?$", tok)
        if m:
            rate = float(m.group())
        elif tok in Compounding.names:
            compounding = Compounding(tok)
        elif tok in DayCount.names:
            day_count = DayCount(tok)
        elif tok in Frequency.names:
            frequency = Frequency(tok)
        elif tok.startswith("cal"):
            calendar = Calendar.load(  # pyright: ignore[reportUnknownMemberType]
                name=tok.replace("cal", "")
            )

    assert rate is not None
    assert frequency is not None
    assert compounding is not None
    assert day_count is not None

    return InterestRate(rate, frequency, compounding, day_count, calendar)


def compound(ir: InterestRate, period: DateRangePeriod) -> float:
    """
    Return the compounding factor regarding an interest rate and a period.
    """
    return ir.compound(period)


def discount(ir: InterestRate, period: DateRangePeriod) -> float:
    """
    Return the discount factor regarding an interest rate and a period.
    """
    return ir.discount(period)


def period(pspec: str) -> GenericPeriod:
    """
    Return a FixedTimePeriod or a DateRangePeriod instance, depending on the
    period specification string passed.

    # FixedTimePeriod
    p = period('15 days')
    p = period('1 month')
    p = period('2.5 months')
    p = period('22.55 months')
    p = period('1.5 years')
    p = period('1.5 quarters')

    # DateRangePeriod
    p = period('2012-07-12:2012-07-16')
    p = period('2012-07-12:2012-07-22')
    """
    start = end = None
    w = "|".join(Frequency.time_units)
    m = re.match(r"^(\d+)(\.\d+)? (%s)s?$" % w, pspec)
    if m:
        is_time_range = False
    elif len(pspec.split(":")) == 2:
        (start, end) = pspec.split(":")
        is_time_range = True
    else:
        raise Exception("Invalid period specification")

    if is_time_range:
        assert start is not None
        assert end is not None
        dates = [
            datetime.strptime(start, "%Y-%m-%d").date(),
            datetime.strptime(end, "%Y-%m-%d").date(),
        ]
        return DateRangePeriod(dates, "day")
    else:
        assert m is not None
        g = m.groups()
        return FixedTimePeriod(float(g[0] + (g[1] or ".0")), g[2])
