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
        id: "manufacturer-packer",
        label: "Manufacturer / packer / importer",
        status: "manual_verification",
        reading: "Sunridge Agro Pvt. Ltd. (role unclear)",
        ruleRef: "LM(PC) Rules 2011, r.6(1)(a)",
        reason:
          "A name and address were detected, but OCR couldn't confidently determine whether this is the manufacturer, packer, or importer — this affects which declaration is actually required. Check the label wording directly.",
      },
      {
        id: "batch-lot",
        label: "Batch / lot number",
        status: "detected",
        reading: "SR24B0417",
        ruleRef: "LM(PC) Rules 2011, r.6(1)(j)",
        reason: null,
      },
      {
        id: "mfg-date",
        label: "Date-related declaration",
        status: "detected",
        reading: "MFD 03/2026",
        ruleRef: "LM(PC) Rules 2011, r.6(1)(h)",
        reason: null,
      },
      {
        id: "consumer-care",
        label: "Consumer care details",
        status: "potential_issue",
        reading: null,
        ruleRef: "LM(PC) Rules 2011, r.6(1)(k)",
        reason:
          "No phone number, email, or contact address for consumer complaints was located on the scanned face. Check the reverse panel before treating this as missing.",
      },
    ],
  };
}
