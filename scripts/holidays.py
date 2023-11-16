import urllib.request
import pandas as pd
import datetime as dt


YEAR = 2014

URL = "http://www.anbima.com.br/feriados/arqs/feriados_nacionais.xls"
FILE = "feriados_nacionais.xls"

urllib.request.urlretrieve(URL, FILE)

df = pd.read_excel(FILE, skipfooter=9, names=["Data", "DiaDaSemana", "Feriado"])
df = df.set_index("Data")

FIRST_DAY = dt.date(YEAR, 1, 1)
LAST_DAY = dt.date(YEAR, 12, 31)

print(df.loc[FIRST_DAY:LAST_DAY])
