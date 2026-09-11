"""Text normalization and OCR cleaning utilities for Indian product label text."""

import re


def normalize_text(text: str) -> str:
    """Normalize raw OCR text to standardize symbols, units, and spacing."""
    if not text:
        return ""

    # Replace multiple spaces/tabs with single space (preserve newlines)
    text = re.sub(r"[ \t]+", " ", text)

    # Standardize currency representations (Rs., RS, INR -> ₹)
    # Handles both 'Rs. 5.00' and 'Rs.5.00'
    text = re.sub(r"(?:Rs\.?|RS|INR)\s*", "₹ ", text, flags=re.IGNORECASE)

    # Fix common PaddleOCR confusion where Indian Rupee symbol '₹' is misrecognized as 'E', '?', or '7' (only when not part of a number)
    # Examples: 'M.R.PE' -> 'M.R.P. ₹ :', 'M.R.P. ?' -> 'M.R.P. ₹ :', 'M.R.P. 7 (Incl.' -> 'M.R.P. ₹ (Incl.'
    # Protects genuine prices like 'MRP 70.00' from being corrupted into 'MRP ₹ : 0.00'
    text = re.sub(r"((?:MRP|M\.R\.P\.)\s*)(?:[E\?]|7(?!\s*\d|\.\d))\s*", r"\1₹ : ", text, flags=re.IGNORECASE)
    text = re.sub(r"((?:U\.?S\.?P\.?|Unit\s*Sale\s*Price)\s*)(?:[E\?N]|7(?!\s*\d|\.\d))\s*", r"\1₹ : ", text, flags=re.IGNORECASE)

    # Standardize common OCR typos in tax inclusion statements (e.g. 'fall taxes' -> 'all taxes')
    text = re.sub(r"\b(?:fall|alll|al)\s+taxes\b", "all taxes", text, flags=re.IGNORECASE)

    # Standardize price notation with trailing slash or dash (e.g. '10.00/-' or '10.00/')
    text = re.sub(r"(\d+\.\d{2})\s*\/\s*(?:[\-\s]|$)", r"\1 ", text)

    # Fix OCR typos in Net Quantity declarations (e.g., 'Net aty' -> 'Net Qty')
    text = re.sub(r"\bNet\s*(?:aty|oty|otv)\b", "Net Qty", text, flags=re.IGNORECASE)

    # Fix dot-matrix unit sale price where '/g' is misrecognized as '/9'
    text = re.sub(r"(\d+\.\d+)\s*\/\s*9\b", r"\1/g", text)

    # Normalize common weight/volume unit variants
    # Liters
    text = re.sub(r"\b(?:Ltr|Ltrs|Litre|Litres|LITRES)\b", "L", text, flags=re.IGNORECASE)
    # Milliliters
    text = re.sub(r"\b(?:M\.?L\.?|ml|Ml|mL)\b", "ml", text)
    # Grams
    text = re.sub(r"\b(?:gm|gms|grm|grams|GRAMS)\b", "g", text, flags=re.IGNORECASE)
    # Kilograms
    text = re.sub(r"\b(?:kg|kgs|kilo|kilograms)\b", "kg", text, flags=re.IGNORECASE)
    # Number of units / pieces
    text = re.sub(r"\b(?:pcs|pieces|units)\b", "N", text, flags=re.IGNORECASE)

    # Fix OCR typos inside price or quantity patterns
    text = fix_ocr_price_and_numbers(text)

    return text.strip()


def fix_ocr_price_and_numbers(text: str) -> str:
    """Fix common OCR digit/letter confusion inside prices and numeric declarations.

    Common misread examples:
    - '₹ 1O0.00' -> '₹ 100.00'
    - '1.O kg' -> '1.0 kg'
    """
    # Replace uppercase 'O' or lowercase 'o' surrounded by digits with '0'
    text = re.sub(r"(?<=\d)[Oo](?=\d|\s*₹|\s*g|\s*kg|\s*ml|\s*L)", "0", text)
    text = re.sub(r"(?<=\d\.)[Oo]\b", "0", text)
    text = re.sub(r"₹\s*([0-9]*)[Oo]([0-9]*)", r"₹ \g<1>0\g<2>", text)

    # Clean double spaces that may have been created
    text = re.sub(r" +", " ", text)

    return text
