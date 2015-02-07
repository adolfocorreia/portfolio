import string
import glob
import pandas as pd

from .retriever import ValueRetriever


class DirectTreasureRetriever(ValueRetriever):

    _base_bond_codes = [
        "LFT",
        "LTN",
        "NTN-B",
        "NTN-B_Principal",
        "NTN-C",
        "NTN-F",
    ]

    def __init__(self):
        self._bond_codes = []
        ValueRetriever.__init__(self, "directtreasure")

    def _get_data_file_patterns(self):
        return [self.data_directory + "/" + code + "_%s.xls"
                for code in DirectTreasureRetriever._base_bond_codes]

    def _available_codes(self):
        return self._bond_codes

    def _load_data_files(self):
        print "Loading Direct Treasure XLS files..."

        self._data = {}

        names = [
            "Dia",
            "Taxa_Compra_Manha",
            "Taxa_Venda_Manha",
            "PU_Compra_Manha",
            "PU_Venda_Manha",
            "PU_Base_Manha"
        ]

        file_list = sorted(glob.glob(self.data_directory + "/*.xls"))
        for file_name in file_list:
            print "Loading file %s..." % file_name

            excel = pd.ExcelFile(file_name)

            for sheet_name in excel.sheet_names:
                bond_code = string.replace(sheet_name, " ", "_")

                self._bond_codes.append(bond_code)
                if bond_code not in self._data:
                    self._data[bond_code] = pd.DataFrame()

                df = excel.parse(
                    sheet_name,
                    names=names,
                    parse_dates=['Dia'],
                    dayfirst=True,
                    index_col=['Dia'],
                    skiprows=1
                )

                self._data[bond_code] = self._data[bond_code].append(df)

    def get_value(self, code, date):
        ValueRetriever.get_value(self, code, date)
        ts = pd.Timestamp(date)
        asof_ts = self._data[code].index.asof(ts)
        return self._data[code].ix[asof_ts].PU_Base_Manha
