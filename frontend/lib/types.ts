export type CheckStatus = "detected" | "potential_issue" | "manual_verification";

export interface ComplianceCheck {
  id: string;
  label: string;
  status: CheckStatus;
  /** The value read off the label, if any (e.g. "250 g", "MRP ₹145.00") */
  reading: string | null;
  /** Rule reference, e.g. "LM(PC) Rules 2011, r.6(1)(f)" */
  ruleRef: string;
  /** Why this was flagged — only shown when status !== "detected" */
  reason: string | null;
}

export interface ProductInfo {
  name: string;
  brand: string;
  netQuantity: string;
  mrp: string;
  batchNumber: string;
  mfgDate: string;
  packerAddress: string;
  customerCareText: string | null;
  bestBefore?: string | null;
}


export interface ScanResult {
  scanId: string;
  imageUrl: string;
  scannedAt: string;
  product: ProductInfo;
  checks: ComplianceCheck[];
}

export type AppScreen = "upload" | "scanning" | "results";
