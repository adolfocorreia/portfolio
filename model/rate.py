from abc import ABC


class BondRate(ABC):
    def __init__(self, rate):
        self.rate = rate


class FixedRate(BondRate):
    pass


class FloatingRate(BondRate, ABC):
    pass


class CDIRate(FloatingRate):
    pass


class SELICRate(FloatingRate):
    pass


class InflationIndexedRate(BondRate, ABC):
    pass


class IPCARate(InflationIndexedRate):
    pass
