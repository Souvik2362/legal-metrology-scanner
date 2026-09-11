"""Unit tests for text normalizer and information extraction pipeline."""

import os
import sys
import unittest

# Ensure parent directory is in python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from backend.extraction.normalizer import normalize_text
from backend.extraction.extractors import (
    extract_mrp,
    extract_net_quantity,
    extract_manufacturer_packer,
    extract_batch_lot,
    extract_mfg_date,
    extract_best_before,
    extract_consumer_care,
    extract_all_declarations,
)



class TestNormalizer(unittest.TestCase):

    def test_normalize_currency_and_units(self):
        raw = "MRP Rs. 189.00 Net Vol. 1 Ltr"
        normalized = normalize_text(raw)
        self.assertIn("₹", normalized)
        self.assertIn("1 L", normalized)

    def test_fix_ocr_typos(self):
        raw = "MRP ₹ 1O0.00 Net Wt. 50o g"
        normalized = normalize_text(raw)
        self.assertIn("₹ 100.00", normalized)


class TestExtractors(unittest.TestCase):

    def test_extract_mrp(self):
        sample = "MRP Rs 189.00 (incl. of all taxes)"
        res = extract_mrp(normalize_text(sample))
        self.assertIsNotNone(res)
        self.assertEqual(res["amount"], "189.00")
        self.assertTrue(res["has_tax_clause"])

    def test_extract_net_quantity(self):
        sample = "Net Quantity: 1 L"
        res = extract_net_quantity(normalize_text(sample))
        self.assertIsNotNone(res)
        self.assertEqual(res["value"], "1 L")

        sample2 = "Net Wt. 500 g"
        res2 = extract_net_quantity(normalize_text(sample2))
        self.assertIsNotNone(res2)
        self.assertEqual(res2["value"], "500 g")

    def test_extract_manufacturer_packer(self):
        sample = "Manufactured by: Sunridge Agro Pvt. Ltd., MIDC Industrial Area, Nashik, Maharashtra 422010"
        res = extract_manufacturer_packer(sample)
        self.assertIsNotNone(res)
        self.assertIn("Sunridge Agro", res["value"])

    def test_extract_batch_lot(self):
        sample = "Batch No: SR24B0417"
        res = extract_batch_lot(sample)
        self.assertIsNotNone(res)
        self.assertEqual(res["value"], "SR24B0417")

    def test_extract_mfg_date(self):
        sample = "MFD: 03/2026"
        res = extract_mfg_date(sample)
        self.assertIsNotNone(res)
        self.assertEqual(res["value"], "03/2026")

    def test_extract_best_before(self):
        sample = "Best Before 6 months from packaging"
        res = extract_best_before(sample)
        self.assertIsNotNone(res)
        self.assertIn("Best Before 6 months", res["value"])

    def test_extract_consumer_care(self):
        sample = "For complaints contact: care@sunridge.com or Toll Free: 1800-123-4567"
        res = extract_consumer_care(sample)
        self.assertIsNotNone(res)
        self.assertTrue(res["has_email"])
        self.assertTrue(res["has_phone"])

    def test_extract_all_declarations(self):
        full_label = """
        Sunridge Refined Sunflower Oil
        Net Quantity: 1 L
        MRP ₹ 189.00 (incl. of all taxes)
        Batch No: SR24B0417
        MFD: 03/2026
        Best Before 9 months from mfg
        Manufactured by: Sunridge Agro Pvt. Ltd., MIDC Nashik 422010
        Customer Care: care@sunridge.com, Ph: 1800-123-4567
        """
        results = extract_all_declarations(full_label)
        self.assertIsNotNone(results["mrp"])
        self.assertIsNotNone(results["net_quantity"])
        self.assertIsNotNone(results["manufacturer_packer"])
        self.assertIsNotNone(results["batch_lot"])
        self.assertIsNotNone(results["mfg_date"])
        self.assertIsNotNone(results["best_before"])
        self.assertIsNotNone(results["consumer_care"])


if __name__ == "__main__":
    unittest.main()
