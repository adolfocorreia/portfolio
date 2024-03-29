import glob
import pandas as pd

from .retriever import ValueRetriever


class BovespaRetriever(ValueRetriever):
    def __init__(self):
        ValueRetriever.__init__(self, "bovespa")

    def _get_data_file_patterns(self):
        return [self.data_directory + "/COTAHIST_A%s.ZIP"]

    def _available_codes(self):
        return self._data.index.levels[1].values

    def _load_data_files(self):
        print("Loading stocks TXT files...")

        # fmt: off
        fields = [
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

        colspecs = [(item[0] - 1, item[1]) for item in fields]
        names = [item[2] for item in fields]

        # filter_CODBDI = [
        #     "02",  # Lote padrao
        #     "12",  # Fundos imobiliarios
        # ]

        prices = [
            "PREABE",
            "PREMAX",
            "PREMIN",
            "PREMED",
            "PREULT",
            "PREOFC",
            "PREOFV",
            # "VOLTOT",
            "PREEXE",
        ]

        self._data = pd.DataFrame()

        file_list = sorted(glob.glob(self.data_directory + "/COTAHIST_A*.TXT"))

        for file_name in file_list:
            print("Loading file %s..." % file_name)

            df = pd.read_fwf(
                file_name,
                names=names,
                header=0,
                parse_dates=["DATA"],
                index_col=["DATA", "CODNEG"],
                colspecs=colspecs,
                skipfooter=1,
                encoding="windows-1252",
            )
            df = df[df["TPMERC"] == 10]  # Mercado a vista

            self._data = pd.concat([self._data, df])

        for col in prices:
            self._data[col] /= 100.0

        self._data.sort_index(inplace=True, kind="stable")

        print("Done loading stocks TXT files.")

    def get_value(self, code, date):
        ValueRetriever.get_value(self, code, date)
        ts = pd.Timestamp(date)
        sub_df = self._data.xs(code, level="CODNEG")
        asof_ts = sub_df.index.asof(ts)
        return sub_df.loc[asof_ts].PREULT
