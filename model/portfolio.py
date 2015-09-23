import pandas as pd
from datetime import datetime as dt
from collections import namedtuple

from allocation import AllocationSet

from .security import (
    EquitySecurity,
    InfraDebenture,
    LCI,
    CDB,
    LC,
    HedgeFundShare,
    RealEstateFundShare,
    ExchangeTradedFundShare,
    StockFundShare,
    TreasureBond,
)

from .category import (
    MainCategories,
    StocksCategories,
    RealEstateCategories,
    PrivateDebtCategories,
    PublicDebtCategories,
    CashCategories,
)


PortfolioItem = namedtuple("PortfolioItem", ["sec", "amount"])


class Portfolio:

    def __init__(self):
        self.at_day = dt.today()
        self.securities = {}
        self.portfolio_value = 0.0
        self.categories_values = dict.fromkeys(list(MainCategories), 0.0)

        self.subcategories_values = dict.fromkeys(list(MainCategories), {})
        self.subcategories_values[MainCategories.Stocks] = dict.fromkeys(list(StocksCategories), 0.0)
        self.subcategories_values[MainCategories.RealEstate] = dict.fromkeys(list(RealEstateCategories), 0.0)
        self.subcategories_values[MainCategories.PrivateDebt] = dict.fromkeys(list(PrivateDebtCategories), 0.0)
        self.subcategories_values[MainCategories.PublicDebt] = dict.fromkeys(list(PublicDebtCategories), 0.0)
        self.subcategories_values[MainCategories.Cash] = dict.fromkeys(list(CashCategories), 0.0)


    def load_from_csv(self, file):
        df = pd.read_csv(
            file,
            parse_dates=['Data', 'Vencimento'],
            header=0
        )

        for index, row in df.iterrows():
            kind = row.Categoria

            if kind == "TD":
                rate = float(row.Taxa[:-1]) / 100.0
                self.add_security(
                    TreasureBond.create(row.Ativo, rate),
                    row.Quantidade)
            elif kind == "Acao":
                self.add_security(
                    EquitySecurity.create(row.Ativo),
                    row.Quantidade)
            elif kind == "FII":
                self.add_security(
                    RealEstateFundShare(row.Ativo),
                    row.Quantidade)
            elif kind == "LCI":
                rate = float(row.Taxa[:-1]) / 100.0
                self.add_security(
                    LCI(row.Ativo, row.Vencimento, rate, row.Data,
                        row.PrecoUnitario, row.Subcategoria),
                    row.Quantidade)
            elif kind == "CDB":
                rate = float(row.Taxa[:-1]) / 100.0
                self.add_security(
                    CDB(row.Ativo, row.Vencimento, rate, row.Data,
                        row.PrecoUnitario, row.Subcategoria),
                    row.Quantidade)
            elif kind == "LC":
                rate = float(row.Taxa[:-1]) / 100.0
                self.add_security(
                    LC(row.Ativo, row.Vencimento, rate, row.Data,
                        row.PrecoUnitario, row.Subcategoria),
                    row.Quantidade)
            elif kind == "Deb":
                rate = float(row.Taxa[:-1]) / 100.0
                self.add_security(
                    InfraDebenture(row.Ativo, row.Vencimento, rate),
                    row.Quantidade)
            elif kind == "ETF":
                self.add_security(
                    ExchangeTradedFundShare(row.Ativo, row.Subcategoria),
                    row.Quantidade)
            elif kind == "HedgeFund":
                pass
                # self.add_security(
                #     HedgeFundShare(row.Ativo),
                #     row.Quantidade)
            elif kind == "StockFund":
                self.add_security(
                    StockFundShare(row.Ativo, row.Subcategoria),
                    row.Quantidade)
            else:
                raise Exception("Unknown security kind: %s" % kind)

    def add_security(self, security, amount):
        unit_value = security.get_value(self.at_day)
        total_value = unit_value * amount
        if security.name in self.securities:
            old_amount = self.securities[security.name].amount
        else:
            old_amount = 0.0

        self.securities[security.name] = PortfolioItem(security,
                                                       old_amount + amount)
        self.portfolio_value += total_value

        cat = security.category
        subcat = security.subcategory

        self.categories_values[cat] += total_value

        subcat_value = self.subcategories_values[cat][subcat]
        self.subcategories_values[cat][subcat] = subcat_value + total_value

    def print_portfolio(self):
        for name, (security, amount) in sorted(self.securities.iteritems()):
            unit_value = security.get_value(self.at_day)
            value = unit_value * amount
            print "%30s: %8.2f * %8.2f  =  R$ %8.2f" % (
                name, unit_value, amount, value)

        print

        for cat in sorted(list(MainCategories)):
            print "%12s: R$ %9.2f  (%5.2f%%)" % (
                cat.name, self.categories_values[cat],
                self.categories_values[cat] / self.portfolio_value * 100.0)
        print "       TOTAL: R$ %9.2f" % self.portfolio_value

    def get_allocation(self):
        allocations = [(x[0], x[1] / self.portfolio_value)
                       for x in self.categories_values.items()]
        return AllocationSet(allocations)

    def get_category_allocation(self, category):
        assert category in self.categories_values
        allocations = [(x[0], x[1] / self.categories_values[category])
                       for x in self.subcategories_values[category].items()]
        return AllocationSet(allocations)

    def get_category_securities_allocation(self, category):
        assert category in self.categories_values
        filtered_securities = {k: v for (k, v) in self.securities.iteritems()
                               if v.sec.category == category}
        total = self.categories_values[category]
        alloc = {k: v.sec.get_value(self.at_day) * v.amount / total
                 for (k, v) in filtered_securities.iteritems()}

        return alloc

    def get_subcategory_securities_allocation(self, category, subcategory):
        assert category in self.categories_values
        if category == MainCategories.Stocks:
            assert StocksCategories[subcategory.name] is not None
        elif category == MainCategories.RealEstate:
            assert RealEstateCategories[subcategory.name] is not None
        elif category == MainCategories.PrivateDebt:
            assert PrivateDebtCategories[subcategory.name] is not None
        elif category == MainCategories.PublicDebt:
            assert PublicDebtCategories[subcategory.name] is not None

        filtered_securities = {k: v for (k, v) in self.securities.iteritems()
                               if v.sec.category == category and
                                  v.sec.subcategory == subcategory}
        total = self.subcategories_values[category][subcategory]
        alloc = {k: v.sec.get_value(self.at_day) * v.amount / total
                 for (k, v) in filtered_securities.iteritems()}

        return alloc
