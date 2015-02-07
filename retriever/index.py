import requests
from bs4 import BeautifulSoup


class IndexRetriever:

    __base_URL = "http://www.bmfbovespa.com.br/indices/ResumoCarteiraTeorica.aspx?idioma=en-us&Indice="
    _index_URLs = {
        "Ibovespa": __base_URL + "Ibovespa",
        "IBrX100": __base_URL + "IBrX",
        "IBrX50": __base_URL + "IBrX50",
        "IFIX": __base_URL + "IFIX",
        "SMLL": __base_URL + "SMLL",
        "IDIV": __base_URL + "IDIV",
    }

    def get_composition(self, index):
        assert index in IndexRetriever._index_URLs
        url = IndexRetriever._index_URLs[index]

        stocks = []

        session = requests.session()
        content = session.get(url, headers={'Connection': 'close'}).content
        page = BeautifulSoup(content)

        table_id = "ctl00_contentPlaceHolderConteudo_grdResumoCarteiraTeorica_ctl00"
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
            stock["part"] = float(td.span.string)
            row = row.find_next_sibling("tr")
            stocks.append(stock)

        session.close()

        return stocks
