import unittest

from retriever.cdi import CDIRetriever
from retriever.debentures import DebenturesRetriever
from retriever.dt import DirectTreasureRetriever
from retriever.stocks import StocksRetriever


class DataRetrieverTestCase(unittest.TestCase):
    """Tests for DataRetriver classes"""

    def test_cdi(self):
        print
        dr = CDIRetriever()
        self.assertIsNotNone(dr)
        self.assertAlmostEqual(
            dr.get_variation("CDI", "2014-01-02", "2014-01-03"),
            (0.0977 + 1.0)**(1.0 / 252.0) - 1.0
        )

    def test_debentures(self):
        print
        dr = DebenturesRetriever()
        self.assertIsNotNone(dr)
        self.assertAlmostEqual(
            dr.get_value("RDVT11", "2014-01-02"),
            1069.734504
        )
        self.assertAlmostEqual(
            dr.get_value("TEPE31", "2014-01-03"),
            1021.587536
        )

    def test_dt(self):
        print
        dr = DirectTreasureRetriever()
        self.assertIsNotNone(dr)
        self.assertAlmostEqual(
            dr.get_value("LFT_070314", "2014-01-02"),
            5897.21
        )
        self.assertAlmostEqual(
            dr.get_value("LTN_010115", "2014-01-02"),
            902.97
        )
        self.assertAlmostEqual(
            dr.get_value("NTN-B_Principal_150515", "2014-01-02"),
            2223.61
        )
        self.assertAlmostEqual(
            dr.get_value("NTN-F_010117", "2014-01-02"),
            945.17
        )

    def test_stocks(self):
        print
        dr = StocksRetriever()
        self.assertIsNotNone(dr)
        # self.assertAlmostEqual(
        #     dr.get_value("ITUB3", "2014-01-02"),
        #     25.88
        # )
        # self.assertAlmostEqual(
        #     dr.get_value("PETR3", "2014-01-02"),
        #     15.27
        # )


if __name__ == '__main__':
    suite = unittest.TestLoader().loadTestsFromTestCase(DataRetrieverTestCase)
    unittest.TextTestRunner(verbosity=2).run(suite)
