import glob
import re

import pandas as pd

from .retriever import ValueRetriever


class FundRetriever(ValueRetriever):
    _regex = re.compile(r"(\.|/|-)")

    def __init__(self):
        ValueRetriever.__init__(self, "fund")

    def _get_data_file_patterns(self):
        return [
            self.data_directory + "/" + FundRetriever._regex.sub("", code) + "_%s.csv"
            for code in self.codes
        ]

    def _available_codes(self):
        return [FundRetriever._regex.sub("", code) for code in self.codes]

    def _load_data_files(self):
        self._data = {}

        names = [
            "Dia",
            "Quota",
            "CaptacaoDia",
            "ResgateDia",
            "Patrimonio",
            "TotalCarteira",
            "NumCotistas",
            "ProxData",
        ]

        file_list = sorted(glob.glob(self.data_directory + "/??????????????_????.csv"))
        for file_name in file_list:
            print("Loading file %s..." % file_name)

            fund_cnpj = file_name.split("/")[-1][:14]

            if fund_cnpj not in self._data:
                self._data[fund_cnpj] = pd.DataFrame()

            df = pd.read_csv(
                file_name,
                names=names,
                header=0,
                skiprows=1,
                parse_dates=["Dia"],
                index_col=0,
            )

            self._data[fund_cnpj] = pd.concat([self._data[fund_cnpj], df])

    def get_value(self, code, date):
        ValueRetriever.get_value(self, code, date)
        ts = pd.Timestamp(date)
        asof_ts = self._data[code].index.asof(ts)
        return self._data[code].loc[asof_ts].Quota
