"""
A security is a tradable financial asset of any kind.
Securities are broadly categorized into:
- debt securities (e.g., banknotes, bonds and debentures)
- equity securities (e.g., common stocks)
- derivative securities (e.g., forwards, futures, options and swaps)
Reference: http://en.wikipedia.org/wiki/Security_(finance)

Fund shares may be categorized as equity securities as well.
"""

from abc import ABC, abstractmethod
from datetime import date, datetime, timedelta
from typing import override

from bizdays import Calendar

CAL = Calendar.load("ANBIMA")

import retriever
from retriever.retriever import ValueRetriever

from .category import (
    CashCategories,
    MainCategories,
    OrderedEnum,
    PrivateDebtCategories,
    PublicDebtCategories,
    RealEstateCategories,
    StocksCategories,
)
from .curves import Curve
from .fixedincome import DateRangePeriod, ir_over
from .rate import BondRate, CDIPercentualRate, FixedRate, IPCARate, SELICRate


class Security(ABC):
    def __init__(
        self,
        name: str,
        retriever: ValueRetriever,
        category: OrderedEnum,
        subcategory: OrderedEnum,
        issuer: str = "",
    ):
        self.name: str = name
        self.retriever: ValueRetriever = retriever
        self.category: OrderedEnum = category
        self.subcategory: OrderedEnum = subcategory
        self.issuer: str = issuer

    def get_value(self, day: str | date) -> float:
        assert self.retriever is not None
        return self.retriever.get_value(self.name, day)

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(name={self.name!r})"


#####################
# EQUITY SECURITIES #
#####################


class EquitySecurity(Security, ABC):
    def __init__(
        self,
        name: str,
        retriever: ValueRetriever,
        category: OrderedEnum,
        subcategory: OrderedEnum,
    ):
        Security.__init__(self, name, retriever, category, subcategory)

    @staticmethod
    def create(name: str):
        if name.endswith("F"):
            name = name[:-1]
        if name.endswith("11"):
            return StockUnit(name)
        return Stock(name)


##########
# Stocks #
##########


class Stock(EquitySecurity):
    def __init__(self, name: str):
        code = int(name[-1])
        assert 1 <= code <= 8, "Invalid stock: %s" % name
        EquitySecurity.__init__(
            self,
            name,
            retriever.get_bovespa_retriever(),
            MainCategories.Stocks,
            StocksCategories.NationalIndex,
        )


class StockUnit(EquitySecurity):
    def __init__(self, name: str):
        assert name.endswith("11")
        EquitySecurity.__init__(
            self,
            name,
            retriever.get_bovespa_retriever(),
            MainCategories.Stocks,
            StocksCategories.NationalIndex,
        )


class SubscriptionRight(EquitySecurity):
    def __init__(self, name: str, stock: Stock):
        code = int(name[-1])
        assert code in (1, 2)
        self.stock: Stock = stock
        EquitySecurity.__init__(
            self,
            name,
            retriever.get_bovespa_retriever(),
            MainCategories.Stocks,
            StocksCategories.NationalIndex,
        )


##########################
# Investment Fund Shares #
##########################


class FundShare(EquitySecurity, ABC):
    def __init__(
        self,
        name: str,
        retriever: ValueRetriever,
        category: OrderedEnum,
        subcategory: OrderedEnum,
    ):
        EquitySecurity.__init__(self, name, retriever, category, subcategory)


class MutualFundShare(FundShare):
    pass


class ExchangeTradedFundShare(FundShare):
    def __init__(self, name: str, subcat: str):
        assert name.endswith("11")

        is_stock = subcat in StocksCategories._member_names_
        is_cash = subcat in CashCategories._member_names_
        assert is_stock ^ is_cash, "Not stock nor cash: %s" % subcat

        if is_stock:
            category = MainCategories.Stocks
            subcategory = StocksCategories[subcat]
        elif is_cash:
            category = MainCategories.Cash
            subcategory = CashCategories[subcat]
        else:
            raise Exception("Invalid ETF!")

        FundShare.__init__(
            self, name, retriever.get_bovespa_retriever(), category, subcategory
        )


class HedgeFundShare(FundShare):
    def __init__(self, name: str):
        FundShare.__init__(
            self, name, retriever.get_fund_retriever(), MainCategories.Other, None
        )


class RealEstateFundShare(FundShare):
    def __init__(self, name: str):
        assert name.endswith("11") or name.endswith("11B")
        FundShare.__init__(
            self,
            name,
            retriever.get_bovespa_retriever(),
            MainCategories.RealEstate,
            RealEstateCategories.Brick,
        )


class StockFundShare(FundShare):
    def __init__(self, name: str, subcat: str):
        assert StocksCategories[subcat] is not None, "Subcategory: %s" % subcat
        FundShare.__init__(
            self,
            name,
            retriever.get_fund_retriever(),
            MainCategories.Stocks,
            StocksCategories[subcat],
        )


###################
# DEBT SECURITIES #
###################


