from enum import auto

from ordered_enum import OrderedEnum


class MainCategories(OrderedEnum):
    Stocks = auto()
    RealEstate = auto()
    PrivateDebt = auto()
    PublicDebt = auto()
    Cash = auto()
    Other = auto()


class StocksCategories(OrderedEnum):
    NationalIndex = auto()
    NationalSmall = auto()
    Foreign = auto()
    Active = auto()


class RealEstateCategories(OrderedEnum):
    Brick = auto()
    Paper = auto()


class PrivateDebtCategories(OrderedEnum):
    Floating = auto()
    Inflation = auto()
    Fixed = auto()


class PublicDebtCategories(OrderedEnum):
    Floating = auto()
    Inflation = auto()
    Fixed = auto()


class CashCategories(OrderedEnum):
    Gold = auto()
    Dollar = auto()
    Cripto = auto()
