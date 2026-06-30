from datetime import date, datetime

import pandas as pd
import QuantLib as ql

import retriever

# Reference: https://www.wilsonfreitas.net/posts/2023-07-26-quantlib-zerocurve/main


class Curve:
    def __init__(self, code: str, base_date: str | date):
        if isinstance(base_date, str):
            base_date = datetime.strptime(base_date, "%Y-%m-%d").date()
        assert isinstance(base_date, date)
        self.code = code
        self.base_date = base_date

        curve_retriever = retriever.get_curve_retriever()
        df: pd.DataFrame = curve_retriever.get_curve_vertices(self.code, self.base_date)

        dates = list(df["forward_date"].map(lambda d: ql.Date().from_date(d)))
        rates = list(df["rate"])

        # TODO: understand QuantLib curve interpolations better

        # In QuantLib, ZeroCurves only support linear interpolations.  In particular, note that
        # the LogLinearZeroCurve is deprecated because of this limitation.  To use log-linear
        # interpolations, a DiscountCurve must be used.  Here we convert the zero rates into the
        # corresponding discount factors before feeding them into the curve constructor.

        # Brazilian banking holidays calendar (federal holidays plus carnival)
        calendar = ql.Brazil(ql.Brazil.Settlement)
        self.day_counter = ql.Business252(calendar)
        self.compounding = ql.Compounded
        frequency = ql.Annual

        base_date = ql.Date().from_date(base_date)
        discount_factors = list()
        for day, rate in zip(dates, rates):
            interest_rate = ql.InterestRate(
                rate, self.day_counter, self.compounding, frequency
            )
            discount_factor = interest_rate.discountFactor(base_date, day)
            discount_factors.append(discount_factor)

        # QuantLib requires the first discount factor to be equal to 1.0 in order to flag the base date
        dates.insert(0, base_date)
        discount_factors.insert(0, 1.0)

        interpolator = ql.LogLinear()
        self.ql_curve = ql.DiscountCurve(
            dates,
            discount_factors,
            self.day_counter,
            calendar,
            interpolator,
        )

    def get_rate(self, forward_date: str | date) -> float:
        if isinstance(forward_date, str):
            d = ql.Date(forward_date, "%Y-%m-%d")
        elif isinstance(forward_date, date):
            d = ql.Date().from_date(forward_date)
        else:
            assert False
        r = self.ql_curve.zeroRate(d, self.day_counter, self.compounding)
        return r.rate()

    def __repr__(self):
        return f"Curve(code={self.code!r}, base_date={self.base_date:%Y-%m-%d})"
