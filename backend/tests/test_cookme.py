"""Unit test validating real Indian spice product label extraction (Cookme Cumin)."""

import os
import sys
import unittest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from backend.extraction.extractors import extract_all_declarations
from backend.compliance.engine import run_compliance_assessment
from backend.compliance.models import CheckStatus


class TestCookmeLabel(unittest.TestCase):

    def test_cookme_cumin_extraction(self):
        sample_label_text = """
        Batch No.: J8/32/027 H
        Date of Pkg.: 25.04.26
        Use By: 25.12.26
        M.R.P. ₹ (Incl. of all taxes) : Rs. 5.00
        Net Qty : 6 g
        U.S.P. ₹ : Rs. 0.83/g
        Manufactured by: Krishna Chandra Dutta (Spice) Private Limited
        Vill & P.O.- Belumilki, Mouza- Piarapur, Srirampore, Pin: 712223
        Marketed by: J.D. Marketing Private Limited, "Cookme House", 235, Maharshi Debendra Road, Kolkata-700 007
        Product of India
        Store in cool & dry place.
        Ingredient : Whole Cumin
        For Feedback / Complaint:
        Please write to Consumer Care Executive at
        235, Maharshi Debendra Road, Kolkata - 700 007.
        e-mail: consumercare@cookme.in
        Or Call us any working day during working hours on 033 2259 9247
        """

        extracted = extract_all_declarations(sample_label_text)

        # 1. MRP
        self.assertIsNotNone(extracted["mrp"])
        self.assertEqual(extracted["mrp"]["amount"], "5.00")
        self.assertTrue(extracted["mrp"]["has_tax_clause"])

        # 2. Net Quantity
        self.assertIsNotNone(extracted["net_quantity"])
        self.assertEqual(extracted["net_quantity"]["value"], "6 g")

        # 3. Manufacturer
        self.assertIsNotNone(extracted["manufacturer_packer"])
        self.assertEqual(extracted["manufacturer_packer"]["role"], "manufacturer")

        # 4. Batch
        self.assertIsNotNone(extracted["batch_lot"])
        self.assertIn("J8/32/027", extracted["batch_lot"]["value"])

        # 5. Date of Pkg
        self.assertIsNotNone(extracted["mfg_date"])
        self.assertIn("25.04.26", extracted["mfg_date"]["value"])

        # 6. Best Before / Use By
        self.assertIsNotNone(extracted["best_before"])
        self.assertIn("25.12.26", extracted["best_before"]["value"])

        # 7. Consumer Care
        self.assertIsNotNone(extracted["consumer_care"])
        self.assertTrue(extracted["consumer_care"]["has_email"])
        self.assertTrue(extracted["consumer_care"]["has_phone"])

        # 8. Unit Sale Price
        self.assertIsNotNone(extracted["unit_sale_price"])
        self.assertIn("0.83", extracted["unit_sale_price"]["value"])

        # 9. Country of Origin
        self.assertIsNotNone(extracted["country_of_origin"])
        self.assertEqual(extracted["country_of_origin"]["value"], "India")

        # 10. Full Compliance Assessment
        result = run_compliance_assessment(extracted, avg_ocr_confidence=0.92, raw_ocr_text=sample_label_text)
        self.assertEqual(result.product.brand, "Cookme")
        self.assertIn("Whole Cumin", result.product.name)

        # Verify all 9 checks are DETECTED
        statuses = {c.id: c.status for c in result.checks}
        self.assertEqual(statuses["mrp"], CheckStatus.DETECTED)
        self.assertEqual(statuses["net_quantity"], CheckStatus.DETECTED)
        self.assertEqual(statuses["manufacturer_packer"], CheckStatus.DETECTED)
        self.assertEqual(statuses["batch_lot"], CheckStatus.DETECTED)
        self.assertEqual(statuses["mfg_date"], CheckStatus.DETECTED)
        self.assertEqual(statuses["best_before"], CheckStatus.DETECTED)
        self.assertEqual(statuses["consumer_care"], CheckStatus.DETECTED)
        self.assertEqual(statuses["unit_sale_price"], CheckStatus.DETECTED)
        self.assertEqual(statuses["country_of_origin"], CheckStatus.DETECTED)


if __name__ == "__main__":
    unittest.main()
