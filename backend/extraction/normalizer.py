"""Text normalization and OCR cleaning utilities for Indian product label text."""

import re


def normalize_text(text: str) -> str:
    """Normalize raw OCR text to standardize symbols, units, and spacing."""
    if not text:
        return ""

    # Replace multiple spaces/tabs with single space (preserve newlines)
    text = re.sub(r"[ \t]+", " ", text)

    # Standardize currency representations (Rs., RS, INR -> ₹)
    text = re.sub(r"\b(?:Rs\.?|RS|INR)\b", "₹", text, flags=re.IGNORECASE)

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

    return text
