from enum import Enum


class OrderedEnum(Enum):
    def __ge__(self, other):
        if self.__class__ is other.__class__:
            return self.value >= other.value
        return NotImplemented

    def __gt__(self, other):
        if self.__class__ is other.__class__:
            return self.value > other.value
        return NotImplemented

    def __le__(self, other):
        if self.__class__ is other.__class__:
            return self.value <= other.value
        return NotImplemented

    def __lt__(self, other):
        if self.__class__ is other.__class__:
            return self.value < other.value
        return NotImplemented


MainCategories = OrderedEnum(
    "MainCategories",
    [
        "Stocks",
        "RealEstate",
        "PrivateDebt",
        "PublicDebt",
        "Cash",
        "Other",
    ],
)

StocksCategories = OrderedEnum(
    "StocksCategories",
    [
        "NationalIndex",
        "NationalSmall",
        "Foreign",
        "Active",
    ],
)

RealEstateCategories = OrderedEnum(
    "RealEstateCategories",
    [
        "Brick",
        "Paper",
    ],
)

PrivateDebtCategories = OrderedEnum(
    "PrivateDebtCategories",
    [
        "Floating",
        "Inflation",
        "Fixed",
    ],
)

PublicDebtCategories = OrderedEnum(
    "PublicDebtCategories",
    [
        "Floating",
        "Inflation",
        "Fixed",
    ],
)

CashCategories = OrderedEnum(
    "CashCategories",
    [
        "Gold",
        "Dollar",
        "Cripto",
    ],
)
