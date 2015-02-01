import pandas as pd

from model import (
    EquitySecurity,
    InfraDebenture,
    LCI,
    RealEstateFundShare,
    TreasureBond,
)


class Portfolio:

    def __init__(self):
        self.securities = []

    def load_from_csv(self, file):
        df = pd.read_csv(
            file,
            parse_dates=['Data', 'Vencimento'],
            header=0
        )

        for index, row in df.iterrows():
            kind = row.Tipo

            if kind == "TD":
                self.securities.append(
                    TreasureBond.create(row.Ativo, row.Taxa))
            elif kind == "Acao":
                self.securities.append(
                    EquitySecurity.create(row.Ativo))
            elif kind == "FII":
                self.securities.append(RealEstateFundShare(row.Ativo))
            elif kind == "LCI":
                self.securities.append(
                    LCI(row.Ativo, row.Vencimento, row.Taxa, row.Data))
            elif kind == "Deb":
                self.securities.append(
                    InfraDebenture(row.Ativo, row.Vencimento, row.Taxa))
