import glob

import pandas as pd

from .retriever import ValueRetriever


class BovespaRetriever(ValueRetriever):
    def __init__(self):
        ValueRetriever.__init__(self, "bovespa")
        self.check_and_update_data()

    def _get_data_file_patterns(self):
        return [self.data_directory + "/COTAHIST_A%s.parquet"]

    def _available_codes(self):
        assert self._data is not None
        assert isinstance(self._data["bovespa"].index, pd.MultiIndex)
        return self._data["bovespa"].index.levels[1].values

    def _load_data_files(self):
        file_list = sorted(glob.glob(self.data_directory + "/COTAHIST_A*.parquet"))
        df_list = [pd.read_parquet(file) for file in file_list]
        data = pd.concat(df_list)
        data.set_index(["data", "codneg"], inplace=True)
        self._data = {"bovespa": data}

    def get_value(self, code, day):
        assert self._data is not None
        ValueRetriever.get_value(self, code, day)
        sub_df = self._data["bovespa"].xs(code, level="codneg")
        asof_day = sub_df.index.asof(day)
        return sub_df.loc[asof_day]["preult"]
