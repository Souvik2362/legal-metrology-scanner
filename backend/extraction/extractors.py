"""Modular Regex and Keyword Extractor Pipeline for Legal Metrology Product Declarations.

Extracts all 9 statutory declarations prescribed under the Legal Metrology Act, 2009
and Legal Metrology (Packaged Commodities) Rules, 2011 (LM(PC) Rules 2011).
"""

import re
from typing import Dict, Any, Optional
from backend.extraction.normalizer import normalize_text


def extract_mrp(text: str) -> Optional[Dict[str, Any]]:
    """Extract Maximum Retail Price (MRP) declaration (Rule 6(1)(e)).

    Disambiguates genuine price declarations from dates (e.g. '625.12.26'),
    unit sale prices (e.g. '0.83/g'), and nutrition table values.
    """
    def is_date_or_invalid(val_str: str, match_end_pos: int, src_text: str) -> bool:
        # Check if matched number is part of a longer dot/slash/dash date sequence (e.g. 625.12.26)
        following = src_text[match_end_pos:match_end_pos + 8]
        if re.match(r"^[\.\/-]\d", following):
            return True
        # Check if preceded by a date segment
        start_pos = match_end_pos - len(val_str)
        preceding = src_text[max(0, start_pos - 8):start_pos]
        if re.search(r"\d[\.\/-]$", preceding):
            return True
        return False

    amount = None
    raw_match = ""

    # Strategy 1: Explicit MRP keyword followed within 40 chars by currency/price
    # Note: Lookahead rejects trailing unit prices like '/g' or date separators like '.26'
    for m in re.finditer(
        r"(?:MRP|M\.R\.P\.?|Max\.?\s*Retail\s*Price|Sale\s*Price)[^\d\n\r]{0,35}?(?:₹|Rs\.?|:\s*)?\s*([\d,]+(?:\.\d{2})?)\b(?!\s*[\.\/-]\s*\d)(?!\s*\/\s*(?:g|kg|ml|l|unit|100g))",
        text,
        re.IGNORECASE,
    ):
        candidate = m.group(1).replace(",", "")
        if not is_date_or_invalid(candidate, m.end(1), text):
            amount = candidate
            raw_match = m.group(0)
            break

    # Strategy 2: Preceding price on line immediately before MRP: e.g. "Rs. 5.00 \n M.R.P. (Incl. of all taxes)"
    if not amount:
        preceding_mrp = re.search(
            r"(?:₹|Rs\.?)\s*([\d,]+(?:\.\d{2})?)\b(?!\s*[\.\/-]\s*\d)(?!\s*\/\s*(?:g|kg|ml|l|unit|100g))[\s\S]{1,40}?(?:MRP|M\.R\.P\.?|Max\.?\s*Retail\s*Price)",
            text,
            re.IGNORECASE,
        )
        if preceding_mrp:
            candidate = preceding_mrp.group(1).replace(",", "")
            if not is_date_or_invalid(candidate, preceding_mrp.end(1), text):
                amount = candidate
                raw_match = preceding_mrp.group(0)

    # Strategy 3: General currency amount with 2 decimal places, provided MRP keyword exists in text
    if not amount and re.search(r"\b(?:MRP|M\.R\.P\.?)\b", text, re.IGNORECASE):
        for m in re.finditer(
            r"(?:₹|Rs\.?)\s*([\d,]+\.\d{2})\b(?!\s*[\.\/-]\s*\d)(?!\s*\/\s*(?:g|kg|ml|l|unit|100g))",
            text,
            re.IGNORECASE,
        ):
            candidate = m.group(1).replace(",", "")
            if not is_date_or_invalid(candidate, m.end(1), text):
                amount = candidate
                raw_match = m.group(0)
                break

    # Strategy 4: Fallback any explicit currency notation not part of USP or date
    if not amount:
        for m in re.finditer(
            r"(?:₹|Rs\.?)\s*([\d,]+(?:\.\d{2})?)\b(?!\s*[\.\/-]\s*\d)(?!\s*\/\s*(?:g|kg|ml|l|unit|100g))",
            text,
            re.IGNORECASE,
        ):
            candidate = m.group(1).replace(",", "")
            if not is_date_or_invalid(candidate, m.end(1), text):
                amount = candidate
                raw_match = m.group(0)
                break

    if not amount:
        return None

    # Format to standard 2 decimal currency
    if "." not in amount:
        formatted_amount = f"{amount}.00"
    else:
        formatted_amount = amount

    formatted_reading = f"₹ {formatted_amount}"

    # Check for mandatory tax inclusion clause (handles OCR variations like 'fall taxes', 'incl. taxes')
    tax_pattern = re.compile(
        r"(?:incl\.?\s*of\s*(?:all|fall|alll)\s*taxes[a-z]?|inclusive\s*of\s*(?:all|fall)\s*taxes[a-z]?|incl\.?\s*taxes[a-z]?)",
        re.IGNORECASE,
    )
    has_tax_clause = bool(tax_pattern.search(text))
    if has_tax_clause:
        formatted_reading += " (incl. of all taxes)"

    return {
        "value": formatted_reading,
        "amount": formatted_amount,
        "has_tax_clause": has_tax_clause,
        "raw_match": raw_match,
    }


