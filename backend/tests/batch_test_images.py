"""Batch Evaluation Script for Test_Images Dataset.

Runs full Legal Metrology Compliance Scan on images in Test_Images/ and outputs
structured evaluation summaries for accuracy and statutory compliance validation.
"""

import os
import sys
import json
import time
import argparse

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from backend.ocr.ocr_engine import run_ocr_pipeline
from backend.extraction.extractors import extract_all_declarations
from backend.compliance.engine import run_compliance_assessment


def evaluate_image(image_path: str):
    start_t = time.time()
    with open(image_path, "rb") as f:
        image_bytes = f.read()

    ocr_res = run_ocr_pipeline(image_bytes)
    raw_text = ocr_res.get("raw_text", "")
    avg_conf = ocr_res.get("avg_confidence", 0.0)
    line_count = ocr_res.get("line_count", 0)

    extracted = extract_all_declarations(raw_text)
    assessment = run_compliance_assessment(
        extracted_declarations=extracted,
        avg_ocr_confidence=avg_conf,
        image_url=os.path.basename(image_path),
        raw_ocr_text=raw_text,
    )
    elapsed = round(time.time() - start_t, 2)

    result_summary = {
        "filename": os.path.basename(image_path),
        "elapsed_seconds": elapsed,
        "ocr_status": ocr_res.get("status"),
        "line_count": line_count,
        "confidence": round(avg_conf * 100, 1),
        "product": {
            "brand": assessment.product.brand,
            "name": assessment.product.name,
            "net_quantity": assessment.product.netQuantity,
            "mrp": assessment.product.mrp,
            "batch": assessment.product.batchNumber,
            "mfg_date": assessment.product.mfgDate,
            "best_before": assessment.product.bestBefore,
            "usp": assessment.product.unitSalePrice,
            "country_of_origin": assessment.product.countryOfOrigin,
            "packer": assessment.product.packerAddress[:50] + "..." if assessment.product.packerAddress else None,
        },
        "checks": [
            {
                "id": c.id,
                "label": c.label,
                "status": c.status.value,
                "reading": c.reading,
            }
            for c in assessment.checks
        ],
    }

    return result_summary, raw_text


if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass


def print_summary(res: dict):
    print("=" * 65)
    print(f"FILE: {res['filename']}  (Time: {res['elapsed_seconds']}s, OCR Lines: {res['line_count']}, Conf: {res['confidence']}%)")
    print("=" * 65)
    p = res["product"]
    print(f"  Brand:    {p['brand']}")
    print(f"  Name:     {p['name']}")
    print(f"  Net Qty:  {p['net_quantity']}")
    print(f"  MRP:      {p['mrp']}")
    print(f"  Batch:    {p['batch']}")
    print(f"  MFD:      {p['mfg_date']}")
    print(f"  Expiry:   {p['best_before']}")
    print(f"  USP:      {p['usp']}")
    print(f"  Origin:   {p['country_of_origin']}")
    print(f"  Packer:   {p['packer']}")
    print("-" * 65)
    detected_count = sum(1 for c in res["checks"] if c["status"] == "detected")
    issue_count = sum(1 for c in res["checks"] if c["status"] == "potential_issue")
    verify_count = sum(1 for c in res["checks"] if c["status"] == "manual_verification")
    print(f"  RESULTS: {detected_count} DETECTED | {issue_count} POTENTIAL ISSUE | {verify_count} TO VERIFY")
    for c in res["checks"]:
        reading_str = f" -> {c['reading']}" if c['reading'] else ""
        print(f"    [{c['status'].upper()[:4]}] {c['id']}{reading_str}")
    print("=" * 65 + "\n")


def main():
    parser = argparse.ArgumentParser(description="Batch test Legal Metrology Scanner on Test_Images")
    parser.add_argument("--files", nargs="*", help="Specific filenames in Test_Images to test")
    parser.add_argument("--limit", type=int, default=5, help="Number of images to evaluate (default 5)")
    args = parser.parse_args()

    test_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "Test_Images"))
    if not os.path.exists(test_dir):
        print(f"Test directory not found: {test_dir}")
        sys.exit(1)

    if args.files:
        filenames = args.files
    else:
        filenames = sorted(os.listdir(test_dir))[:args.limit]

    all_results = []
    raw_texts_map = {}
    print(f"\nStarting evaluation of {len(filenames)} images from {test_dir}...\n")

    for fname in filenames:
        img_path = os.path.join(test_dir, fname)
        if not os.path.isfile(img_path):
            continue
        try:
            res, raw_text = evaluate_image(img_path)
            all_results.append(res)
            raw_texts_map[fname] = raw_text
            print_summary(res)
        except Exception as e:
            print(f"Error evaluating {fname}: {e}")

    out_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "batch_test_results.json"))
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(all_results, f, indent=2)

    raw_out = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "batch_raw_texts.json"))
    with open(raw_out, "w", encoding="utf-8") as f:
        json.dump(raw_texts_map, f, indent=2)

    print(f"Batch evaluation complete! Detailed JSON saved to: {out_path}")


if __name__ == "__main__":
    main()
