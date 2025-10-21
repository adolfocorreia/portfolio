from abc import ABC, abstractmethod
from datetime import date, datetime
from typing import override

from bizdays import Calendar
from retriever import get_bcb_retriever
from retriever.retriever import VariationRetriever

from model.fixedincome import DateRangePeriod, InterestRate, ir_over

ANBIMA_CAL = Calendar.load("ANBIMA")


class Indexer:
    def __init__(
        self,
        pre: float = 0.0,
        post: VariationRetriever | None = None,
        percent: float = 1.0,
        code: str | None = None,
    ):
        assert pre != 0.0 or post is not None
        self.pre: InterestRate | None = ir_over(pre) if pre != 0.0 else None
        self.post: VariationRetriever | None = post
        self.percent: float = percent
        self.code: str | None = code

    def get_variation(self, begin_date: str | date, end_date: str | date) -> float:
        if isinstance(begin_date, str):
            begin_date = datetime.strptime(begin_date, "%Y-%m-%d").date()
        if isinstance(end_date, str):
            end_date = datetime.strptime(end_date, "%Y-%m-%d").date()

        days: int = ANBIMA_CAL.bizdays(begin_date, end_date)
        assert days >= 0

        post_factor = 1.0
        if self.post is not None:
            assert self.code is not None
            post_factor += self.post.get_variation(
                self.code, begin_date, end_date, self.percent
            )

        pre_factor = 1.0
        if self.pre is not None:
            period = DateRangePeriod([begin_date, end_date])
            pre_factor = self.pre.compound(period)

        return post_factor * pre_factor - 1.0

    def __repr__(self):
        return f"Indexer(pre={self.pre}, post={self.post}, percent={self.percent:.2f}, code={self.code!r})"


class BondRate(ABC):
    @abstractmethod
    def get_indexer(self) -> Indexer:
        pass


class FixedRate(BondRate):
    def __init__(self, rate: float):
        self.rate: float = rate
        self.indexer: Indexer = Indexer(pre=rate)

    @override
    def get_indexer(self) -> Indexer:
        return self.indexer


class FloatingRate(BondRate, ABC):
    pass


class CDIPercentualRate(FloatingRate):
    def __init__(self, percent: float):
        self.percent: float = percent
        self.indexer: Indexer = Indexer(
            post=get_bcb_retriever(), percent=percent, code="CDI"
        )

    @override
    def get_indexer(self) -> Indexer:
        return self.indexer


class SELICRate(FloatingRate):
    def __init__(self, rate: float):
        self.rate: float = rate

    @override
    def get_indexer(self) -> Indexer:
        raise Exception("Not implemented!")


class InflationIndexedRate(BondRate, ABC):
    pass


class IPCARate(InflationIndexedRate):
    def __init__(self, rate: float):
        self.rate: float = rate
        self.indexer: Indexer = Indexer(pre=rate, post=get_bcb_retriever(), code="IPCA")

    @override
    def get_indexer(self) -> Indexer:
        return self.indexer
