"""Script to run full Legal Metrology Compliance Scan on product_01.JPG and print clean report."""

import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from backend.ocr.ocr_engine import run_ocr_pipeline
from backend.extraction.extractors import extract_all_declarations
from backend.compliance.engine import run_compliance_assessment


try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass


def scan_file(file_path: str):
    with open(file_path, "rb") as f:
        image_bytes = f.read()

    ocr_res = run_ocr_pipeline(image_bytes)
    raw_text = ocr_res.get("raw_text", "")
    avg_conf = ocr_res.get("avg_confidence", 0.9)

    print("=" * 60)
    print("OCR EXTRACTION SUMMARY")
    print(f"Status: {ocr_res.get('status')}")
    print(f"Detected Text Lines: {ocr_res.get('line_count')}")
    print(f"Average Confidence: {round(avg_conf * 100, 1)}%")
    print("=" * 60)
    print("RAW TEXT EXTRACTED:")
    for line in raw_text.split("\n"):
        if line.strip():
            print("  |", line.encode("ascii", "replace").decode("ascii"))

    extracted = extract_all_declarations(raw_text)
    assessment = run_compliance_assessment(
        extracted_declarations=extracted,
        avg_ocr_confidence=avg_conf,
        image_url=file_path,
        raw_ocr_text=raw_text,
    )

    def _safe(v):
        return str(v).encode("ascii", "replace").decode("ascii") if v else "None"

    print("\n" + "=" * 60)
    print("LEGAL METROLOGY COMPLIANCE ASSESSMENT REPORT")
    print("=" * 60)
    print(f"Product Brand: {_safe(assessment.product.brand)}")
    print(f"Product Name:  {_safe(assessment.product.name)}")
    print(f"Net Quantity:  {_safe(assessment.product.netQuantity)}")
    print(f"MRP:           {_safe(assessment.product.mrp)}")
    print(f"Batch Number:  {_safe(assessment.product.batchNumber)}")
    print(f"Mfg Date:      {_safe(assessment.product.mfgDate)}")
    print(f"Best Before:   {_safe(assessment.product.bestBefore)}")
    print(f"Consumer Care: {_safe(assessment.product.customerCareText)}")
    print(f"Unit Price:    {_safe(assessment.product.unitSalePrice)}")
    print(f"Country Origin:{_safe(assessment.product.countryOfOrigin)}")
    print(f"Packer Addr:   {_safe(assessment.product.packerAddress[:60])}...")
    print("-" * 60)
    print("MANDATORY DECLARATION CHECKS:")
    for c in assessment.checks:
        reading_safe = str(c.reading).encode("ascii", "replace").decode("ascii") if c.reading else "None"
        reason_safe = f" (Reason: {c.reason})" if c.reason else ""
        print(f"  [{c.status.value.upper()}] {c.label}")
        print(f"      Reading: {reading_safe}")
        print(f"      Rule:    {c.ruleRef}{reason_safe}")
    print("=" * 60)


if __name__ == "__main__":
    scan_file("product_01.JPG")
