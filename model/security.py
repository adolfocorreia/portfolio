"""
A security is a tradable financial asset of any kind.
Securities are broadly categorized into:
- debt securities (e.g., banknotes, bonds and debentures)
- equity securities (e.g., common stocks)
- derivative securities (e.g., forwards, futures, options and swaps)
Reference: http://en.wikipedia.org/wiki/Security_(finance)

Fund shares may be categorized as equity securities as well.
"""

from abc import ABC
from datetime import datetime, date

import retriever

from .category import (
    CashCategories,
    MainCategories,
    PrivateDebtCategories,
    PublicDebtCategories,
    RealEstateCategories,
    StocksCategories,
)
from .rate import BondRate, CDIPercentualRate, FixedRate, IPCARate, SELICRate


class Security(ABC):
    def __init__(self, name, issuer=""):
        self.name = name
        self.issuer = issuer
        self.retriever = None
        self.category = None
        self.subcategory = None

    def get_value(self, day):
        date_str = day.strftime("%Y-%m-%d")
        return self.retriever.get_value(self.name, date_str)


#####################
# EQUITY SECURITIES #
#####################


class EquitySecurity(Security, ABC):
    def __init__(self, name):
        Security.__init__(self, name)

    @staticmethod
    def create(name):
        if name.endswith("F"):
            name = name[:-1]
        if name.endswith("11"):
            return StockUnit(name)
        return Stock(name)


##########
# Stocks #
##########


class Stock(EquitySecurity):
    def __init__(self, name):
        code = int(name[-1])
        assert 1 <= code <= 8, "Invalid stock: %s" % name
        EquitySecurity.__init__(self, name)
        self.retriever = retriever.get_bovespa_retriever()
        self.category = MainCategories.Stocks
        self.subcategory = StocksCategories.NationalIndex


class StockUnit(EquitySecurity):
    def __init__(self, name):
        assert name.endswith("11")
        EquitySecurity.__init__(self, name)
        self.retriever = retriever.get_bovespa_retriever()
        self.category = MainCategories.Stocks
        self.subcategory = StocksCategories.NationalIndex


class SubscriptionRight(EquitySecurity):
    def __init__(self, name, stock):
        code = int(name[-1])
        assert code in (1, 2)
        self.stock = stock
        EquitySecurity.__init__(self, name)
        self.retriever = retriever.get_bovespa_retriever()
        self.category = MainCategories.Stocks
        self.subcategory = StocksCategories.NationalIndex


##########################
# Investment Fund Shares #
##########################


class FundShare(EquitySecurity, ABC):
    def __init__(self, name):
        EquitySecurity.__init__(self, name)


class MutualFundShare(FundShare):
    pass


class ExchangeTradedFundShare(FundShare):
    def __init__(self, name, subcat):
        assert name.endswith("11")

        is_stock = subcat in StocksCategories._member_names_
        is_cash = subcat in CashCategories._member_names_
        assert is_stock ^ is_cash, "Not stock nor cash: %s" % subcat

        FundShare.__init__(self, name)
        self.retriever = retriever.get_bovespa_retriever()

        if is_stock:
            self.category = MainCategories.Stocks
            self.subcategory = StocksCategories[subcat]
        elif is_cash:
            self.category = MainCategories.Cash
            self.subcategory = CashCategories[subcat]
        else:
            raise Exception("Invalid ETF!")


class HedgeFundShare(FundShare):
    def __init__(self, name):
        FundShare.__init__(self, name)
        self.retriever = retriever.get_fund_retriever()
        self.category = MainCategories.Other


class RealEstateFundShare(FundShare):
    def __init__(self, name):
        assert name.endswith("11") or name.endswith("11B")
        FundShare.__init__(self, name)
        self.retriever = retriever.get_bovespa_retriever()
        self.category = MainCategories.RealEstate
        self.subcategory = RealEstateCategories.Brick


class StockFundShare(FundShare):
    def __init__(self, name, subcat):
        assert StocksCategories[subcat] is not None, "Subcategory: %s" % subcat
        FundShare.__init__(self, name)
        self.retriever = retriever.get_fund_retriever()
        self.category = MainCategories.Stocks
        self.subcategory = StocksCategories[subcat]


###################
# DEBT SECURITIES #
###################


class DebtSecurity(Security, ABC):
    def __init__(self, name, maturity, rate):
        Security.__init__(self, name)
        self.maturity = maturity
        assert isinstance(rate, BondRate)
        self.rate = rate

    def is_expired(self):
        return self.maturity < datetime.now()

    def get_value(self, day):
        if self.is_expired():
            return 0.0
        return Security.get_value(self, day)


##################
# Treasure Bonds #
##################


