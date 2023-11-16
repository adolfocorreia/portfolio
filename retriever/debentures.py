import glob
import re
import pandas as pd

from .retriever import ValueRetriever


class DebenturesRetriever(ValueRetriever):
    def __init__(self):
        ValueRetriever.__init__(self, "debentures")

    def _get_data_file_patterns(self):
        return [self.data_directory + "/" + code + "_NEG_%s.csv" for code in self.codes]

    def _available_codes(self):
        return self.codes

    def _load_data_files(self):
        print("Loading debentures CSV files...")

        names = [
            "Data",
            "Emissor",
            "Codigo_do_Ativo",
            "ISIN",
            "Quantidade",
            "Numero_de_Negocios",
            "PU_Minimo",
            "PU_Medio",
            "PU_Maximo",
            "Percentual_PU_da_Curva",
        ]

        self._data = {}
        for deb in self.codes:
            self._data[deb] = pd.DataFrame()

        file_list = sorted(glob.glob(self.data_directory + "/*_NEG_*.csv"))

        for file_name in file_list:
            print("Loading file %s..." % file_name)

            reg_exp = re.search(
                self.data_directory + r"/(.*)_NEG_\d{4}\.csv", file_name
            )
            deb = reg_exp.groups()[0]

            df = pd.read_csv(
                file_name,
                parse_dates=["Data"],
                dayfirst=True,
                index_col=["Data"],
                names=names,
                header=0,
            ).sort_index(kind="stable")

            if len(df) > 0:
                self._data[deb] = pd.concat([self._data[deb], df])

    def get_value(self, code, date):
        ValueRetriever.get_value(self, code, date)
        ts = pd.Timestamp(date)
        asof_ts = self._data[code].index.asof(ts)
        return self._data[code].loc[asof_ts].PU_Medio
