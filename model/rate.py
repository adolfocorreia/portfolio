from abc import ABCMeta


class BondRate(metaclass=ABCMeta):
    def __init__(self, rate):
        self.rate = rate


class FixedRate(BondRate):
    pass


class FloatingRate(BondRate, metaclass=ABCMeta):
    pass


class CDIRate(FloatingRate):
    pass


class SELICRate(FloatingRate):
    pass


class InflationIndexedRate(BondRate, metaclass=ABCMeta):
    pass


class IPCARate(InflationIndexedRate):
    pass
