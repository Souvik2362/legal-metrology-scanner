"""Unit tests for the Legal Metrology Compliance Engine."""

import os
import sys
import unittest

# Ensure project root is in python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from backend.compliance.models import CheckStatus, ScanResult
from backend.compliance.engine import evaluate_declaration, run_compliance_assessment


class TestComplianceEngine(unittest.TestCase):

    def test_evaluate_mrp_with_tax(self):
        mrp_data = {"value": "₹ 189.00 (incl. of all taxes)", "has_tax_clause": True}
        check = evaluate_declaration("mrp", mrp_data, avg_ocr_confidence=0.95)
        self.assertEqual(check.status, CheckStatus.DETECTED)
        self.assertIsNone(check.reason)

    def test_evaluate_mrp_without_tax(self):
        mrp_data = {"value": "₹ 189.00", "has_tax_clause": False}
        check = evaluate_declaration("mrp", mrp_data, avg_ocr_confidence=0.95)
        self.assertEqual(check.status, CheckStatus.POTENTIAL_ISSUE)
        self.assertIn("inclusive of all taxes", check.reason)

    def test_evaluate_low_ocr_confidence(self):
        mrp_data = {"value": "₹ 189.00", "has_tax_clause": True}
        check = evaluate_declaration("mrp", mrp_data, avg_ocr_confidence=0.45)
        self.assertEqual(check.status, CheckStatus.MANUAL_VERIFICATION)
        self.assertIn("OCR confidence is below threshold", check.reason)

    def test_evaluate_missing_required_declaration(self):
        check = evaluate_declaration("net_quantity", None, avg_ocr_confidence=0.95)
        self.assertEqual(check.status, CheckStatus.POTENTIAL_ISSUE)
        self.assertIn("was not detected", check.reason)

    def test_run_compliance_assessment_full(self):
        sample_extracted = {
            "mrp": {"value": "₹ 189.00 (incl. of all taxes)", "has_tax_clause": True},
            "net_quantity": {"value": "1 L"},
            "manufacturer_packer": {"value": "Sunridge Agro Pvt. Ltd."},
            "batch_lot": {"value": "SR24B0417"},
            "mfg_date": {"value": "03/2026"},
            "best_before": {"value": "Best before 9 months"},
            "consumer_care": {"value": "Email: care@sunridge.com"},
        }
        res = run_compliance_assessment(sample_extracted, avg_ocr_confidence=0.95, image_url="blob:sample")
        self.assertIsInstance(res, ScanResult)
        self.assertEqual(len(res.checks), 7)
        self.assertEqual(res.product.netQuantity, "1 L")
        self.assertEqual(res.product.mrp, "₹ 189.00 (incl. of all taxes)")


if __name__ == "__main__":
    unittest.main()
