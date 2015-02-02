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

    def print_portfolio(self):
        for name, (security, amount) in sorted(self.securities.iteritems()):
            today_value = security.get_value(dt.today())
            total = today_value * amount
            print "%30s: %8.2f * %6.2f  =  R$ %8.2f" % (name, today_value, amount, total)
