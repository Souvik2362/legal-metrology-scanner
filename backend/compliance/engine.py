"""Modular Compliance Engine for Legal Metrology Preliminary Assessment.

Evaluates extracted product fields against official Legal Metrology (Packaged Commodities) Rules, 2011.
Computes non-judgmental status classifications: DETECTED, POTENTIAL_ISSUE, MANUAL_VERIFICATION.
"""

import datetime
import random
from typing import Dict, Any, List, Optional
from backend.compliance.models import (
    ScanResult,
    ProductInfo,
    ComplianceCheck,
    CheckStatus,
)
from backend.compliance.rules_config import RULE_CONFIGS


def evaluate_declaration(
    check_id: str,
    extracted_item: Optional[Dict[str, Any]],
    avg_ocr_confidence: float = 0.9,
) -> ComplianceCheck:
    """Evaluate a single declaration against its Legal Metrology rule specification."""
    rule = RULE_CONFIGS[check_id]
    rule_ref = rule["rule_ref"]
    label = rule["label"]
    is_required = rule.get("required", True)

    # 1. Declaration not detected
    if not extracted_item or not extracted_item.get("value"):
        if is_required:
            return ComplianceCheck(
                id=check_id,
                label=label,
                status=CheckStatus.POTENTIAL_ISSUE,
                reading=None,
                ruleRef=rule_ref,
                reason=(
                    f"The {label.lower()} was not detected on the scanned package face. "
                    "Verify other packaging panels before concluding non-compliance."
                ),
            )
        else:
            return ComplianceCheck(
                id=check_id,
                label=label,
                status=CheckStatus.DETECTED,
                reading="Not required / Optional",
                ruleRef=rule_ref,
                reason="Optional date declaration not located on scanned face.",
            )

    value = str(extracted_item["value"]).strip()

    # 2. Low OCR Confidence triggers Manual Verification
    if avg_ocr_confidence < 0.60:
        return ComplianceCheck(
            id=check_id,
            label=label,
            status=CheckStatus.MANUAL_VERIFICATION,
            reading=value,
            ruleRef=rule_ref,
            reason=(
                "Declaration detected, but OCR confidence is below threshold. "
                "Manual review recommended to verify legibility and completeness."
            ),
        )

    # 3. Rule-specific validation checks
    # MRP Tax Clause check
    if check_id == "mrp":
        has_tax = extracted_item.get("has_tax_clause", False)
        if not has_tax:
            return ComplianceCheck(
                id=check_id,
                label=label,
                status=CheckStatus.POTENTIAL_ISSUE,
                reading=value,
                ruleRef=rule_ref,
                reason=(
                    "MRP amount was detected, but the mandatory 'inclusive of all taxes' "
                    "statement was not clearly identified near the price."
                ),
            )

    # Manufacturer / Packer Role Ambiguity check
    if check_id == "manufacturer_packer":
        role = extracted_item.get("role")
        if not role or role == "unclear":
            return ComplianceCheck(
                id=check_id,
                label=label,
                status=CheckStatus.MANUAL_VERIFICATION,
                reading=value,
                ruleRef=rule_ref,
                reason=(
                    "Name and address detected, but OCR could not verify whether "
                    "the entity is manufacturer, packer, or importer. Check label wording."
                ),
            )

    # Default success: DETECTED
    return ComplianceCheck(
        id=check_id,
        label=label,
        status=CheckStatus.DETECTED,
        reading=value,
        ruleRef=rule_ref,
        reason=None,
    )


