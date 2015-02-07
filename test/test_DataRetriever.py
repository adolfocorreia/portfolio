import unittest

from retriever import (
    get_cdi_retriever,
    get_debentures_retriever,
    get_directtreasure_retriever,
    get_bovespa_retriever,
    get_index_retriever,
)


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
        self.assertEqual(
            dr.get_variation("CDI", "2014-06-25", "2015-02-02"),
            0.06718371
        )
        self.assertEqual(
            dr.get_variation("CDI", "2014-06-25", "2015-02-02", 1.04),
            0.06996239
        )
        self.assertEqual(
            dr.get_variation("CDI", "2014-06-11", "2015-02-02"),
            0.07109966
        )
        self.assertEqual(
            dr.get_variation("CDI", "2014-06-11", "2015-02-02", 1.015),
            0.07220353
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

    def test_index(self):
        print
        ir = get_index_retriever()
        self.assertIsNotNone(ir)

        total = 0.0
        ibrx50 = ir.get_composition("IBrX50")
        self.assertEqual(len(ibrx50), 50)
        for stock in ibrx50:
            total += stock["part"]
        self.assertAlmostEqual(total, 100.0)

        total = 0.0
        ibrx100 = ir.get_composition("IBrX100")
        self.assertEqual(len(ibrx100), 100)
        for stock in ibrx100:
            total += stock["part"]
        self.assertAlmostEqual(total, 100.0)

        total = 0.0
        ifix = ir.get_composition("IFIX")
        for stock in ifix:
            total += stock["part"]
        self.assertAlmostEqual(total, 100.0)

        total = 0.0
        ibovespa = ir.get_composition("Ibovespa")
        for stock in ibovespa:
            total += stock["part"]
        self.assertAlmostEqual(total, 100.0)


if __name__ == '__main__':
    suite = unittest.TestLoader().loadTestsFromTestCase(DataRetrieverTestCase)
    unittest.TextTestRunner(verbosity=2).run(suite)
