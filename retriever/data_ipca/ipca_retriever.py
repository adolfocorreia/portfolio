#!/usr/bin/env python

import calendar
import datetime as dt
import os
import re
import sys
import urllib
import zipfile

import pandas as pd


assert len(sys.argv) == 2
YEAR = int(sys.argv[1])
assert re.match(r"^(19|20)[0-9]{2}$", str(YEAR))


IPCA_MAIN_URL = "ftp://ftp.ibge.gov.br/Precos_Indices_de_Precos_ao_Consumidor/IPCA/Serie_Historica/ipca_SerieHist.zip"
IPCA_MAIN_FILE = "ipca_SerieHist.zip"

# http://www.anbima.com.br/pt_br/informar/estatisticas/precos-e-indices/projecao-de-inflacao-gp-m.htm
# http://www.anbima.com.br/pt_br/informar/tabela-de-indicadores.htm
IPCA_PROJECTION_URL = "http://www.anbima.com.br/informacoes/indicadores/arqs/indicadores.xls"
IPCA_PROJECTION_FILE = "indicadores.xls"

COL_NAMES = [
    "Ano",
    "Mes",
    "NumeroIndice",
    "PercNoMes",
    "Perc3Meses",
    "Perc6Meses",
    "PercNoAno",
    "Perc12Meses"
]
MONTHS = {
    "JAN": 1,
    "FEV": 2,
    "MAR": 3,
    "ABR": 4,
    "MAI": 5,
    "JUN": 6,
    "JUL": 7,
    "AGO": 8,
    "SET": 9,
    "OUT": 10,
    "NOV": 11,
    "DEZ": 12
}


# Download and extract main data file
urllib.urlretrieve(IPCA_MAIN_URL, IPCA_MAIN_FILE)

with zipfile.ZipFile(IPCA_MAIN_FILE, 'r') as myzip:
    assert len(myzip.namelist()) == 1
    excel_file_name = myzip.namelist()[0]
    assert excel_file_name[-3:] == "xls"
    myzip.extract(excel_file_name)


# Load data file
df = pd.read_excel(excel_file_name, index_col=None, names=COL_NAMES, skiprows=5)
os.remove(excel_file_name)


# Preprocess data
df.dropna(subset=COL_NAMES[1:], inplace=True)

year = None
for i in range(len(df)):
    if pd.isnull(df.iloc[i].Ano):
        df.iloc[i].Ano = year
    else:
        year = df.iloc[i].Ano

df["Mes"] = df.Mes.apply(lambda x: MONTHS[x])
df.drop(axis=1, inplace=True,
        columns=["NumeroIndice","Perc3Meses","Perc6Meses","PercNoAno","Perc12Meses"])


# Download and load projection data
urllib.urlretrieve(IPCA_PROJECTION_URL, IPCA_PROJECTION_FILE)
df_proj = pd.read_excel(IPCA_PROJECTION_FILE, index_col=None)


# Check data consistency
assert df_proj.iloc[12,0] == "IPCA1"
assert df_proj.iloc[12,1][0:5] == "Proje"  # Example: "Projecao (dez/18)"
today = dt.date.today()
year = df_proj.iloc[12,1][-3:-1]
assert year == today.strftime("%y"), "Unexpected projection year: %s" % year
month = df_proj.iloc[12,1][-7:-4]
assert MONTHS[month.upper()] == today.month, "Unexpected projection month: %s" % month


# Append present month projection rate
rows = {
    "Ano": [today.year],
    "Mes": [today.month],
    "PercNoMes": [df_proj.iloc[12,2]]
}
df = df.append(pd.DataFrame.from_dict(rows))


# Calculate daily rates
df["DiasNoMes"] = df.apply(lambda row: calendar.monthrange(row["Ano"], row["Mes"]), axis=1) \
                    .apply(lambda t: t[1])
df["TaxaDiaria"] = (1.0 + df.PercNoMes/100.0) ** (1.0/df.DiasNoMes) - 1.0


# Assemble CSV file
df.set_index(["Ano", "Mes"], inplace=True)

DELTA = dt.timedelta(days=1)
FIRST_DAY = dt.date(YEAR, 1, 1)
LAST_DAY = min(dt.date(YEAR, 12, 31), dt.date.today())

csv_file_name = "IPCA_%s.csv" % YEAR
with open(csv_file_name, 'w') as csv_file:
    csv_file.write("Dia,Taxa\n")
    day = FIRST_DAY
    while day <= LAST_DAY:
        rate = df.loc[day.year,day.month].TaxaDiaria
        csv_file.write("%s,%s\n" % (day, rate))
        day += DELTA
