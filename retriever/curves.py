import glob
import re

import pandas as pd

from .retriever import CurveRetriever


class B3CurveRetriever(CurveRetriever):
    def __init__(self):
        CurveRetriever.__init__(self, "curves")

    def _get_data_file_patterns(self):
        return [self.data_directory + "/yc_" + code + "_%s.csv" for code in self.codes]

    def _available_codes(self):
        return self.codes

    def _load_data_files(self):
        self._data = {}
        for curve in self.codes:
            self._data[curve] = pd.DataFrame()

        file_list = sorted(glob.glob(self.data_directory + "/yc_*.csv"))

        for file_name in file_list:
            print("Loading file %s..." % file_name)

            reg_exp = re.search(self.data_directory + r"/yc_(.*)_\d{4}\.csv", file_name)
            curve = reg_exp.groups()[0]

            df = pd.read_csv(
                file_name,
                parse_dates=["refdate", "forward_date"],
                usecols=["refdate", "forward_date", "r_252"],
            ).sort_index(kind="stable")

            if len(df) > 0:
                self._data[curve] = pd.concat([self._data[curve], df])

    def get_curve_vertices(self, code, base_date):
        CurveRetriever.get_curve_vertices(self, code, base_date)
        df = self._data[code]
        df = df[df["refdate"] == base_date]
        return df
