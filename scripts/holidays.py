import urllib.request
from datetime import date

import pandas as pd

YEAR = date.today().year

URL = "http://www.anbima.com.br/feriados/arqs/feriados_nacionais.xls"
FILE = "feriados_nacionais.xls"

_ = urllib.request.urlretrieve(URL, FILE)

df = pd.read_excel(FILE, skipfooter=9, names=["Data", "DiaDaSemana", "Feriado"])
df = df.set_index("Data")

FIRST_DAY = date(YEAR, 1, 1)
LAST_DAY = date(YEAR, 12, 31)

print(df.loc[FIRST_DAY:LAST_DAY])