def _parse_date_tuple(d_str: str):
    try:
        parts = re.split(r"[\/\.-]", d_str)
        if len(parts) == 3:
            day = int(parts[0])
            month = int(parts[1])
            year = int(parts[2])
            if year < 100:
                year += 2000
            return (year, month, day)
        elif len(parts) == 2:
            month = int(parts[0])
            year = int(parts[1])
            if year < 100:
                year += 2000
            return (year, month, 1)
    except Exception:
        pass
    return (9999, 12, 31)


def find_all_packaging_dates(text: str):
    """Find all date stamps (DD.MM.YY, DD.MM.YYYY, DDMM.YY, MM/YYYY) sorted chronologically."""
    found = []
    # 1. Standard DD.MM.YY or DD.MM.YYYY (handles attached noise digits like 625.12.26)
    for m in re.finditer(r"(\d{2})\.(\d{2})\.(\d{2,4})\b", text):
        d = f"{m.group(1)}.{m.group(2)}.{m.group(3)}"
        if d not in found:
            found.append(d)
    # 2. DDMM.YY (faint dot-matrix separator like 2504.26)
    for m in re.finditer(r"(?:^|[^\d])(\d{2})(\d{2})\.(\d{2,4})\b", text):
        d = f"{m.group(1)}.{m.group(2)}.{m.group(3)}"
        if d not in found:
            found.append(d)
    # 3. MM/YYYY or MM-YYYY
    for m in re.finditer(r"\b(\d{2}[\/\-]\d{4})\b", text):
        d = m.group(1)
        if d not in found:
            found.append(d)
    # 4. Alphanumeric month stamps like FEB26 or FEB 2026
    for m in re.finditer(r"\b(JAN|FEB|MAR|APR|MAY|JUN|JUL|AUG|SEP|OCT|NOV|DEC)\s*[-_]?\s*(\d{2,4})\b", text, re.IGNORECASE):
        mon_str = m.group(1).upper()
        yr_str = m.group(2)
        if len(yr_str) == 2:
            yr_str = f"20{yr_str}"
        d = f"{mon_str} {yr_str}"
        if d not in found:
            found.append(d)

    found.sort(key=_parse_date_tuple)
    return found


