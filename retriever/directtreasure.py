import glob
import os

import duckdb
import pandas as pd

from .retriever import ValueRetriever


class DirectTreasureRetriever(ValueRetriever):
    def __init__(self):
        ValueRetriever.__init__(self, "directtreasure")
        self.check_and_update_data()

    def _get_data_file_patterns(self):
        return [self.data_directory + "/" + code + "_%s.csv" for code in self.codes]

    def _available_codes(self):
        assert self._data is not None
        return self._data.keys()

    def _load_data_files(self):
        self._data = {}

        file_list = sorted(glob.glob(self.data_directory + "/*_????.csv"))
        for file_name in file_list:
            print("Loading file %s..." % file_name)

            code = os.path.basename(file_name).split("_")[0]
            assert code in self.codes

            tickers = (
                duckdb.sql(
                    """
                    SELECT DISTINCT(codigo) AS codigo
                    FROM query_table($file_name)
                    WHERE tipo_titulo = $tipo_titulo
                    ORDER BY 1;
                    """,
                    params={"file_name": file_name, "tipo_titulo": code},
                )
                .df()["codigo"]
                .to_list()
            )

            for ticker in tickers:
                if ticker not in self._data:
                    self._data[ticker] = pd.DataFrame()

                df = duckdb.sql(
                    """
                    SELECT
                        data_base,
                        taxa_compra_manha,
                        taxa_venda_manha,
                        pu_compra_manha,
                        pu_venda_manha,
                        pu_base_manha
                    FROM query_table($file_name)
                    WHERE codigo = $codigo
                    ORDER BY data_base;
                    """,
                    params={"file_name": file_name, "codigo": ticker},
                ).df()
                df.set_index(["data_base"], inplace=True)

                self._data[ticker] = pd.concat([self._data[ticker], df])

    def get_value(self, code, day):
        ValueRetriever.get_value(self, code, day)
        ts = pd.Timestamp(day)
        assert self._data is not None
        asof_ts = self._data[code].index.asof(ts)
        return self._data[code].loc[asof_ts]["pu_base_manha"]