class DebtSecurity(Security, ABC):
    def __init__(
        self,
        name: str,
        retriever: ValueRetriever,
        category: OrderedEnum,
        subcategory: OrderedEnum,
        maturity: str | date,
        rate: BondRate,
        issuer: str = "",
    ):
        Security.__init__(self, name, retriever, category, subcategory, issuer)
        self.maturity: date = (
            datetime.strptime(maturity, "%Y-%m-%d").date()
            if isinstance(maturity, str)
            else date(maturity.year, maturity.month, maturity.day)
        )
        self.rate: BondRate = rate

    def is_expired(self) -> bool:
        return self.maturity < date.today()

    @override
    def get_value(self, day: str | date) -> float:
        if self.is_expired():
            return 0.0
        return Security.get_value(self, day)


##################
# Treasure Bonds #
##################


class TreasureBond(DebtSecurity, ABC):
    def __init__(self, name: str, subcategory: OrderedEnum, rate: BondRate):
        maturity = datetime.strptime(name[-6:], "%d%m%y").date()
        DebtSecurity.__init__(
            self,
            name,
            retriever.get_directtreasure_retriever(),
            MainCategories.PublicDebt,
            subcategory,
            maturity,
            rate,
            "Tesouro Nacional",
        )

    @staticmethod
    def create(name: str, rate_value: float):
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
    def __init__(self, name: str, rate_value: float):
        assert name.startswith("LTN_")
        rate = FixedRate(rate_value)
        TreasureBond.__init__(self, name, PublicDebtCategories.Fixed, rate)


class LFT(TreasureBond):
    def __init__(self, name: str, rate_value: float):
        assert name.startswith("LFT_")
        rate = SELICRate(rate_value)
        TreasureBond.__init__(self, name, PublicDebtCategories.Floating, rate)


class NTNF(TreasureBond):
    def __init__(self, name: str, rate_value: float):
        assert name.startswith("NTN-F_")
        rate = FixedRate(rate_value)
        TreasureBond.__init__(self, name, PublicDebtCategories.Fixed, rate)


class NTNB(TreasureBond):
    def __init__(self, name: str, rate_value: float):
        assert name.startswith("NTN-B_") and not name.startswith("NTN-B_Principal_")
        rate = IPCARate(rate_value)
        TreasureBond.__init__(self, name, PublicDebtCategories.Inflation, rate)


class NTNBP(TreasureBond):
    def __init__(self, name: str, rate_value: float):
        assert name.startswith("NTN-B_Principal_")
        rate = FixedRate(rate_value)
        TreasureBond.__init__(self, name, PublicDebtCategories.Inflation, rate)


#############
# Bank Bond #
#############


class BankBond(DebtSecurity, ABC):
    def __init__(
        self,
        name: str,
        maturity: date,
        rate: BondRate,
        issue_date: date,
        unit_value: float,
        subcat: str,
        mark_to_market: bool = True,
    ):
        assert PrivateDebtCategories[subcat] is not None, "Subcategory: %s" % subcat
        assert (
            name.startswith("LCI")
            or name.startswith("LCA")
            or name.startswith("CDB")
            or name.startswith("LC")
        )
        assert isinstance(maturity, date)
        DebtSecurity.__init__(
            self,
            name,
            None,
            MainCategories.PrivateDebt,
            PrivateDebtCategories[subcat],
            maturity,
            rate,
        )
        assert isinstance(issue_date, date)
        self.issue_date: date = date(issue_date.year, issue_date.month, issue_date.day)
        self.unit_value: float = unit_value
        self.mark_to_market = mark_to_market
        self.g_spread_at_emission: float = self.compute_g_spread_at_emission()

    @abstractmethod
    def compute_g_spread_at_emission(self) -> float:
        pass

    @abstractmethod
    def compute_cash_flow_at_maturity(self, reference_day: date) -> float:
        pass

    @property
    def tax_rate(self) -> float:
        days_to_maturity = (self.maturity - self.issue_date).days
        assert days_to_maturity > 0
        # TODO: place this logic elsewhere
        if days_to_maturity <= 180:
            return 22.5 / 100
        elif days_to_maturity <= 360:
            return 20.0 / 100
        elif days_to_maturity <= 720:
            return 17.5 / 100
        else:
            return 15.0 / 100

    @override
    def get_value(self, day: str | date) -> float:
        if self.is_expired():
            return 0.0

        if isinstance(day, str):
            day = datetime.strptime(day, "%Y-%m-%d").date()

        if self.mark_to_market:
            # Mark to market value is equal to the projected cash flow at maturity,
            # discounted by the sum of the risk-free rate and the bond's g-spread.

            # Compute projected cash flow at maturity (per bond)
            projected_cash_flow = self.compute_cash_flow_at_maturity(day)

            # Compute discount rate (risk-free + g-spread)
            curve_date = (
                day if date.today() > day else CAL.preceding(day - timedelta(days=1))
            )
            pre_curve = Curve("di_pre", curve_date)
            risk_free_rate = pre_curve.get_rate(self.maturity)
            discount_rate = risk_free_rate + self.g_spread_at_emission

            # Compute discount factor
            ir = ir_over(discount_rate)
            discount_factor = ir.discount(DateRangePeriod([day, self.maturity]))

            market_value = projected_cash_flow * discount_factor
            return market_value

        else:
            # Mark to curve value is equal to the original issued value,
            # compounded by past variation of the corresponding indexer.
            indexer = self.rate.get_indexer()
            variation = indexer.get_variation(self.issue_date, day)
            return (1.0 + variation) * self.unit_value


