import inspect
import os
import requests
from bs4 import BeautifulSoup


class IndexRetriever:

    __base_URL = "http://bvmf.bmfbovespa.com.br/indices/ResumoCarteiraTeorica.aspx?idioma=en-us&Indice="
    _index_URLs = {
        "Ibovespa": __base_URL + "Ibovespa",
        "IBrX100": __base_URL + "IBrX",
        "IBrX50": __base_URL + "IBrX50",
        "IFIX": __base_URL + "IFIX",
        "SMLL": __base_URL + "SMLL",
        "IDIV": __base_URL + "IDIV",
        "IGCX": __base_URL + "IGC",
        "ISEE": __base_URL + "ISE",
    }

    def __init__(self):
        module_file = inspect.getfile(inspect.currentframe())
        module_dir = os.path.dirname(os.path.abspath(module_file))
        self.data_directory = module_dir + "/data_index"

    def get_composition(self, index):
        assert index in IndexRetriever._index_URLs
        url = IndexRetriever._index_URLs[index]

        stocks = []

        session = requests.session()
        content = str(session.get(url, headers={'Connection': 'close'}).content)
        table_id = "ctl00_contentPlaceHolderConteudo_grdResumoCarteiraTeorica_ctl00"

        file_name = self.data_directory + "/" + index + ".html"
        if table_id in content:
            with open(file_name, "w") as f:
                f.write(content)
        else:
            with open(file_name, "r") as f:
                content = f.read()

        page = BeautifulSoup(content, "lxml")
        row = page.find(id=table_id).tbody.tr
        while row:
            stock = {}
            td = row.td
            stock["code"] = td.span.string
            td = td.find_next_sibling("td")
            stock["name"] = td.span.string
            td = td.find_next_sibling("td")
            stock["stockType"] = td.span.string
            td = td.find_next_sibling("td")
            stock["quantity"] = td.span.string.replace(',', '')
            td = td.find_next_sibling("td")
            stock["part"] = float(td.span.string) / 100.0
            row = row.find_next_sibling("tr")
            stocks.append(stock)

        session.close()

        return stocks
