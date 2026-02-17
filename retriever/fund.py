import glob
import re

import pandas as pd

from .retriever import ValueRetriever


class FundsInfo:
    def __init__(self, codes_file: str):
        self.funds = dict()
        for line in open(codes_file):
            split_line = line.strip().split("|")
            code = split_line[0].translate({ord(i): None for i in "./-"})
            cnpj = split_line[0]
            subclass = split_line[1] or None
            name = split_line[2]
            self.funds[code] = {"name": name, "cnpj": cnpj, "subclass": subclass}

    def get_fund_name(self, code: str):
        return self.funds[code]["name"]

    def get_fund_subclass(self, code: str):
        return self.funds[code]["subclass"]


class FundRetriever(ValueRetriever):
    _regex = re.compile(r"(\.|/|-)")

    def __init__(self):
        ValueRetriever.__init__(self, "fund")
        self.funds_info: FundsInfo = FundsInfo(self.data_directory + "/codes.txt")
        self.check_and_update_data()

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
            "TP_FUNDO_CLASSE",
            "CNPJ_FUNDO_CLASSE",
            "ID_SUBCLASSE",
            "DT_COMPTC",
            "VL_TOTAL",
            "VL_QUOTA",
            "VL_PATRIM_LIQ",
            "CAPTC_DIA",
            "RESG_DIA",
            "NR_COTST",
        ]

        file_list = sorted(glob.glob(self.data_directory + "/??????????????_????.csv"))
        for file_name in file_list:
            print("Loading file %s..." % file_name)

            # year = int(file_name.split("/")[-1][-8:-4])
            fund_cnpj = file_name.split("/")[-1][:14]

            if fund_cnpj not in self._data:
                self._data[fund_cnpj] = pd.DataFrame()

            df = pd.read_csv(
                file_name,
                names=names,
                header=0,
                skiprows=1,
                parse_dates=["DT_COMPTC"],
                index_col="DT_COMPTC",
            )
            df.drop("TP_FUNDO_CLASSE", axis=1, inplace=True)
            df.drop_duplicates(inplace=True)

            # ID_SUBCLASSE must be null or a unique value corresponding to the fund
            subclass = self.funds_info.get_fund_subclass(fund_cnpj)
            if subclass is None:
                assert df["ID_SUBCLASSE"].isna().all(), (
                    f"Non null subclasses: {set(df['ID_SUBCLASSE'].dropna())}"
                )
            else:
                df = df.query(f"ID_SUBCLASSE.isnull() or ID_SUBCLASSE=='{subclass}'")

            if len(df) > 0:
                self._data[fund_cnpj] = pd.concat([self._data[fund_cnpj], df])
                assert not any(self._data[fund_cnpj].index.duplicated())

    def get_value(self, code, date):
        ValueRetriever.get_value(self, code, date)
        ts = pd.Timestamp(date)
        asof_ts = self._data[code].index.asof(ts)
        return self._data[code].loc[asof_ts]["VL_QUOTA"]
