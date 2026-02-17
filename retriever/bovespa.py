import glob
from multiprocessing import Pool

import pandas as pd

from .retriever import ValueRetriever

# fmt: off
FIELDS = [
    (  1,   2, "TIPREG"),
    (  3,  10, "DATA"  ),  # Data
    ( 11,  12, "CODBDI"),  # Codigo BDI
    ( 13,  24, "CODNEG"),  # Codigo de negociacao
    ( 25,  27, "TPMERC"),  # Tipo de mercado
    ( 28,  39, "NOMRES"),  # Nome resumido
    ( 40,  49, "ESPECI"),  # Especificacao do papel
    ( 50,  52, "PRAZOT"),
    ( 53,  56, "MODREF"),
    ( 57,  69, "PREABE"),  # Preco abertura
    ( 70,  82, "PREMAX"),  # Preco maximo
    ( 83,  95, "PREMIN"),  # Preco minimo
    ( 96, 108, "PREMED"),  # Preco medio
    (109, 121, "PREULT"),  # Preco fechamento
    (122, 134, "PREOFC"),
    (135, 147, "PREOFV"),
    (148, 152, "TOTNEG"),  # Total de negocios
    (153, 170, "QUATOT"),  # Quantidade de titulos negociados
    (171, 188, "VOLTOT"),  # Volume negociado
    (189, 201, "PREEXE"),
    (202, 202, "INDOPC"),
    (203, 210, "DATVEN"),
    (211, 217, "FATCOT"),
    (218, 230, "PTOEXE"),
    (231, 242, "CODISI"),
    (243, 245, "DISMES"),
]
# fmt: on

COLSPECS = [(item[0] - 1, item[1]) for item in FIELDS]
NAMES = [item[2] for item in FIELDS]

PRICES = [
    "PREABE",
    "PREMAX",
    "PREMIN",
    "PREMED",
    "PREULT",
    "PREOFC",
    "PREOFV",
    "PREEXE",
]

COLS = [
    "DATA",
    "CODNEG",
    "TPMERC",
    "PREULT",
]


def _read_file(file_name):
    print("Loading file %s..." % file_name)

    df = pd.read_fwf(
        file_name,
        names=NAMES,
        header=0,
        parse_dates=["DATA"],
        index_col=["DATA", "CODNEG"],
        usecols=COLS,
        colspecs=COLSPECS,
        skipfooter=1,
        encoding="windows-1252",
    ).query(
        "TPMERC == 10"  # Mercado a vista
    )

    return df


class BovespaRetriever(ValueRetriever):
    def __init__(self):
        ValueRetriever.__init__(self, "bovespa")
        self.check_and_update_data()

    def _get_data_file_patterns(self):
        return [self.data_directory + "/COTAHIST_A%s.ZIP"]

    def _available_codes(self):
        return self._data["bovespa"].index.levels[1].values

    def _load_data_files(self):
        file_list = sorted(glob.glob(self.data_directory + "/COTAHIST_A*.TXT"))

        # Load TXT files in parallel
        with Pool(processes=16) as pool:
            df_list = pool.map(_read_file, file_list)
        data = pd.concat(df_list)

        # Adjust dataframe
        for col in set(PRICES) & set(COLS):
            data[col] /= 100.0
        data.sort_index(inplace=True, kind="stable")

        self._data = {"bovespa": data}

    def get_value(self, code, date):
        ValueRetriever.get_value(self, code, date)
        ts = pd.Timestamp(date)
        sub_df = self._data["bovespa"].xs(code, level="CODNEG")
        asof_ts = sub_df.index.asof(ts)
        return sub_df.loc[asof_ts]["PREULT"]
