import sys
import os
sys.path.insert(0, os.path.abspath("."))
import json
from backend.ocr.ocr_engine import run_ocr_pipeline

with open("Test_Images/product_02.jpg", "rb") as f:
    res = run_ocr_pipeline(f.read())

print("Total lines:", res.get("line_count"))
with open("p02_lines.txt", "w", encoding="utf-8") as out:
    for line in res.get("lines", []):
        out.write(f"[{line['orientation']}] {line['text']}\n")
print("Saved to p02_lines.txt")