class BankBondCDI(BankBond):
    def __init__(
        self,
        name: str,
        maturity: date,
        percent: float,
        issue_date: date,
        unit_value: float,
        subcat: str,
    ):
        rate = CDIPercentualRate(percent)
        BankBond.__init__(self, name, maturity, rate, issue_date, unit_value, subcat)

    @override
    def compute_g_spread_at_emission(self) -> float:
        pre_curve = Curve("di_pre", self.issue_date)
        risk_free_rate = pre_curve.get_rate(self.maturity)

        percent = self.rate.percent
        bond_rate = risk_free_rate * percent
        # Gross up rates for tax-free bonds
        if self.name[0:3] in ("LCA", "LCI"):
            bond_rate /= 1.0 - self.tax_rate

        g_spread = bond_rate - risk_free_rate
        return g_spread

    @override
    def compute_cash_flow_at_maturity(self, reference_day: date) -> float:
        assert self.issue_date <= reference_day <= self.maturity

        # To compute the projected cash flow at maturity, two steps are needed:
        # First we need to take into account the past variation of the indexer
        # (from the issue date until the reference day).
        # Then we need to consider the projected variation of the indexer
        # (from the reference day until maturity) according to the corresponding curves.

        # Get past variation
        indexer = self.rate.get_indexer()
        past_variation_factor = (
            indexer.get_variation(self.issue_date, reference_day) + 1.0
        )

        # Get projected risk-free and bond rates
        curve_date = (
            reference_day
            if date.today() > reference_day
            else CAL.preceding(reference_day - timedelta(days=1))
        )
        pre_curve = Curve("di_pre", curve_date)
        risk_free_rate = pre_curve.get_rate(self.maturity)
        future_bond_rate = risk_free_rate * self.rate.percent

        # Get projected future variation
        ir = ir_over(future_bond_rate)
        period = DateRangePeriod([reference_day, self.maturity])
        future_variation_factor = ir.compound(period)

        factor = past_variation_factor * future_variation_factor
        return factor * self.unit_value


class BankBondPre(BankBond):
    def __init__(
        self,
        name: str,
        maturity: date,
        rate_value: float,
        issue_date: date,
        unit_value: float,
        subcat: str,
    ):
        rate = FixedRate(rate_value)
        BankBond.__init__(self, name, maturity, rate, issue_date, unit_value, subcat)

    @override
    def compute_g_spread_at_emission(self) -> float:
        pre_curve = Curve("di_pre", self.issue_date)
        risk_free_rate = pre_curve.get_rate(self.maturity)

        bond_rate = self.rate.rate
        # Gross up tax-free bonds
        if self.name[0:3] in ("LCA", "LCI"):
            bond_rate /= 1.0 - self.tax_rate

        g_spread = bond_rate - risk_free_rate
        return g_spread

    @override
    def compute_cash_flow_at_maturity(self, reference_day: date) -> float:
        assert self.issue_date <= reference_day <= self.maturity

        # The projected cash flow at maturity is simply the issued unit value
        # multiplied by the compounding factor from the issue date until maturity.
        ir = ir_over(self.rate.rate)
        period = DateRangePeriod([self.issue_date, self.maturity])
        factor = ir.compound(period)
        return factor * self.unit_value


class BankBondIPCA(BankBond):
    def __init__(
        self,
        name: str,
        maturity: date,
        rate_value: float,
        issue_date: date,
        unit_value: float,
        subcat: str,
    ):
        rate = IPCARate(rate_value)
        BankBond.__init__(self, name, maturity, rate, issue_date, unit_value, subcat)

    @override
    def compute_g_spread_at_emission(self) -> float:
        pre_curve = Curve("di_pre", self.issue_date)
        risk_free_rate = pre_curve.get_rate(self.maturity)

        real_curve = Curve("di_ipca", self.issue_date)
        real_rate = real_curve.get_rate(self.maturity)

        inflation = (1.0 + risk_free_rate) / (1.0 + real_rate) - 1.0
        bond_rate = (1.0 + self.rate.rate) * (1.0 + inflation) - 1.0
        # Gross up tax-free bonds
        if self.name[0:3] in ("LCA", "LCI"):
            bond_rate /= 1.0 - self.tax_rate

        g_spread = bond_rate - risk_free_rate
        return g_spread

    @override
    def compute_cash_flow_at_maturity(self, reference_day: date) -> float:
        assert self.issue_date <= reference_day <= self.maturity
        raise NotImplementedError()


##############
# Debentures #
##############


class Debenture(DebtSecurity):
    def __init__(self, name: str, maturity: date, rate_value: float):
        rate = IPCARate(rate_value)
        DebtSecurity.__init__(
            self,
            name,
            retriever.get_debentures_retriever(),
            MainCategories.PrivateDebt,
            PrivateDebtCategories.Inflation,
            maturity,
            rate,
        )


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