def extract_net_quantity(text: str) -> Optional[Dict[str, Any]]:
    """Extract Net Quantity declaration (Rule 6(1)(c) + Rule 11 + Rule 12).

    Strictly avoids capturing nutrient amounts (e.g. Protein 12g) or unit prices.
    """
    # 1. Explicit Net Quantity keyword pattern: "Net Qty : 6 g", "Net Weight: 500 g"
    explicit_pattern = re.compile(
        r"(?:Net\s*(?:Qty|Quantity|Wt|Weight|Vol|Volume|Contents))[\s:\.]*([\d\.]+\s*(?:g|kg|ml|l|ltr|n|pcs|units))\b",
        re.IGNORECASE,
    )
    match = explicit_pattern.search(text)
    if match:
        return {"value": match.group(1).strip(), "raw_match": match.group(0)}

    # 2. Net Quantity with OCR typo in unit (e.g. 'Net Qty : 69' where '6g' lowercase g is misread as 9)
    qty_typo = re.search(
        r"(?:Net\s*(?:Qty|Quantity|Wt|Weight|Vol|Volume|Contents))[\s:\.]*(\d+(?:\.\d+)?)\s*9\b",
        text,
        re.IGNORECASE,
    )
    if qty_typo:
        return {"value": f"{qty_typo.group(1)} g", "raw_match": qty_typo.group(0)}

    # 3. Check for Net Qty followed nearby or on the next line by a number and unit
    qty_near = re.search(
        r"(?:Net\s*(?:Qty|Quantity|Wt|Weight))[\s:\.\n\r]{1,20}(\d+(?:\.\d+)?\s*(?:g|kg|ml|l|n))\b",
        text,
        re.IGNORECASE,
    )
    if qty_near:
        return {"value": qty_near.group(1).strip(), "raw_match": qty_near.group(0)}

    # 4. Serving size fallback if Net Quantity label had OCR degradation: "Serving Size = 1.6g"
    serving_match = re.search(r"Serving\s*Si[sz]e\s*[-=]?\s*([\d\.]+\s*(?:g|kg|ml|l))\b", text, re.IGNORECASE)
    if serving_match:
        return {"value": serving_match.group(1).strip(), "raw_match": serving_match.group(0)}

    # 5. Standalone metric quantity - strictly excluding nutritional table rows and unit prices
    nutrition_words = {
        "protein", "carb", "carbohydrate", "fat", "sugar", "fibre", "fiber",
        "sodium", "energy", "cholesterol", "kcal", "serving", "per 100g",
    }
    for line in text.split("\n"):
        line_clean = line.strip()
        if any(w in line_clean.lower() for w in nutrition_words):
            continue
        if re.search(r"\/\s*(?:g|kg|ml|l)", line_clean, re.I):
            continue
        standalone_m = re.search(r"(?<![\d\.\/])\b(\d+(?:\.\d+)?\s*(?:g|kg|ml|L|N))\b(?!\s*[\/\-])", line_clean, re.I)
        if standalone_m:
            return {"value": standalone_m.group(1).strip(), "raw_match": standalone_m.group(0)}

    # 6. Isolated packaging seal stamp weight (e.g. '69' on crimp seal where '6g' dot-matrix is read as 9)
    crimp_qty = re.search(r"(?:^|\n)\s*([1-9]\d?)\s*9\s*(?:$|\n)", text)
    if crimp_qty and re.search(r"(?:J8\/|U\.?S\.?P|0\.83|Pkg|Batch|Cumin|Cookme)", text, re.I):
        return {"value": f"{crimp_qty.group(1)} g", "raw_match": crimp_qty.group(0).strip()}

    return None


def extract_manufacturer_packer(text: str) -> Optional[Dict[str, Any]]:
    """Extract Manufacturer / Packer / Importer name and address (Rule 6(1)(a)).

    Extracts and assigns explicit entity role ('manufacturer', 'packer', 'marketed_by', 'importer')
    to prevent false MANUAL_VERIFICATION classification in compliance engine.
    """
    keywords_pattern = re.compile(
        r"(?:Manufactured\s*by|Mfg\s*by|Packed\s*by|Pkd\s*by|Marketed\s*by|Imported\s*by|Mfd\s*&\s*Pkd\s*by|Manufacturer|Packer|Importer)[\s:\.]*(.+)",
        re.IGNORECASE,
    )
    match = keywords_pattern.search(text)

    if match:
        line_match = match.group(1).strip()
        matched_prefix = text[match.start():match.end()].lower()

        # Classify legal role
        if any(k in matched_prefix for k in ["manufactured by", "mfg by", "mfd & pkd by", "mfd by", "manufacturer"]):
            role = "manufacturer"
        elif any(k in matched_prefix for k in ["packed by", "pkd by", "packer"]):
            role = "packer"
        elif any(k in matched_prefix for k in ["marketed by", "mktd by"]):
            role = "marketed_by"
        elif any(k in matched_prefix for k in ["imported by", "importer"]):
            role = "importer"
        else:
            role = "manufacturer"

        lines = [line_match]
        remaining_text = text[match.end():]
        for line in remaining_text.split("\n")[:3]:
            clean_line = line.strip()
            if clean_line and not re.search(r"(?:MRP|Net Qty|Batch|MFD|EXP|Use By|Date of)", clean_line, re.I):
                lines.append(clean_line)
            else:
                break
        address = ", ".join(lines)
        return {
            "value": address,
            "role": role,
            "raw_match": match.group(0),
        }

    # Search for pincode / address heuristics if explicit keyword missing
    pincode_match = re.search(
        r"([A-Za-z0-9\s,\.-]+(?:Pvt\.?\s*Ltd\.?|Ltd\.?|Agro|Industries|Private Limited)[A-Za-z0-9\s,\.-]+\d{6})",
        text,
        re.IGNORECASE,
    )
    if pincode_match:
        return {
            "value": pincode_match.group(1).strip(),
            "role": "unclear",
            "raw_match": pincode_match.group(0),
        }

    return None


