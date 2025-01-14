import datetime as dt
import glob
from typing import override

import pandas as pd

from .retriever import VariationRetriever


class BCBRetriever(VariationRetriever):
    def __init__(self):
        VariationRetriever.__init__(self, "bcb")

    @override
    def _get_data_file_patterns(self):
        return [self.data_directory + "/sgs_daily_%s.csv"]

    @override
    def _available_codes(self):
        return ["CDI", "SELIC", "IPCA"]

    @override
    def _load_data_files(self):
        file_list = sorted(glob.glob(self.data_directory + "/sgs_daily_*.csv"))
        assert len(file_list) > 0

        data = pd.DataFrame()

        for file_name in file_list:
            print("Loading file %s..." % file_name)

            df = pd.read_csv(
                file_name,
                index_col=0,
                parse_dates=True,
            )

            data = pd.concat([data, df])

        data /= 100.0

        self._data = {"bcb": data}

    def get_variation(self, code, begin_date, end_date, percentage=1.0):
        VariationRetriever.get_variation(self, code, begin_date, end_date)

        start = dt.datetime.strptime(begin_date, "%Y-%m-%d")
        end = dt.datetime.strptime(end_date, "%Y-%m-%d")

        # Last day is not considered
        end = end - dt.timedelta(days=1)

        interval_df = self._data["bcb"].loc[start:end]
        assert len(interval_df) > 0
        return round((interval_df[code] * percentage + 1.0).prod() - 1.0, 8)
