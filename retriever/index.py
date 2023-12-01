import inspect
import os

import pandas as pd
from playwright.sync_api import sync_playwright

from .retriever import is_file_up_to_date


class IndexRetriever:
    __base_URL = "https://sistemaswebb3-listados.b3.com.br/indexPage/day"

    def __init__(self):
        module_file = inspect.getfile(inspect.currentframe())
        module_dir = os.path.dirname(os.path.abspath(module_file))
        self.data_directory = module_dir + "/data_index"

    def get_composition(self, index):
        assert isinstance(index, str)
        assert len(index) == 4

        url = f"{IndexRetriever.__base_URL}/{index}?language=en-us"
        file_name = os.path.join(self.data_directory, f"{index}.csv")

        if not is_file_up_to_date(file_name):
            with sync_playwright() as p:
                page = p.firefox.launch().new_page()
                page.goto(url)
                with page.expect_download() as download:
                    page.get_by_text("Download").click()
                download.value.save_as(file_name)
            assert is_file_up_to_date(file_name)

        columns = ["code", "name", "stockType", "quantity", "part"]
        df = pd.read_csv(
            file_name,
            engine="python",
            header=0,
            names=columns + [""],
            skiprows=2,
            skipfooter=2,
        ).iloc[:, :-1]
        df["part"] /= 100.0

        return df.to_dict("records")