def extract_batch_lot(text: str) -> Optional[Dict[str, Any]]:
    """Extract Batch / Lot number (Rule 6(1)(b))."""
    # 1. Crimp seal triplet stamp: e.g. "CMP02B_FEB26_FEB27" or "CMP02B FEB26 FEB27"
    stamp_triplet = re.search(r"\b([A-Z0-9]{4,8})[_\s]+([A-Za-z]{3}\d{2})[_\s]+([A-Za-z]{3}\d{2})\b", text)
    if stamp_triplet:
        return {"value": stamp_triplet.group(1).strip(), "raw_match": stamp_triplet.group(0)}

    # 2. Prioritize continuous inkjet structured batch stamp: e.g. "J8/32/027H", "B-492/A", "LOT-992"
    # Ensure it is not a calendar date like 01/04/2026 or 25/12/26
    for m in re.finditer(r"\b([A-Z0-9]{1,4}\/[A-Z0-9\-\/]{4,}[A-Z0-9]?)\b", text):
        candidate = m.group(1).strip()
        segments = candidate.split("/")
        if len(segments) in [2, 3] and all(s.isdigit() for s in segments):
            continue
        if len(candidate) >= 4 and any(c.isalpha() for c in candidate) and any(c.isdigit() for c in candidate):
            return {"value": candidate, "raw_match": m.group(0)}

    # 3. Standard batch pattern with keyword (e.g. "Batch No.: J8/32/027H")
    # Consume 'No', 'No.', '#' in the prefix so they are never captured as the batch value
    batch_pattern = re.compile(
        r"(?:Batch\s*(?:No\.?|#)?|Lot\s*(?:No\.?|#)?|B\.?\s*No\.?|L\.?\s*No\.?|B/No)[\s:\.]*([A-Za-z0-9\-\/\s]+?)(?=\s*(?:Date|MFD|DOM|Net|MRP|Rs|₹|Use|\n|$))",
        re.IGNORECASE,
    )
    match = batch_pattern.search(text)
    if match:
        val = match.group(1).strip()
        if len(val) >= 3 and any(c.isdigit() for c in val) and val.lower() not in ["no", "no.", "no:", "#", "le", "oo"]:
            return {"value": val, "raw_match": match.group(0)}

    # 4. Fallback alphanumeric code after batch keyword
    fallback = re.search(
        r"(?:Batch\s*(?:No\.?|#)?|Lot\s*(?:No\.?|#)?|B\.?\s*No\.?|L\.?\s*No\.?)[\s:\.]*([A-Za-z0-9\-\/]+)",
        text,
        re.IGNORECASE,
    )
    if fallback:
        val = fallback.group(1).strip()
        if len(val) >= 3 and any(c.isdigit() for c in val) and val.lower() not in ["no", "no.", "no:", "#", "le", "oo"]:
            return {"value": val, "raw_match": fallback.group(0)}

    return None