def run_compliance_assessment(
    extracted_declarations: Dict[str, Any],
    avg_ocr_confidence: float = 0.9,
    image_url: str = "",
    raw_ocr_text: str = "",
) -> ScanResult:
    """Run full compliance assessment across all 9 Legal Metrology declarations and build ScanResult."""

    scan_id = f"SCN-{random.randint(100000, 999999)}"
    scanned_at = datetime.datetime.now(datetime.timezone.utc).isoformat()

    checks: List[ComplianceCheck] = []

    # Order of checks aligned with Legal Metrology statutory priorities
    check_order = [
        "mrp",
        "net_quantity",
        "manufacturer_packer",
        "batch_lot",
        "mfg_date",
        "best_before",
        "consumer_care",
        "unit_sale_price",
        "country_of_origin",
    ]

    for check_id in check_order:
        item = extracted_declarations.get(check_id)
        check_res = evaluate_declaration(check_id, item, avg_ocr_confidence)
        checks.append(check_res)

    # Extract or infer product metadata
    mrp_val = extracted_declarations.get("mrp", {}).get("value") if extracted_declarations.get("mrp") else "Not detected"
    net_qty_val = extracted_declarations.get("net_quantity", {}).get("value") if extracted_declarations.get("net_quantity") else "Not detected"
    batch_val = extracted_declarations.get("batch_lot", {}).get("value") if extracted_declarations.get("batch_lot") else "Not detected"
    mfg_val = extracted_declarations.get("mfg_date", {}).get("value") if extracted_declarations.get("mfg_date") else "Not detected"
    packer_val = extracted_declarations.get("manufacturer_packer", {}).get("value") if extracted_declarations.get("manufacturer_packer") else "Not detected"
    care_val = extracted_declarations.get("consumer_care", {}).get("value") if extracted_declarations.get("consumer_care") else None
    exp_val = extracted_declarations.get("best_before", {}).get("value") if extracted_declarations.get("best_before") else None
    usp_val = extracted_declarations.get("unit_sale_price", {}).get("value") if extracted_declarations.get("unit_sale_price") else None
    origin_val = extracted_declarations.get("country_of_origin", {}).get("value") if extracted_declarations.get("country_of_origin") else None

    # Intelligent product name and brand inference from raw OCR text
    import re
    brand_name = "Packaged Product"
    product_name = "Packaged Commodity"

    brand_match = re.search(r'"([^"]+)"\s*(?:House|Agro|Foods|Spices|Enterprises)', raw_ocr_text, re.I)
    if not brand_match:
        brand_match = re.search(r'\b(Cookme|Everest|MDH|Catch|Tata|Sunridge|Fortune|Amul|Aashirvaad|Britannia|Parle|Haldiram|Nestle)\b', raw_ocr_text, re.I)
    if brand_match:
        brand_name = brand_match.group(1).strip()
    elif extracted_declarations.get("manufacturer_packer") and extracted_declarations["manufacturer_packer"].get("value"):
        val = extracted_declarations["manufacturer_packer"]["value"]
        first_word = val.split()[0] if val else ""
        if len(first_word) > 2:
            brand_name = first_word

    # Search for commodity / ingredient name (ignore 'Product of India')
    ing_match = re.search(r'(?:Ingredient(?:s)?|Commodity)[\s:\.]*([A-Za-z\s]+)', raw_ocr_text, re.I)
    if ing_match:
        product_name = ing_match.group(1).strip().split("\n")[0]
    else:
        candidates = [
            l.strip() for l in raw_ocr_text.split("\n")
            if l.strip() and not re.search(r'(?:Batch|MRP|Net|MFD|Pkg|Lic|Regd|Clean|Keep|Date|Product\s*of|Made\s*in|For\s*Feedback)', l, re.I)
        ]
        if candidates:
            product_name = candidates[0][:40]

    product = ProductInfo(
        name=product_name,
        brand=brand_name,
        netQuantity=net_qty_val,
        mrp=mrp_val,
        batchNumber=batch_val,
        mfgDate=mfg_val,
        packerAddress=packer_val,
        customerCareText=care_val,
        bestBefore=exp_val,
        unitSalePrice=usp_val,
        countryOfOrigin=origin_val,
    )

    return ScanResult(
        scanId=scan_id,
        imageUrl=image_url,
        scannedAt=scanned_at,
        product=product,
        checks=checks,
    )
