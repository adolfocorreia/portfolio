import datetime as dt
import glob

import pandas as pd

from .retriever import VariationRetriever


class IPCARetriever(VariationRetriever):
    def __init__(self):
        self._data = None
        VariationRetriever.__init__(self, "ipca")

    def _get_data_file_patterns(self):
        return [self.data_directory + "/IPCA_%s.csv"]

    def _available_codes(self):
        return ["IPCA"]

    def _load_data_files(self):
        print("Loading IPCA CSV files...")

        file_list = sorted(glob.glob(self.data_directory + "/IPCA_*.csv"))

        self._data = pd.DataFrame()

        for file_name in file_list:
            print("Loading file %s..." % file_name)

            df = pd.read_csv(
                file_name,
                names=["date", "daily"],
                header=0,
                parse_dates=["date"],
                index_col=["date"],
            )

            self._data = pd.concat([self._data, df])

    def get_variation(self, code, begin_date, end_date):
        VariationRetriever.get_variation(self, code, begin_date, end_date)

        start = dt.datetime.strptime(begin_date, "%Y-%m-%d")
        end = dt.datetime.strptime(end_date, "%Y-%m-%d")

        # Last day is not considered
        end = end - dt.timedelta(days=1)

        interval_df = self._data.loc[start:end]
        return round((interval_df.daily + 1.0).prod() - 1.0, 8)