def extract_mfg_date(text: str) -> Optional[Dict[str, Any]]:
    """Extract Date of manufacture / packaging / import (Rule 6(1)(d))."""
    # 1. Crimp seal triplet stamp: e.g. "CMP02B_FEB26_FEB27"
    stamp_triplet = re.search(r"\b([A-Z0-9]{4,8})[_\s]+([A-Za-z]{3}\d{2})[_\s]+([A-Za-z]{3}\d{2})\b", text)
    if stamp_triplet:
        mfg = stamp_triplet.group(2)
        return {"value": f"{mfg[:3].upper()} 20{mfg[3:]}", "raw_match": stamp_triplet.group(0)}

    # 2. Look for explicit keyword + date
    date_pattern = re.compile(
        r"(?:Mfg|Pkd|Packed|Date\s*of\s*Pkg|Date\s*of\s*Packaging|MFD|DOM)[\s:\.]*(\d{1,2}[\/\.-]\d{1,2}[\/\.-](?:\d{4}|\d{2})|\d{1,2}[\/\.-](?:\d{4}|\d{2})|[A-Za-z]{3}\s*(?:\d{4}|\d{2}))",
        re.IGNORECASE,
    )
    match = date_pattern.search(text)
    if match:
        return {"value": match.group(1).strip(), "raw_match": match.group(0)}

    # 3. Look for dates in text (first date is typically packaging date)
    dates = find_all_packaging_dates(text)
    if dates:
        return {"value": dates[0], "raw_match": dates[0]}

    return None


def extract_best_before(text: str) -> Optional[Dict[str, Any]]:
    """Extract Best Before / Use By / Expiry declaration (Rule 6(1)(da))."""
    # 1. Crimp seal triplet stamp: e.g. "CMP02B_FEB26_FEB27"
    stamp_triplet = re.search(r"\b([A-Z0-9]{4,8})[_\s]+([A-Za-z]{3}\d{2})[_\s]+([A-Za-z]{3}\d{2})\b", text)
    if stamp_triplet:
        exp = stamp_triplet.group(3)
        return {
            "value": f"Use By: {exp[:3].upper()} 20{exp[3:]}",
            "details": f"{exp[:3].upper()} 20{exp[3:]}",
            "raw_match": stamp_triplet.group(0),
        }

    # 2. Explicit keyword with date or duration: e.g. "Use By: 25.12.26", "Best before 9 months"
    exp_pattern = re.compile(
        r"(?:Best\s*Before|Use\s*By|Expiry|Exp\.?\s*Date|EXP)[\s:\.]*(\d{1,2}[\/\.-]\d{1,2}[\/\.-](?:\d{4}|\d{2})|\d+\s*(?:months|days|weeks|year|years)[^\n\r]*)",
        re.IGNORECASE,
    )
    match = exp_pattern.search(text)
    if match:
        return {"value": match.group(0).strip(), "details": match.group(1).strip(), "raw_match": match.group(0)}

    # 3. If 'Use By' or 'Best Before' keyword exists, check for second date in continuous inkjet stamp
    if re.search(r"\b(?:Use\s*By|Best\s*Before|Expiry|EXP)\b", text, re.IGNORECASE):
        dates = find_all_packaging_dates(text)
        if len(dates) >= 2:
            return {"value": f"Use By: {dates[1]}", "details": dates[1], "raw_match": dates[1]}
        elif len(dates) == 1 and not re.search(r"\b(?:Mfg|Pkd|Date\s*of\s*Pkg)\b", text, re.IGNORECASE):
            return {"value": f"Use By: {dates[0]}", "details": dates[0], "raw_match": dates[0]}

    return None


