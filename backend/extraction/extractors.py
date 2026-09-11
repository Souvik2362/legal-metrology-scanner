"""Modular Regex and Keyword Extractor Pipeline for Legal Metrology Product Declarations."""

import re
from typing import Dict, Any, Optional
from backend.extraction.normalizer import normalize_text


def extract_mrp(text: str) -> Optional[Dict[str, Any]]:
    """Extract Maximum Retail Price (MRP) declaration (Rule 6(1)(e))."""
    # Pattern matching MRP value
    mrp_pattern = re.compile(
        r"(?:MRP|M\.R\.P\.|Max\.?\s*Retail\s*Price|Sale\s*Price)[\s:\.]*(?:₹|Rs\.?)?\s*([\d,]+\.?\d*)",
        re.IGNORECASE,
    )
    match = mrp_pattern.search(text)
    if not match:
        # Fallback search for currency symbol followed by amount if MRP keyword is nearby
        fallback_pattern = re.compile(r"₹\s*([\d,]+\.?\d*)")
        match = fallback_pattern.search(text)
        if not match:
            return None

    amount = match.group(1).replace(",", "")
    formatted_reading = f"₹ {amount}"

    # Check for tax inclusion clause
    tax_pattern = re.compile(
        r"(?:incl\.?\s*of\s*all\s*taxes|inclusive\s*of\s*all\s*taxes|incl\.?\s*taxes)",
        re.IGNORECASE,
    )
    has_tax_clause = bool(tax_pattern.search(text))
    if has_tax_clause:
        formatted_reading += " (incl. of all taxes)"

    return {
        "value": formatted_reading,
        "amount": amount,
        "has_tax_clause": has_tax_clause,
        "raw_match": match.group(0),
    }


def extract_net_quantity(text: str) -> Optional[Dict[str, Any]]:
    """Extract Net Quantity declaration (Rule 6(1)(c) + Rule 11 + Rule 12)."""
    # Explicit Net Quantity pattern
    explicit_pattern = re.compile(
        r"(?:Net\s*(?:Qty|Quantity|Wt|Weight|Vol|Volume|Contents)?)[\s:\.]*([\d\.]+\s*(?:g|kg|ml|l|n|pcs|units))\b",
        re.IGNORECASE,
    )
    match = explicit_pattern.search(text)

    if not match:
        # Isolated standalone unit pattern (e.g. "500 g", "1 L", "250 ml")
        standalone_pattern = re.compile(
            r"\b(\d+(?:\.\d+)?\s*(?:g|kg|ml|L|N))\b"
        )
        match = standalone_pattern.search(text)

    if not match:
        return None

    value = match.group(1).strip()
    return {
        "value": value,
        "raw_match": match.group(0),
    }


def extract_manufacturer_packer(text: str) -> Optional[Dict[str, Any]]:
    """Extract Manufacturer / Packer / Importer name and address (Rule 6(1)(a))."""
    keywords_pattern = re.compile(
        r"(?:Manufactured\s*by|Mfg\s*by|Packed\s*by|Pkd\s*by|Marketed\s*by|Imported\s*by|Mfd\s*&\s*Pkd\s*by|Manufacturer|Packer|Importer)[\s:\.]*(.+)",
        re.IGNORECASE,
    )
    match = keywords_pattern.search(text)

    if match:
        line_match = match.group(1).strip()
        # Take up to 2-3 lines of context if address spans multiple lines
        lines = [line_match]
        remaining_text = text[match.end():]
        for line in remaining_text.split("\n")[:2]:
            clean_line = line.strip()
            if clean_line and not re.search(r"(?:MRP|Net Qty|Batch|MFD|EXP)", clean_line, re.I):
                lines.append(clean_line)
            else:
                break
        address = ", ".join(lines)
        return {
            "value": address,
            "raw_match": match.group(0),
        }

    # Search for pincode / address heuristics if explicit keyword missing
    pincode_match = re.search(r"([A-Za-z0-9\s,\.-]+(?:Pvt\.?\s*Ltd\.?|Ltd\.?|Agro|Industries|Private Limited)[A-Za-z0-9\s,\.-]+\d{6})", text, re.IGNORECASE)
    if pincode_match:
        return {
            "value": pincode_match.group(1).strip(),
            "raw_match": pincode_match.group(0),
        }

    return None


