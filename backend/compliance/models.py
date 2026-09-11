"""Pydantic data models for the Legal Metrology Scanner API.

Aligned with frontend TypeScript definitions in lib/types.ts.
"""

from enum import Enum
from typing import List, Optional
from pydantic import BaseModel, Field


class CheckStatus(str, Enum):
    """Preliminary compliance status values.

    IMPORTANT: Never use 'legally compliant' or 'legal violation'.
    - DETECTED: Relevant declaration was found on label.
    - POTENTIAL_ISSUE: Declaration appears missing or ambiguous.
    - MANUAL_VERIFICATION: OCR confidence low or entity requires human verification.
    """
    DETECTED = "detected"
    POTENTIAL_ISSUE = "potential_issue"
    MANUAL_VERIFICATION = "manual_verification"


class ComplianceCheck(BaseModel):
    """Single compliance check result for one of the 7 MVP declarations."""
    id: str
    label: str
    status: CheckStatus
    reading: Optional[str] = Field(
        default=None,
        description="The value extracted from label text, if any."
    )
    ruleRef: str = Field(
        description="Rule reference string, e.g. Rule 6(1)(e)"
    )
    reason: Optional[str] = Field(
        default=None,
        description="Non-judgmental explanation of status or review advice."
    )


class ProductInfo(BaseModel):
    """Extracted product label metadata."""
    name: str = Field(default="Packaged Product")
    brand: str = Field(default="Unspecified Brand")
    netQuantity: str = Field(default="Not detected")
    mrp: str = Field(default="Not detected")
    batchNumber: str = Field(default="Not detected")
    mfgDate: str = Field(default="Not detected")
    packerAddress: str = Field(default="Not detected")
    customerCareText: Optional[str] = None
    bestBefore: Optional[str] = None


class ScanResult(BaseModel):
    """Complete API response contract matching frontend expectations."""
    scanId: str
    imageUrl: str
    scannedAt: str
    product: ProductInfo
    checks: List[ComplianceCheck]
