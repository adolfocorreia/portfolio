import pandas as pd
from datetime import datetime as dt

from model import (
    EquitySecurity,
    InfraDebenture,
    LCI,
    RealEstateFundShare,
    TreasureBond,
)


class Portfolio:

    def __init__(self):
        self.securities = {}

    def load_from_csv(self, file):
        df = pd.read_csv(
            file,
            parse_dates=['Data', 'Vencimento'],
            header=0
        )

        for index, row in df.iterrows():
            kind = row.Tipo

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
                    LCI(row.Ativo, row.Vencimento, rate, row.Data, row.PrecoUnitario),
                    row.Quantidade)
            elif kind == "Deb":
                rate = float(row.Taxa[:-1]) / 100.0
                self.add_security(
                    InfraDebenture(row.Ativo, row.Vencimento, rate),
                    row.Quantidade)
            else:
                raise Exception("Unknown security kind!")

    def add_security(self, security, amount):
        name = security.name
        if name in self.securities:
            old_amount = self.securities[name][1]
            self.securities[name] = (security, old_amount + amount)
        else:
            self.securities[name] = (security, amount)

    def print_portfolio(self, at_day=None):
        portfolio_total = 0.0
        classes_total = {
            'FII': 0.0,
            'TD': 0.0,
            'BOV': 0.0,
            'LCI': 0.0,
            'DEB': 0.0,
        }

        if at_day is None:
            at_day = dt.today()

        for name, (security, amount) in sorted(self.securities.iteritems()):
            value_at_day = security.get_value(at_day)
            total = value_at_day * amount
            print "%30s: %8.2f * %6.2f  =  R$ %8.2f" % (name, value_at_day, amount, total)

            portfolio_total += total
            if isinstance(security, RealEstateFundShare):
                classes_total['FII'] += total
            elif isinstance(security, TreasureBond):
                classes_total['TD'] += total
            elif isinstance(security, EquitySecurity):
                classes_total['BOV'] += total
            elif isinstance(security, LCI):
                classes_total['LCI'] += total
            elif isinstance(security, InfraDebenture):
                classes_total['DEB'] += total
            else:
                raise Exception()

        print
        print "  FII: R$ %9.2f  (%5.2f%%)" % (classes_total['FII'], classes_total['FII'] / portfolio_total * 100.0)
        print "  BOV: R$ %9.2f  (%5.2f%%)" % (classes_total['BOV'], classes_total['BOV'] / portfolio_total * 100.0)
        print "   TD: R$ %9.2f  (%5.2f%%)" % (classes_total['TD'], classes_total['TD'] / portfolio_total * 100.0)
        print "  LCI: R$ %9.2f  (%5.2f%%)" % (classes_total['LCI'], classes_total['LCI'] / portfolio_total * 100.0)
        print "  DEB: R$ %9.2f  (%5.2f%%)" % (classes_total['DEB'], classes_total['DEB'] / portfolio_total * 100.0)
        print "Total: R$ %9.2f" % portfolio_total
