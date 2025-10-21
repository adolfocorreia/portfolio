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

        dates = df["forward_date"].map(lambda d: ql.Date().from_date(d))
        rates = df["r_252"]
        calendar = ql.Brazil(
            ql.Brazil.Settlement
        )  # Brazilian banking holidays (federal holidays plus carnival)
        interpolator = ql.Linear()
        self.day_counter = ql.Business252(calendar)
        self.compounding = ql.Compounded
        self.ql_curve = ql.ZeroCurve(
            dates, rates, self.day_counter, calendar, interpolator, self.compounding
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
