from abc import ABC, abstractmethod
from typing import override

from bizdays import Calendar

from retriever.cdi import CDIRetriever
from retriever.ipca import IPCARetriever
from retriever.retriever import VariationRetriever


class Indexer:
    def __init__(
        self,
        pre: float = 0.0,
        post: VariationRetriever | None = None,
        percent: float = 1.0,
        code: str | None = None,
    ):
        assert pre != 0.0 or post is not None
        self.pre: float = pre
        self.post: VariationRetriever | None = None
        self.percent: float = percent
        self.code: str | None = code
        self.cal: Calendar = Calendar.load("ANBIMA")

    def get_variation(self, begin_date: str, end_date: str) -> float:
        assert self.cal is not None
        days: int = self.cal.bizdays(begin_date, end_date)
        assert days >= 0

        post_factor = 1.0
        if self.post is not None:
            assert self.code is not None
            post_factor += self.post.get_variation(
                self.code, begin_date, end_date, self.percent
            )

        pre_factor: float = (1.0 + self.pre) ** (days / 252)

        return post_factor * pre_factor


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
            post=CDIRetriever(), percent=percent, code="CDI"
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
        self.indexer: Indexer = Indexer(pre=rate, post=IPCARetriever(), code="IPCA")

    @override
    def get_indexer(self) -> Indexer:
        return self.indexer
