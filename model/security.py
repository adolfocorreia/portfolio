from abc import ABCMeta
from datetime import datetime

from .rate import BondRate, FixedRate, CDIRate, SELICRate, IPCARate
from .category import (
    MainCategories,
    StocksCategories,
    RealEstateCategories,
    PrivateDebtCategories,
    PublicDebtCategories,
)


import retriever


"""
A security is a tradable financial asset of any kind.
Securities are broadly categorized into:
- debt securities (e.g., banknotes, bonds and debentures)
- equity securities (e.g., common stocks)
- derivative securities (e.g., forwards, futures, options and swaps)
Reference: http://en.wikipedia.org/wiki/Security_(finance)

Fund shares may be categorized as equity securities as well.
"""


class Security:
    __metaclass__ = ABCMeta

    def __init__(self, name, issuer=""):
        self.name = name
        self.issuer = issuer
        self.retriever = None
        self.category = None
        self.subcategory = None

    def get_value(self, date):
        date_str = date.strftime("%Y-%m-%d")
        return self.retriever.get_value(self.name, date_str)


#####################
# EQUITY SECURITIES #
#####################

class EquitySecurity(Security):
    __metaclass__ = ABCMeta

    def __init__(self, name):
        Security.__init__(self, name)

    @staticmethod
    def create(name):
        if name.endswith("F"):
            name = name[:-1]
        if name.endswith("11"):
            return StockUnit(name)
        else:
            return Stock(name)


##########
# Stocks #
##########

class Stock(EquitySecurity):
    def __init__(self, name):
        code = int(name[-1])
        assert code >= 3 and code <= 8, "Invalid stock: %s" % name
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
        assert code == 1 or code == 2
        self.stock = stock
        EquitySecurity.__init__(self, name)
        self.retriever = retriever.get_bovespa_retriever()
        self.category = MainCategories.Stocks
        self.subcategory = StocksCategories.NationalIndex


##########################
# Investment Fund Shares #
##########################

class FundShare(EquitySecurity):
    __metaclass__ = ABCMeta

    def __init__(self, name):
        EquitySecurity.__init__(self, name)


class MutualFundShare(FundShare):
    pass


class ExchangeTradedFundShare(FundShare):
    def __init__(self, name, subcat):
        assert name.endswith("11")
        assert StocksCategories[subcat] is not None, "Subcategory: %s" % subcat
        FundShare.__init__(self, name)
        self.retriever = retriever.get_bovespa_retriever()
        self.category = MainCategories.Stocks
        self.subcategory = StocksCategories[subcat]


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

class DebtSecurity(Security):
    __metaclass__ = ABCMeta

    def __init__(self, name, maturity, rate):
        Security.__init__(self, name)
        self.maturity = maturity
        assert isinstance(rate, BondRate)
        self.rate = rate

    def is_expired(self):
        return self.maturity < datetime.now()

    def get_value(self, date):
        if self.is_expired():
            return 0.0
        else:
            return Security.get_value(self, date)


##################
# Treasure Bonds #
##################

class TreasureBond(DebtSecurity):
    __metaclass__ = ABCMeta

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
        assert (name.startswith("NTN-B_") and
                not name.startswith("NTN-B_Principal_"))
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

class BankBond(DebtSecurity):
    __metaclass__ = ABCMeta

    def __init__(self, name, maturity, rate, issue_date, unit_value, subcat):
        assert PrivateDebtCategories[subcat] is not None, "Subcategory: %s" % subcat
        DebtSecurity.__init__(self, name, maturity, rate)
        self.issue_date = issue_date
        self.unit_value = unit_value
        self.retriever = retriever.get_cdi_retriever()
        self.category = MainCategories.PrivateDebt
        self.subcategory = PrivateDebtCategories[subcat]

    def get_value(self, date):
        if self.is_expired():
            return 0.0
        elif isinstance(self.rate, CDIRate):
            begin_date = self.issue_date.strftime("%Y-%m-%d")
            end_date = date.strftime("%Y-%m-%d")
            variation = self.retriever.get_variation(
                "CDI", begin_date, end_date, self.rate.rate)
            return (1.0 + variation) * self.unit_value
        elif isinstance(self.rate, FixedRate):
            delta = date - self.issue_date
            days = delta.days
            annual_rate = self.rate.rate
            daily_rate = (annual_rate + 1.0)**(1.0 / 365.0) - 1.0
            variation = (daily_rate + 1.0)**days - 1.0
            return (1.0 + variation) * self.unit_value
        else:
            assert False


class LCI(BankBond):
    def __init__(self, name, maturity, rate_value, issue_date, unit_value, subcat):
        assert name.startswith("LCI")
        rate = CDIRate(rate_value)
        BankBond.__init__(self, name, maturity, rate, issue_date, unit_value, subcat)


class CDB(BankBond):
    def __init__(self, name, maturity, rate_value, issue_date, unit_value, subcat):
        assert name.startswith("CDB")
        rate = CDIRate(rate_value)
        BankBond.__init__(self, name, maturity, rate, issue_date, unit_value, subcat)


class LC(BankBond):
    def __init__(self, name, maturity, rate_value, issue_date, unit_value, subcat):
        assert name.startswith("LC")
        rate = FixedRate(rate_value)
        BankBond.__init__(self, name, maturity, rate, issue_date, unit_value, subcat)


##############
# Debentures #
##############

class Debenture(DebtSecurity):
    __metaclass__ = ABCMeta

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

class DerivativeSecurity(Security):
    __metaclass__ = ABCMeta


class Forward(DerivativeSecurity):
    pass


class Future(DerivativeSecurity):
    pass


class Option(DerivativeSecurity):
    pass


class Swap(DerivativeSecurity):
    pass