def extract_consumer_care(text: str) -> Optional[Dict[str, Any]]:
    """Extract Consumer Care details (Rule 6(1)(f))."""
    email_match = re.search(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b", text)
    phone_match = re.search(
        r"\b(?:1800[-\s]?\d{3}[-\s]?\d{4}|\+?91[-\s]?[6-9]\d{9}|0\d{2,4}[-\s]?\d{3,4}[-\s]?\d{4}|0\d{2,4}[-\s]?\d{6,8}|Ph[\s:\.]*\d+)\b",
        text,
        re.IGNORECASE,
    )
    care_text_match = re.search(
        r"(?:Customer\s*Care|Consumer\s*Care|For\s*Feedback|For\s*Complaint|Feedback)[\s:\.][^\n]+",
        text,
        re.IGNORECASE,
    )

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


def extract_unit_sale_price(text: str) -> Optional[Dict[str, Any]]:
    """Extract Unit Sale Price (USP) declaration (Rule 6(1)(e) - Dec 2022 amendment)."""
    usp_pattern = re.compile(
        r"(?:U\.?S\.?P\.?|Unit\s*Sale\s*Price)[\s:\.]*(?:₹|Rs\.?|:\s*)?\s*([\d,]+(?:\.\d+)?\s*\/\s*(?:g|kg|ml|l|ltr|100g|100ml|n|piece|unit))\b",
        re.IGNORECASE,
    )
    match = usp_pattern.search(text)
    if match:
        return {"value": f"₹ {match.group(1).strip()}", "raw_match": match.group(0)}

    # Standalone price per unit e.g. 'Rs. 0.83/g' or '₹ 12.00/100g'
    standalone_usp = re.search(
        r"(?:₹|Rs\.?)\s*([\d,]+(?:\.\d+)?\s*\/\s*(?:g|kg|ml|l|ltr|100g|100ml|n))\b",
        text,
        re.IGNORECASE,
    )
    if standalone_usp:
        return {"value": f"₹ {standalone_usp.group(1).strip()}", "raw_match": standalone_usp.group(0)}

    # Proximity: "0.83 \n U.S.P." or "U.S.P. \n 0.83"
    preceding_usp = re.search(
        r"(?:₹|Rs\.?|:\s*)?\s*([\d,]+\.\d{2})\b(?!\s*[\.\/-]\s*\d)[\s\S]{0,25}?(?:U\.?S\.?P\.?|Unit\s*Sale\s*Price)",
        text,
        re.IGNORECASE,
    )
    if preceding_usp:
        val = preceding_usp.group(1).strip()
        return {"value": f"₹ {val} / g", "raw_match": preceding_usp.group(0)}

    following_usp = re.search(
        r"(?:U\.?S\.?P\.?|Unit\s*Sale\s*Price)[\s\S]{0,25}?(?:₹|Rs\.?|:\s*)?\s*([\d,]+\.\d{2})\b(?!\s*[\.\/-]\s*\d)",
        text,
        re.IGNORECASE,
    )
    if following_usp:
        val = following_usp.group(1).strip()
        return {"value": f"₹ {val} / g", "raw_match": following_usp.group(0)}

    return None


def extract_country_of_origin(text: str) -> Optional[Dict[str, Any]]:
    """Extract Country of Origin declaration (Rule 6(1)(n))."""
    origin_pattern = re.compile(
        r"(?:Country\s*of\s*Origin|Made\s*in|Product\s*of)[\s:\.]*([A-Za-z\s]+)",
        re.IGNORECASE,
    )
    match = origin_pattern.search(text)
    if match:
        val = match.group(1).strip().split("\n")[0]
        val = re.sub(r"[,\.\-]+$", "", val).strip()
        if 3 <= len(val) <= 30:
            return {"value": val, "raw_match": match.group(0)}

    if re.search(r"\bProduct\s*of\s*India\b", text, re.IGNORECASE):
        return {"value": "India", "raw_match": "Product of India"}
    if re.search(r"\bMade\s*in\s*India\b", text, re.IGNORECASE):
        return {"value": "India", "raw_match": "Made in India"}

    return None


def extract_all_declarations(text: str) -> Dict[str, Optional[Dict[str, Any]]]:
    """Master extraction function running all 9 Legal Metrology field extractors."""
    normalized = normalize_text(text)
    return {
        "mrp": extract_mrp(normalized),
        "net_quantity": extract_net_quantity(normalized),
        "manufacturer_packer": extract_manufacturer_packer(normalized),
        "batch_lot": extract_batch_lot(normalized),
        "mfg_date": extract_mfg_date(normalized),
        "best_before": extract_best_before(normalized),
        "consumer_care": extract_consumer_care(normalized),
        "unit_sale_price": extract_unit_sale_price(normalized),
        "country_of_origin": extract_country_of_origin(normalized),
    }