def extract_batch_lot(text: str) -> Optional[Dict[str, Any]]:
    """Extract Batch / Lot number (Rule 6(1)(b))."""
    batch_pattern = re.compile(
        r"(?:Batch\s*(?:No|#)?|Lot\s*(?:No|#)?|B\.?\s*No|L\.?\s*No|B/No)[\s:\.]*([A-Za-z0-9\-\/]+)",
        re.IGNORECASE,
    )

    match = batch_pattern.search(text)
    if not match:
        return None

    return {
        "value": match.group(1).strip(),
        "raw_match": match.group(0),
    }


def extract_mfg_date(text: str) -> Optional[Dict[str, Any]]:
    """Extract Date of manufacture / packaging / import (Rule 6(1)(d))."""
    date_pattern = re.compile(
        r"(?:Mfg|Pkd|Packed|Date of Pkg|MFD|DOM|Date)[\s:\.]*(\d{2}[\/\.-]\d{4}|\d{2}[\/\.-]\d{2}[\/\.-]\d{4}|[A-Za-z]{3}\s*\d{4}|\d{2}\/\d{2})",
        re.IGNORECASE,
    )
    match = date_pattern.search(text)
    if not match:
        # Fallback date pattern MM/YYYY or MM-YYYY
        fallback = re.search(r"\b(\d{2}\/\d{4})\b", text)
        if fallback:
            return {
                "value": fallback.group(1),
                "raw_match": fallback.group(0),
            }
        return None

    return {
        "value": match.group(1).strip(),
        "raw_match": match.group(0),
    }


def extract_best_before(text: str) -> Optional[Dict[str, Any]]:
    """Extract Best Before / Use By / Expiry declaration (Rule 6(1)(da))."""
    exp_pattern = re.compile(
        r"(?:Best\s*Before|Use\s*By|Expiry|Exp\.?\s*Date|EXP)[\s:\.]*([^\n\.,]+)",
        re.IGNORECASE,
    )
    match = exp_pattern.search(text)
    if not match:
        return None

    return {
        "value": match.group(0).strip(),
        "details": match.group(1).strip(),
        "raw_match": match.group(0),
    }


def extract_consumer_care(text: str) -> Optional[Dict[str, Any]]:
    """Extract Consumer Care details (Rule 6(1)(f))."""
    email_match = re.search(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b", text)
    phone_match = re.search(r"\b(?:1800[-\s]?\d{3}[-\s]?\d{4}|\+?91[-\s]?[6-9]\d{9}|0\d{2,4}[-\s]?\d{6,8}|Ph[\s:\.]*\d+)\b", text, re.IGNORECASE)
    care_text_match = re.search(r"(?:Customer\s*Care|Consumer\s*Care|For\s*Complaints|Feedback)[\s:\.][^\n]+", text, re.IGNORECASE)

    parts = []
    if care_text_match:
        parts.append(care_text_match.group(0).strip())
    if email_match:
        parts.append(f"Email: {email_match.group(0)}")
    if phone_match:
        parts.append(f"Ph: {phone_match.group(0)}")

    if not parts:
        return None

    return {
        "value": ", ".join(parts),
        "has_email": bool(email_match),
        "has_phone": bool(phone_match),
    }


def extract_all_declarations(text: str) -> Dict[str, Optional[Dict[str, Any]]]:
    """Master extraction function running all 7 Legal Metrology field extractors."""
    normalized = normalize_text(text)
    return {
        "mrp": extract_mrp(normalized),
        "net_quantity": extract_net_quantity(normalized),
        "manufacturer_packer": extract_manufacturer_packer(normalized),
        "batch_lot": extract_batch_lot(normalized),
        "mfg_date": extract_mfg_date(normalized),
        "best_before": extract_best_before(normalized),
        "consumer_care": extract_consumer_care(normalized),
    }
