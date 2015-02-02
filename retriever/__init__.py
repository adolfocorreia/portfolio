from .retriever import DataRetriever

from .cdi import CDIRetriever
from .debentures import DebenturesRetriever
from .directtreasure import DirectTreasureRetriever
from .bovespa import BovespaRetriever


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


def get_bovespa_retriever():
    if get_bovespa_retriever.instance is None:
        get_bovespa_retriever.instance = BovespaRetriever()
    return get_bovespa_retriever.instance
get_bovespa_retriever.instance = None


__all__ = [
    "DataRetriever",
    "get_cdi_retriever",
    "get_debentures_retriever",
    "get_dt_retriever",
    "get_bovespa_retriever",
]
