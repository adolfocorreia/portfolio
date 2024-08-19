import datetime as dt
import glob

import numpy as np
import pandas as pd

from .retriever import VariationRetriever


class CDIRetriever(VariationRetriever):
    def __init__(self):
        VariationRetriever.__init__(self, "cdi")

    def _get_data_file_patterns(self):
        return [self.data_directory + "/CDI_%s.csv"]

    def _available_codes(self):
        return ["CDI"]

    def _load_data_files(self):
        file_list = sorted(glob.glob(self.data_directory + "/CDI_*.csv"))

        data = pd.DataFrame()

        for file_name in file_list:
            print("Loading file %s..." % file_name)

            df = pd.read_csv(
                file_name,
                names=["date", "annual"],
                header=0,
                parse_dates=["date"],
                index_col=["date"],
            )

            data = pd.concat([data, df])

        data["annual"] /= 10000.0

        # http://www.cetip.com.br/astec/di_documentos/metodologia2_i1.htm
        data["daily"] = np.around(
            (data["annual"] + 1.0) ** (1.0 / 252.0) - 1.0, decimals=8
        )

        self._data = {"cdi": data}

    def get_variation(self, code, begin_date, end_date, percentage=1.0):
        VariationRetriever.get_variation(self, code, begin_date, end_date)

        start = dt.datetime.strptime(begin_date, "%Y-%m-%d")
        end = dt.datetime.strptime(end_date, "%Y-%m-%d")

        # Last day is not considered
        end = end - dt.timedelta(days=1)

        interval_df = self._data["cdi"].loc[start:end]
        return round((interval_df.daily * percentage + 1.0).prod() - 1.0, 8)
