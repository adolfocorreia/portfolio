import unittest

from retriever import (get_cdi_retriever,
                       get_debentures_retriever,
                       get_directtreasure_retriever,
                       get_bovespa_retriever)


class DataRetrieverTestCase(unittest.TestCase):
    """Tests for DataRetriver classes"""

    def test_cdi(self):
        print
        dr = get_cdi_retriever()
        self.assertIsNotNone(dr)
        self.assertEqual(
            dr.get_variation("CDI", "2014-01-02", "2014-01-03"),
            round((0.0977 + 1.0)**(1.0 / 252.0) - 1.0, 8)
        )
        self.assertEqual(
            dr.get_variation("CDI", "2014-01-03", "2015-01-03"),
            0.10821161
        )

    def test_debentures(self):
        print
        dr = get_debentures_retriever()
        self.assertIsNotNone(dr)
        self.assertAlmostEqual(
            dr.get_value("RDVT11", "2014-01-02"),
            1069.734504
        )
        self.assertAlmostEqual(
            dr.get_value("TEPE31", "2014-01-03"),
            1021.587536
        )
        self.assertAlmostEqual(
            dr.get_value("RDVT11", "2015-01-01"),
            1157.962552
        )
        self.assertAlmostEqual(
            dr.get_value("TEPE31", "2015-01-01"),
            1268.458594
        )

    def test_directtreasure(self):
        print
        dr = get_directtreasure_retriever()
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
        self.assertAlmostEqual(
            dr.get_value("LFT_070315", "2015-01-01"),
            6537.17
        )

    def test_bovespa(self):
        print
        dr = get_bovespa_retriever()
        self.assertIsNotNone(dr)
        self.assertAlmostEqual(
            dr.get_value("ITUB3", "2014-01-02"),
            29.43
        )
        self.assertAlmostEqual(
            dr.get_value("PETR3", "2014-01-02"),
            15.82
        )
        self.assertAlmostEqual(
            dr.get_value("BBDC3", "2015-01-01"),
            34.32
        )


if __name__ == '__main__':
    suite = unittest.TestLoader().loadTestsFromTestCase(DataRetrieverTestCase)
    unittest.TextTestRunner(verbosity=2).run(suite)
