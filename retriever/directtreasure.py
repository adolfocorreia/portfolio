import glob
import re

import pandas as pd

from .retriever import ValueRetriever


class DirectTreasureRetriever(ValueRetriever):
    def __init__(self):
        ValueRetriever.__init__(self, "directtreasure")

    def _get_data_file_patterns(self):
        return [self.data_directory + "/" + code + "_%s.xls" for code in self.codes]

    def _available_codes(self):
        return self._data.keys()

    def _load_data_files(self):
        self._data = {}

        names = [
            "Dia",
            "Taxa_Compra_Manha",
            "Taxa_Venda_Manha",
            "PU_Compra_Manha",
            "PU_Venda_Manha",
            "PU_Base_Manha",
        ]

        regex = re.compile(r"NTN-B_Princ_([0-9]{6})")

        file_list = sorted(glob.glob(self.data_directory + "/*.xls"))
        for file_name in file_list:
            print("Loading file %s..." % file_name)

            excel = pd.ExcelFile(file_name)

            for sheet_name in excel.sheet_names:
                bond_code = sheet_name.replace(" ", "_")
                if regex.match(bond_code):
                    bond_code = regex.sub(r"NTN-B_Principal_\g<1>", bond_code)

                if bond_code not in self._data:
                    self._data[bond_code] = pd.DataFrame()

                df = excel.parse(
                    sheet_name,
                    names=names,
                    parse_dates=["Dia"],
                    dayfirst=True,
                    skiprows=1,
                )
                df.drop_duplicates(subset="Dia", inplace=True)
                df.set_index("Dia", inplace=True)

                self._data[bond_code] = pd.concat([self._data[bond_code], df])

    def get_value(self, code, date):
        ValueRetriever.get_value(self, code, date)
        ts = pd.Timestamp(date)
        asof_ts = self._data[code].index.asof(ts)
        return self._data[code].loc[asof_ts].PU_Base_Manha
