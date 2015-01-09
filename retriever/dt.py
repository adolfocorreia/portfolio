import string
import glob
import pandas as pd

from retriever import DataRetriever


class DirectTreasureRetriever(DataRetriever):

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
        DataRetriever.__init__(self, "dt")

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

        file_list = glob.glob(self.data_directory + "/*.xls")
        for file_name in file_list:
            print "Loading file %s..." % file_name

            excel = pd.ExcelFile(file_name)

            for sheet_name in excel.sheet_names:
                bond_code = string.replace(sheet_name, " ", "_")

                self._bond_codes.append(bond_code)
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
        DataRetriever.get_value(self, code, date)
        return self._data[code].ix[date].PU_Base_Manha

    def get_variation(self, code, begin_date, end_date):
        raise Exception("Not implemented!")