class TreasureBond(DebtSecurity, ABC):
    def __init__(self, name, rate):
        maturity = datetime.strptime(name[-6:], "%d%m%y")
        DebtSecurity.__init__(self, name, maturity, rate)
        self.issuer = "Tesouro Nacional"
        self.retriever = retriever.get_directtreasure_retriever()
        self.category = MainCategories.PublicDebt

    @staticmethod
    def create(name, rate_value):
        if name.startswith("LTN_"):
            return LTN(name, rate_value)
        elif name.startswith("LFT_"):
            return LFT(name, rate_value)
        elif name.startswith("NTN-F_"):
            return NTNF(name, rate_value)
        elif name.startswith("NTN-B_Principal_"):
            return NTNBP(name, rate_value)
        elif name.startswith("NTN-B_"):
            return NTNB(name, rate_value)
        else:
            raise Exception("Invalid Treasure Bond!")


class LTN(TreasureBond):
    def __init__(self, name, rate_value):
        assert name.startswith("LTN_")
        rate = FixedRate(rate_value)
        TreasureBond.__init__(self, name, rate)
        self.subcategory = PublicDebtCategories.Fixed


class LFT(TreasureBond):
    def __init__(self, name, rate_value):
        assert name.startswith("LFT_")
        rate = SELICRate(rate_value)
        TreasureBond.__init__(self, name, rate)
        self.subcategory = PublicDebtCategories.Floating


class NTNF(TreasureBond):
    def __init__(self, name, rate_value):
        assert name.startswith("NTN-F_")
        rate = FixedRate(rate_value)
        TreasureBond.__init__(self, name, rate)
        self.subcategory = PublicDebtCategories.Fixed


class NTNB(TreasureBond):
    def __init__(self, name, rate_value):
        assert name.startswith("NTN-B_") and not name.startswith("NTN-B_Principal_")
        rate = IPCARate(rate_value)
        TreasureBond.__init__(self, name, rate)
        self.subcategory = PublicDebtCategories.Inflation


class NTNBP(TreasureBond):
    def __init__(self, name, rate_value):
        assert name.startswith("NTN-B_Principal_")
        rate = FixedRate(rate_value)
        TreasureBond.__init__(self, name, rate)
        self.subcategory = PublicDebtCategories.Inflation


#############
# Bank Bond #
#############


class BankBond(DebtSecurity, ABC):
    def __init__(self, name, maturity, rate, issue_date, unit_value, subcat):
        assert PrivateDebtCategories[subcat] is not None, "Subcategory: %s" % subcat
        DebtSecurity.__init__(self, name, maturity, rate)
        self.issue_date = issue_date
        self.unit_value = unit_value
        self.category = MainCategories.PrivateDebt
        self.subcategory = PrivateDebtCategories[subcat]

    def get_value(self, day):
        if self.is_expired():
            return 0.0

        begin_date = self.issue_date.strftime("%Y-%m-%d")
        end_date = day.strftime("%Y-%m-%d")
        indexer = self.rate.get_indexer()
        variation = indexer.get_variation(begin_date, end_date)
        return (1.0 + variation) * self.unit_value


class BankBondCDI(BankBond):
    def __init__(self, name, maturity, rate_value, issue_date, unit_value, subcat):
        assert (
            name.startswith("LCI")
            or name.startswith("LCA")
            or name.startswith("CDB")
            or name.startswith("LC")
        )
        rate = CDIPercentualRate(rate_value)
        BankBond.__init__(self, name, maturity, rate, issue_date, unit_value, subcat)
        self.retriever = retriever.get_bcb_retriever()


class BankBondPre(BankBond):
    def __init__(self, name, maturity, rate_value, issue_date, unit_value, subcat):
        assert (
            name.startswith("LCI")
            or name.startswith("LCA")
            or name.startswith("CDB")
            or name.startswith("LC")
        )
        rate = FixedRate(rate_value)
        BankBond.__init__(self, name, maturity, rate, issue_date, unit_value, subcat)


class BankBondIPCA(BankBond):
    def __init__(self, name, maturity, rate_value, issue_date, unit_value, subcat):
        assert (
            name.startswith("LCI")
            or name.startswith("LCA")
            or name.startswith("CDB")
            or name.startswith("LC")
        )
        rate = IPCARate(rate_value)
        BankBond.__init__(self, name, maturity, rate, issue_date, unit_value, subcat)
        self.retriever = retriever.get_bcb_retriever()


##############
# Debentures #
##############


class Debenture(DebtSecurity, ABC):
    def __init__(self, name, maturity, rate_value):
        rate = IPCARate(rate_value)
        DebtSecurity.__init__(self, name, maturity, rate)
        self.retriever = retriever.get_debentures_retriever()
        self.category = MainCategories.PrivateDebt
        self.subcategory = PrivateDebtCategories.Inflation


class RegularDebenture(Debenture):
    def __init__(self, name, maturity, rate_value):
        Debenture.__init__(self, name, maturity, rate_value)


class InfraDebenture(Debenture):
    def __init__(self, name, maturity, rate_value):
        Debenture.__init__(self, name, maturity, rate_value)


#########################
# DERIVATIVE SECURITIES #
#########################


class DerivativeSecurity(Security, ABC):
    pass


class Forward(DerivativeSecurity):
    pass


class Future(DerivativeSecurity):
    pass


class Option(DerivativeSecurity):
    pass


class Swap(DerivativeSecurity):
    pass
