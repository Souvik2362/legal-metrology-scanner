import { ScanResult } from "./types";

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api/v1";

/**
 * Scan product label image via backend FastAPI service.
 * Falls back gracefully to updated mock data if backend server is unreachable.
 */
export async function getMockScanResult(imageUrl: string): Promise<ScanResult> {
  try {
    // 1. Fetch image blob if imageUrl is a blob: or data: URL
    const imageRes = await fetch(imageUrl);
    const blob = await imageRes.blob();

    // 2. Prepare multipart form payload
    const formData = new FormData();
    formData.append("image", blob, "scanned_label.jpg");

    // 3. Post to backend scan endpoint
    const response = await fetch(`${API_BASE_URL}/scan`, {
      method: "POST",
      body: formData,
    });

    if (response.ok) {
      const data: ScanResult = await response.json();
      // Ensure image URL points to the local object URL for preview rendering
      data.imageUrl = imageUrl;
      return data;
    }
  } catch (error) {
    console.warn("Backend connection failed or offline. Falling back to rule-aligned mock result.", error);
  }

  // Simulated latency fallback
  await new Promise((resolve) => setTimeout(resolve, 2000));

  return {
    scanId: "SCN-" + Math.floor(100000 + Math.random() * 900000),
    imageUrl,
    scannedAt: new Date().toISOString(),
    product: {
      name: "Refined Sunflower Oil",
      brand: "Sunridge",
      netQuantity: "1 L",
      mrp: "₹189.00",
      batchNumber: "SR24B0417",
      mfgDate: "03/2026",
      packerAddress: "Sunridge Agro Pvt. Ltd., MIDC Industrial Area, Nashik, Maharashtra 422010",
      customerCareText: "care@sunridge.com",
      bestBefore: "Best before 9 months from mfg",
    },
    checks: [
      {
        id: "mrp",
        label: "MRP / Retail Sale Price declaration",
        status: "detected",
        reading: "₹189.00 (incl. of all taxes)",
        ruleRef: "Rule 6(1)(e) — Legal Metrology (Packaged Commodities) Rules, 2011",
        reason: null,
      },
      {
        id: "net_quantity",
        label: "Net Quantity declaration",
        status: "detected",
        reading: "1 L",
        ruleRef: "Rule 6(1)(c) + Rule 11 + Rule 12 — Legal Metrology (Packaged Commodities) Rules, 2011",
        reason: null,
      },
      {
        id: "manufacturer_packer",
        label: "Manufacturer / Packer / Importer details",
        status: "manual_verification",
        reading: "Sunridge Agro Pvt. Ltd., Nashik 422010",
        ruleRef: "Rule 6(1)(a) — Legal Metrology (Packaged Commodities) Rules, 2011",
        reason:
          "A name and address were detected, but OCR could not verify whether this entity is manufacturer, packer, or importer. Check label wording directly.",
      },
      {
        id: "batch_lot",
        label: "Batch / Lot number",
        status: "detected",
        reading: "SR24B0417",
        ruleRef: "Rule 6(1)(b) — Legal Metrology (Packaged Commodities) Rules, 2011",
        reason: null,
      },
      {
        id: "mfg_date",
        label: "Date of manufacture / packaging",
        status: "detected",
        reading: "03/2026",
        ruleRef: "Rule 6(1)(d) — Legal Metrology (Packaged Commodities) Rules, 2011",
        reason: null,
      },
      {
        id: "best_before",
        label: "Best Before / Expiry date",
        status: "detected",
        reading: "Best before 9 months from mfg",
        ruleRef: "Rule 6(1)(da) — Legal Metrology (Packaged Commodities) Rules, 2011",
        reason: null,
      },
      {
        id: "consumer_care",
        label: "Consumer Care details",
        status: "potential_issue",
        reading: null,
        ruleRef: "Rule 6(1)(f) — Legal Metrology (Packaged Commodities) Rules, 2011",
        reason:
          "No phone number, email, or contact address for consumer complaints was located on the scanned face. Check the reverse panel before treating as missing.",
      },
    ],
  };
}
