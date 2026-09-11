"""End-to-End Regression Test on real sample packaging files (product_01.JPG)."""

import os
import sys
import unittest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from backend.ocr.ocr_engine import run_ocr_pipeline
from backend.extraction.extractors import extract_all_declarations
from backend.compliance.engine import run_compliance_assessment
from backend.compliance.models import CheckStatus


class TestRealImagesE2E(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
        cls.image_path = os.path.join(project_root, "product_01.JPG")
        cls.has_image = os.path.exists(cls.image_path)

    def test_product_01_end_to_end(self):
        if not self.has_image:
            self.skipTest("product_01.JPG not found in project root.")

        with open(self.image_path, "rb") as f:
            image_bytes = f.read()

        ocr_res = run_ocr_pipeline(image_bytes)
        self.assertEqual(ocr_res["status"], "success")
        self.assertGreater(ocr_res["line_count"], 10)

        raw_text = ocr_res["raw_text"]
        extracted = extract_all_declarations(raw_text)

        # 1. MRP must be 5.00, NOT 625.12
        self.assertIsNotNone(extracted["mrp"])
        self.assertEqual(extracted["mrp"]["amount"], "5.00")

        # 2. Net quantity must be detected
        self.assertIsNotNone(extracted["net_quantity"])
        self.assertIn(extracted["net_quantity"]["value"], ["5 g", "6 g"])

        # 3. Batch must be J8/32/027H, NOT "No"
        self.assertIsNotNone(extracted["batch_lot"])
        self.assertIn("J8/32/027H", extracted["batch_lot"]["value"])

        # 4. Compliance assessment
        assessment = run_compliance_assessment(
            extracted_declarations=extracted,
            avg_ocr_confidence=ocr_res["avg_confidence"],
            image_url="product_01.JPG",
            raw_ocr_text=raw_text,
        )

        self.assertEqual(assessment.product.brand, "Cookme")
        self.assertIn("Whole Cumin", assessment.product.name)
        self.assertEqual(len(assessment.checks), 9)


if __name__ == "__main__":
    unittest.main()
