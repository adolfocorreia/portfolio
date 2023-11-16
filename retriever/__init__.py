from .retriever import DataRetriever

from .bovespa import BovespaRetriever
from .cdi import CDIRetriever
from .debentures import DebenturesRetriever
from .directtreasure import DirectTreasureRetriever
from .fund import FundRetriever
from .ipca import IPCARetriever

from .index import IndexRetriever


def get_bovespa_retriever():
    if get_bovespa_retriever.instance is None:
        get_bovespa_retriever.instance = BovespaRetriever()
    return get_bovespa_retriever.instance


get_bovespa_retriever.instance = None


def get_cdi_retriever():
    if get_cdi_retriever.instance is None:
        get_cdi_retriever.instance = CDIRetriever()
    return get_cdi_retriever.instance


get_cdi_retriever.instance = None


def get_debentures_retriever():
    if get_debentures_retriever.instance is None:
        get_debentures_retriever.instance = DebenturesRetriever()
    return get_debentures_retriever.instance


get_debentures_retriever.instance = None


def get_directtreasure_retriever():
    if get_directtreasure_retriever.instance is None:
        get_directtreasure_retriever.instance = DirectTreasureRetriever()
    return get_directtreasure_retriever.instance


get_directtreasure_retriever.instance = None


def get_fund_retriever():
    if get_fund_retriever.instance is None:
        get_fund_retriever.instance = FundRetriever()
    return get_fund_retriever.instance


get_fund_retriever.instance = None


def get_ipca_retriever():
    if get_ipca_retriever.instance is None:
        get_ipca_retriever.instance = IPCARetriever()
    return get_ipca_retriever.instance


get_ipca_retriever.instance = None


def get_index_retriever():
    if get_index_retriever.instance is None:
        get_index_retriever.instance = IndexRetriever()
    return get_index_retriever.instance


get_index_retriever.instance = None


__all__ = [
    "DataRetriever",
    "get_bovespa_retriever",
    "get_cdi_retriever",
    "get_debentures_retriever",
    "get_dt_retriever",
    "get_fund_retriever",
    "get_ipca_retriever",
    "get_index_retriever",
]
