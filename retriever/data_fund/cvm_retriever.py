#!/usr/bin/env python

import re
import sys
import mechanize
import http.cookiejar
from datetime import datetime
from time import sleep
from bs4 import BeautifulSoup


assert len(sys.argv) == 3
cnpj = sys.argv[1]
assert re.match(r"^[0-9]{2}\.[0-9]{3}\.[0-9]{3}\/[0-9]{4}-[0-9]{2}$", cnpj)
year = int(sys.argv[2])
assert re.match(r"^(19|20)[0-9]{2}$", str(year))

home_url = "http://cvmweb.cvm.gov.br/SWB/Sistemas/SCW/CPublica/CConsolFdo/FormBuscaParticFdo.aspx"

# Browser
br = mechanize.Browser()
br.set_handle_equiv(True)
br.set_handle_redirect(True)
br.set_handle_referer(True)
br.set_handle_robots(False)
br.addheaders = [("User-agent", "Mozilla/5.0")]

# Cookie Jar
cj = http.cookiejar.LWPCookieJar()
br.set_cookiejar(cj)

# Debugging messages
DEBUG = False
if DEBUG:
    br.set_debug_http(True)
    br.set_debug_redirects(True)
    br.set_debug_responses(True)

# Open first page
response = br.open(home_url)

# Submit form to search for funds
br.select_form(nr=0)
br.set_all_readonly(False)
br.form["txtCNPJNome"] = cnpj
br.form["ddlTpFdo"] = 0

sleep(1)
response = br.submit()

# Select fund on search results list
# To simulate the __doPostBack javascript function behaviour, we take its
# parameters and use them as the values for the inputs __EVENTTARGET and __EVENTARGUMENT
html2 = response.read()
page = BeautifulSoup(html2, "lxml")
link = str(page.find("a", string=cnpj))
match = re.search("""href="javascript:__doPostBack[(]'(.*?)','(.*?)'[)]".""", link)

br.select_form(nr=0)
br.set_all_readonly(False)
br.form["__EVENTTARGET"] = match.group(1)
br.form["__EVENTARGUMENT"] = match.group(2)

sleep(1)
response = br.submit()

# Select "Daily data" link
sleep(1)
response = br.follow_link(text_regex="Dados")

# Sets months array
now = datetime.now()
if year == now.year:
    months = range(1, now.month + 1)
else:
    months = range(1, 12 + 1)

# For each month
translation_map = str.maketrans("", "", "./-")
for month in months:
    # Select desired month/year in combobox and simulate _doPostBack call
    combobox_value = "{:02d}/{}".format(month, year)
    br.select_form(nr=0)
    br.set_all_readonly(False)
    br.form["ddComptc"] = [combobox_value]
    br.form["__EVENTTARGET"] = "ddComptc"
    br.form["__EVENTARGUMENT"] = ""

    sleep(1)
    response = br.submit()

    # Extract table data to CSV file
    html5 = response.read()
    page = BeautifulSoup(html5.decode("iso-8859-15"), "lxml")
    table = page.find("table", {"id": "dgDocDiario"})
    csv_file = (
        cnpj.translate(translation_map) + "_" + "{}-{:02d}".format(year, month) + ".csv"
    )
    with open(csv_file, "w") as f:
        for tr in table.find_all(recursive=False):
            values = []
            for td in tr.find_all("td"):
                text = td.text.translate({ord("."): None}).replace(",", ".")
                values.append(text)
            f.write(",".join(values))
            f.write("\n")
