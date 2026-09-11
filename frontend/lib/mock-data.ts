import { ScanResult } from "./types";

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api/v1";

/**
 * Scan product label image via backend FastAPI service.
 * Throws explicit error on network failure or HTTP errors so UI can render clean feedback.
 */
export async function scanProductLabel(
  imageUrl: string,
  useMockFallback: boolean = false
): Promise<ScanResult> {
  if (useMockFallback) {
    await new Promise((resolve) => setTimeout(resolve, 800));
    return getMockScanResult(imageUrl, "cookme");
  }

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

    if (!response.ok) {
      let errorMsg = `Scan request failed (HTTP ${response.status})`;
      try {
        const errorJson = await response.json();
        if (errorJson.detail) {
          errorMsg = errorJson.detail;
        }
      } catch {
        // Fallback to generic message
      }
      throw new Error(errorMsg);
    }

    const data: ScanResult = await response.json();
    data.imageUrl = imageUrl;
    return data;
  } catch (error: any) {
    // Check if network error (e.g. backend offline)
    if (error.message && (error.message.includes("Failed to fetch") || error.message.includes("NetworkError"))) {
      throw new Error(
        "Backend server is unreachable at http://localhost:8000. Please ensure the FastAPI backend is running (uvicorn main:app --reload), or switch to Demo Mode."
      );
    }
    throw error;
  }
}

/**
 * High-fidelity statutory mock data for presentation & offline demo mode.
 */
