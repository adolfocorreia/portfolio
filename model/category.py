from enum import Enum

MainCategories = Enum(
    'Stocks',
    'RealEstate',
    'PrivateDebt',
    'PublicDebt',
    'Cash',
)

StocksCategories = Enum(
    'NationalIndex',
    'NationalSmall',
    'Foreign',
)

PrivateDebtCategories = Enum(
    'Inflation',
    'Fixed',
    'Floating',
)

PublicDebtCategories = Enum(
    'Inflation',
    'Fixed',
    'Floating',
)

CashCategories = Enum(
    'Gold',
    'Dollar',
    'Euro',
)
