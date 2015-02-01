from abc import ABCMeta


class BondRate:
    __metaclass__ = ABCMeta

    def __init__(self, rate):
        self.rate = rate


class FixedRate(BondRate):
    pass


class FloatingRate(BondRate):
    __metaclass__ = ABCMeta


class CDIRate(FloatingRate):
    pass


class SELICRate(FloatingRate):
    pass


class InflationIndexedRate(BondRate):
    __metaclass__ = ABCMeta


class IPCARate(InflationIndexedRate):
    pass