export function getMockScanResult(imageUrl: string, sample: "cookme" | "sunridge" = "cookme"): ScanResult {
  if (sample === "cookme") {
    return {
      scanId: "SCN-" + Math.floor(100000 + Math.random() * 900000),
      imageUrl,
      scannedAt: new Date().toISOString(),
      product: {
        name: "Whole Cumin",
        brand: "Cookme",
        netQuantity: "6 g",
        mrp: "₹ 5.00 (incl. of all taxes)",
        batchNumber: "J8/32/027H",
        mfgDate: "25.04.26",
        packerAddress: "Krishna Chandra Dutta (Spice) Private Limited, Vill & P.O.- Belumilki, Mouza- Piarapur, Srirampore, Pin: 712223",
        customerCareText: "e-mail: consumercare@cookme.in, Ph: 033 2259 9247",
        bestBefore: "Use By: 25.12.26",
        unitSalePrice: "₹ 0.83 / g",
        countryOfOrigin: "India",
      },
      checks: [
        {
          id: "mrp",
          label: "MRP / Retail Sale Price declaration",
          status: "detected",
          reading: "₹ 5.00 (incl. of all taxes)",
          ruleRef: "Rule 6(1)(e) — Legal Metrology (Packaged Commodities) Rules, 2011",
          reason: null,
        },
        {
          id: "net_quantity",
          label: "Net Quantity declaration",
          status: "detected",
          reading: "6 g",
          ruleRef: "Rule 6(1)(c) + Rule 11 + Rule 12 — Legal Metrology (Packaged Commodities) Rules, 2011",
          reason: null,
        },
        {
          id: "manufacturer_packer",
          label: "Manufacturer / Packer / Importer details",
          status: "detected",
          reading: "Krishna Chandra Dutta (Spice) Private Limited (Manufacturer)",
          ruleRef: "Rule 6(1)(a) — Legal Metrology (Packaged Commodities) Rules, 2011",
          reason: null,
        },
        {
          id: "batch_lot",
          label: "Batch / Lot number",
          status: "detected",
          reading: "J8/32/027H",
          ruleRef: "Rule 6(1)(b) — Legal Metrology (Packaged Commodities) Rules, 2011",
          reason: null,
        },
        {
          id: "mfg_date",
          label: "Date of manufacture / packaging / import",
          status: "detected",
          reading: "25.04.26",
          ruleRef: "Rule 6(1)(d) — Legal Metrology (Packaged Commodities) Rules, 2011",
          reason: null,
        },
        {
          id: "best_before",
          label: "Best Before / Use By / Expiry date",
          status: "detected",
          reading: "Use By: 25.12.26",
          ruleRef: "Rule 6(1)(da) — Legal Metrology (Packaged Commodities) Rules, 2011",
          reason: null,
        },
        {
          id: "consumer_care",
          label: "Consumer Care details",
          status: "detected",
          reading: "Email: consumercare@cookme.in, Ph: 033 2259 9247",
          ruleRef: "Rule 6(1)(f) — Legal Metrology (Packaged Commodities) Rules, 2011",
          reason: null,
        },
        {
          id: "unit_sale_price",
          label: "Unit Sale Price (USP)",
          status: "detected",
          reading: "₹ 0.83 / g",
          ruleRef: "Rule 6(1)(e) — Legal Metrology (Packaged Commodities) Rules, 2011 (as amended Dec 2022)",
          reason: null,
        },
        {
          id: "country_of_origin",
          label: "Country of Origin declaration",
          status: "detected",
          reading: "Product of India",
          ruleRef: "Rule 6(1)(n) — Legal Metrology (Packaged Commodities) Rules, 2011",
          reason: null,
        },
      ],
    };
  }

  return {
    scanId: "SCN-" + Math.floor(100000 + Math.random() * 900000),
    imageUrl,
    scannedAt: new Date().toISOString(),
    product: {
      name: "Refined Sunflower Oil",
      brand: "Sunridge",
      netQuantity: "1 L",
      mrp: "₹189.00 (incl. of all taxes)",
      batchNumber: "SR24B0417",
      mfgDate: "03/2026",
      packerAddress: "Sunridge Agro Pvt. Ltd., MIDC Industrial Area, Nashik, Maharashtra 422010",
      customerCareText: "care@sunridge.com",
      bestBefore: "Best before 9 months from mfg",
      unitSalePrice: "₹ 18.90 / 100ml",
      countryOfOrigin: "India",
    },
    checks: [
      {
        id: "mrp",
        label: "MRP / Retail Sale Price declaration",
        status: "detected",
        reading: "₹ 189.00 (incl. of all taxes)",
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
        status: "detected",
        reading: "Sunridge Agro Pvt. Ltd., Nashik 422010 (Manufacturer)",
        ruleRef: "Rule 6(1)(a) — Legal Metrology (Packaged Commodities) Rules, 2011",
        reason: null,
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
        label: "Date of manufacture / packaging / import",
        status: "detected",
        reading: "03/2026",
        ruleRef: "Rule 6(1)(d) — Legal Metrology (Packaged Commodities) Rules, 2011",
        reason: null,
      },
      {
        id: "best_before",
        label: "Best Before / Use By / Expiry date",
        status: "detected",
        reading: "Best before 9 months from mfg",
        ruleRef: "Rule 6(1)(da) — Legal Metrology (Packaged Commodities) Rules, 2011",
        reason: null,
      },
      {
        id: "consumer_care",
        label: "Consumer Care details",
        status: "detected",
        reading: "Email: care@sunridge.com",
        ruleRef: "Rule 6(1)(f) — Legal Metrology (Packaged Commodities) Rules, 2011",
        reason: null,
      },
      {
        id: "unit_sale_price",
        label: "Unit Sale Price (USP)",
        status: "detected",
        reading: "₹ 18.90 / 100ml",
        ruleRef: "Rule 6(1)(e) — Legal Metrology (Packaged Commodities) Rules, 2011 (as amended Dec 2022)",
        reason: null,
      },
      {
        id: "country_of_origin",
        label: "Country of Origin declaration",
        status: "detected",
        reading: "Product of India",
        ruleRef: "Rule 6(1)(n) — Legal Metrology (Packaged Commodities) Rules, 2011",
        reason: null,
      },
    ],
  };
}
