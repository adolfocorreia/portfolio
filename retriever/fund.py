import string
import glob
import re
import pandas as pd

from .retriever import ValueRetriever


class FundRetriever(ValueRetriever):

    _regex = re.compile(r"(\.|/|-)")

    def __init__(self):
        ValueRetriever.__init__(self, "fund")

    def _get_data_file_patterns(self):
        return [self.data_directory + "/" + FundRetriever._regex.sub('', code)
                + "_%s.xlsx" for code in self.codes]

    def _available_codes(self):
        return [FundRetriever._regex.sub('', code) for code in self.codes]

    def _load_data_files(self):
        print "Loading Fund XLSX files..."

        self._data = {}

        names = [
            "Data",
            "Cota",
            "Patrimonio",
            "CapLiquida",
            "NumCotistas",
            "VarDia",
            "VarMes",
            "VarAno",
            "Var12Meses",
        ]

        file_list = sorted(glob.glob(self.data_directory +
                "/??????????????_????.xlsx"))
        for file_name in file_list:
            print "Loading file %s..." % file_name

            fund_cnpj = file_name.split('/')[-1][:14]

            excel = pd.ExcelFile(file_name)

            if fund_cnpj not in self._data:
                self._data[fund_cnpj] = pd.DataFrame()

            df = excel.parse(
                names=names,
                parse_dates=['Data'],
                dayfirst=True,
                index_col=['Data'],
                skiprows=0
            )

            self._data[fund_cnpj] = self._data[fund_cnpj].append(df.iloc[::-1])

    def get_value(self, code, date):
        ValueRetriever.get_value(self, code, date)
        ts = pd.Timestamp(date)
        asof_ts = self._data[code].index.asof(ts)
        return self._data[code].ix[asof_ts].Cota
