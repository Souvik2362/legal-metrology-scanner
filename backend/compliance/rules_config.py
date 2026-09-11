"""Centralized Legal Metrology Rule Registry.

All legal references in this file are established based on:
1. Legal Metrology Act, 2009 — Section 18
2. Legal Metrology (Packaged Commodities) Rules, 2011 — Rule 6(1)

DO NOT alter these references without consulting the legal metrology research documentation.
"""

from typing import Dict, Any

PARENT_LAW = "Legal Metrology Act, 2009 — Section 18"

RULE_CONFIGS: Dict[str, Dict[str, Any]] = {
    "mrp": {
        "id": "mrp",
        "label": "MRP / Retail Sale Price declaration",
        "rule_ref": "Rule 6(1)(e) — Legal Metrology (Packaged Commodities) Rules, 2011",
        "parent_law": PARENT_LAW,
        "description": (
            "Maximum Retail Price (MRP) inclusive of all taxes must be clearly declared "
            "on every pre-packaged commodity in Indian currency (₹ / Rs.)."
        ),
        "required": True,
    },
    "net_quantity": {
        "id": "net_quantity",
        "label": "Net Quantity declaration",
        "rule_ref": "Rule 6(1)(c) + Rule 11 + Rule 12 — Legal Metrology (Packaged Commodities) Rules, 2011",
        "parent_law": PARENT_LAW,
        "description": (
            "Net quantity in terms of standard unit of weight, measure, or number "
            "must be clearly declared on the package."
        ),
        "required": True,
    },
    "manufacturer_packer": {
        "id": "manufacturer_packer",
        "label": "Manufacturer / Packer / Importer details",
        "rule_ref": "Rule 6(1)(a) — Legal Metrology (Packaged Commodities) Rules, 2011",
        "parent_law": PARENT_LAW,
        "description": (
            "Name and complete address of the manufacturer, packer, or importer "
            "must be declared on the package."
        ),
        "required": True,
    },
    "batch_lot": {
        "id": "batch_lot",
        "label": "Batch / Lot number",
        "rule_ref": "Rule 6(1)(b) — Legal Metrology (Packaged Commodities) Rules, 2011",
        "parent_law": PARENT_LAW,
        "description": (
            "Batch number, lot number, or code number distinguishing the manufacturing lot "
            "must be declared on the package."
        ),
        "required": True,
    },
    "mfg_date": {
        "id": "mfg_date",
        "label": "Date of manufacture / packaging / import",
        "rule_ref": "Rule 6(1)(d) — Legal Metrology (Packaged Commodities) Rules, 2011",
        "parent_law": PARENT_LAW,
        "description": (
            "Month and year in which the commodity is manufactured, packed, or imported "
            "must be declared."
        ),
        "required": True,
    },
    "best_before": {
        "id": "best_before",
        "label": "Best Before / Use By / Expiry date",
        "rule_ref": "Rule 6(1)(da) — Legal Metrology (Packaged Commodities) Rules, 2011",
        "parent_law": PARENT_LAW,
        "description": (
            "Expiry date or 'Best Before' period declaration where applicable "
            "(e.g. food items, cosmetics, perishable goods)."
        ),
        "required": False,  # Conditional upon commodity type
    },
    "consumer_care": {
        "id": "consumer_care",
        "label": "Consumer Care details",
        "rule_ref": "Rule 6(1)(f) — Legal Metrology (Packaged Commodities) Rules, 2011",
        "parent_law": PARENT_LAW,
        "description": (
            "Name, address, telephone number, and email address of the person/office "
            "to be contacted in case of consumer complaints."
        ),
        "required": True,
    },
    "unit_sale_price": {
        "id": "unit_sale_price",
        "label": "Unit Sale Price (USP)",
        "rule_ref": "Rule 6(1)(e) — Legal Metrology (Packaged Commodities) Rules, 2011 (as amended Dec 2022)",
        "parent_law": PARENT_LAW,
        "description": (
            "Unit sale price in terms of price per g/ml or per 100g/100ml must be declared "
            "on packages containing net quantity of more than 1g or 1ml."
        ),
        "required": True,
    },
    "country_of_origin": {
        "id": "country_of_origin",
        "label": "Country of Origin declaration",
        "rule_ref": "Rule 6(1)(n) — Legal Metrology (Packaged Commodities) Rules, 2011",
        "parent_law": PARENT_LAW,
        "description": (
            "The name of the country of origin or manufacture must be clearly mentioned on every package."
        ),
        "required": True,
    },
}


def get_rule_config(check_id: str) -> Dict[str, Any]:
    """Retrieve rule configuration metadata by check ID."""
    return RULE_CONFIGS.get(
        check_id,
        {
            "id": check_id,
            "label": f"Check {check_id}",
            "rule_ref": "Legal Metrology (Packaged Commodities) Rules, 2011",
            "parent_law": PARENT_LAW,
            "description": "General Legal Metrology packaged commodity declaration.",
            "required": True,
        },
    )
