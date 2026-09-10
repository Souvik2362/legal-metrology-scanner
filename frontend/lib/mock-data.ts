import { ScanResult } from "./types";

/**
 * Mock stand-in for a POST to the real label-analysis backend.
 *
 * TO CONNECT THE REAL BACKEND:
 * Replace the body of this function with a fetch to the FastAPI endpoint,
 * e.g.
 *
 *   export async function getMockScanResult(imageFile: File): Promise<ScanResult> {
 *     const form = new FormData();
 *     form.append("image", imageFile);
 *     const res = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/scan`, {
 *       method: "POST",
 *       body: form,
 *     });
 *     if (!res.ok) throw new Error("Scan failed");
 *     return res.json();
 *   }
 *
 * As long as the FastAPI response is shaped like ScanResult (lib/types.ts),
 * no other component needs to change.
 */
export async function getMockScanResult(imageUrl: string): Promise<ScanResult> {
  // Simulate network + inference latency.
  await new Promise((resolve) => setTimeout(resolve, 2600));

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
      customerCareText: null,
    },
    checks: [
      {
        id: "mrp",
        label: "MRP declaration",
        status: "detected",
        reading: "₹189.00 (incl. of all taxes)",
        ruleRef: "LM(PC) Rules 2011, r.6(1)(e)",
        reason: null,
      },
      {
        id: "net-qty",
        label: "Net quantity",
        status: "detected",
        reading: "1 L",
        ruleRef: "LM(PC) Rules 2011, r.6(1)(f)",
        reason: null,
      },
      {
        id: "unit-price",
        label: "Unit sale price",
        status: "needs_verification",
        reading: "₹189.00 / L",
        ruleRef: "LM(PC) Rules 2011, r.6(1)(g)",
        reason:
          "Printed unit price does not divide evenly against MRP and net quantity — off by ₹0.40. May be a rounding artifact or a genuine mismatch; worth a manual check against the invoice.",
      },
      {
        id: "mfg-date",
        label: "Month & year of manufacture",
        status: "detected",
        reading: "03/2026",
        ruleRef: "LM(PC) Rules 2011, r.6(1)(h)",
        reason: null,
      },
      {
        id: "consumer-care",
        label: "Consumer care details",
        status: "not_found",
        reading: null,
        ruleRef: "LM(PC) Rules 2011, r.6(1)(k)",
        reason:
          "No phone number, email, or contact address for consumer complaints was located on the scanned face. Check the reverse panel before marking this as missing.",
      },
      {
        id: "country-origin",
        label: "Country of origin",
        status: "not_found",
        reading: null,
        ruleRef: "LM(PC) Rules 2011, r.6(1)(m)",
        reason:
          "Declaration of origin was not detected in the scanned region. Common on domestically packed goods, but confirm this isn't an imported blend.",
      },
    ],
  };
}
