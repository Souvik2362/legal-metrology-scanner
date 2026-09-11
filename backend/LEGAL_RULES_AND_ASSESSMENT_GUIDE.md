# Legal Metrology Rules & Assessment Calculation Guide

> **Project**: SIH26034 — Product-Label Compliance Scanner  
> **Target Audience**: Academic Evaluators, Professors, Hackathon Judges  
> **Scope**: Preliminary Compliance Assessment under Indian Legal Metrology Laws  

---

## 1. Statutory Framework

### Parent Statute
- **Legal Metrology Act, 2009 — Section 18**
  - Mandates that no person shall manufacture, pack, sell, import, distribute, deliver, or offer for sale any pre-packaged commodity unless the package bears thereon all prescribed declarations.

### Operating Rules
- **Legal Metrology (Packaged Commodities) Rules, 2011 — Rule 6(1)**
  - Outlines mandatory declarations required on every principal display panel (PDP) or package container.

---

## 2. Summary Table of the 9 Mandatory Declarations

| # | Declaration Category | Statutory Reference under LM(PC) Rules, 2011 | What the Rule Mandates | Extractor Logic / Pattern Used |
|---|---|---|---|---|
| **1** | **MRP / Retail Sale Price** | **Rule 6(1)(e)** | Maximum Retail Price inclusive of all taxes declared in Indian Rupees (`₹` / `Rs.`). | Proximity parser: `(MRP\|M.R.P.)` + currency amounts with boundary checks rejecting date stamps (`625.12.26`). |
| **2** | **Net Quantity** | **Rule 6(1)(c) + Rule 11 + Rule 12** | Standard unit of weight, volume, or count (`g`, `kg`, `ml`, `L`, `N`). Standard unit symbols strictly mandated. | Regex: `(Net Qty\|Net Wt\|Net Vol)[\s:]*([\d\.]+\s*(g\|kg\|ml\|l\|n))` with unit normalization, isolating nutrition rows. |
| **3** | **Manufacturer / Packer / Importer** | **Rule 6(1)(a)** | Complete name and postal address of manufacturer, packer, or importer. | Keyword matcher (`Mfg by`, `Packed by`, `Marketed by`) + legal entity role classifier. |
| **4** | **Batch / Lot Number** | **Rule 6(1)(b)** | Batch number, lot number, or code distinguishing the manufacturing lot. | Prefix-safe regex: `(Batch No\|Lot No\|B. No)[\s:]*([A-Za-z0-9\-\/]+)`. |
| **5** | **Date Declaration** | **Rule 6(1)(d)** | Month and Year of manufacture, packaging, or import (`MM/YYYY` or `Month YYYY`). | Regex: `(Mfg\|Pkd\|MFD\|DOM)[\s:]*(\d{2}[\/\.-]\d{4}\|\d{2}[\/\.-]\d{2}[\/\.-]\d{4})`. |
| **6** | **Best Before / Use By** | **Rule 6(1)(da)** | Expiry date or 'Best Before' period declaration (where applicable for perishable/food items). | Regex: `(Best Before\|Use By\|Expiry\|Exp Date)[\s:]*([^\n\.,]+)`. |
| **7** | **Consumer Care Details** | **Rule 6(1)(f)** | Name, address, telephone number, and email address for consumer complaints. | Pattern matcher for toll-free numbers (`1800...`), mobile numbers, and email patterns (`@`). |
| **8** | **Unit Sale Price (USP)** | **Rule 6(1)(e) (amended Dec 2022)** | Mandatory declaration of price per unit (`₹ / g`, `₹ / ml`, `₹ / 100g`, `₹ / 100ml`). | Regex: `(U.S.P.\|USP\|Unit Sale Price)[\s:]*(₹\|Rs.?)?\s*([\d\.]+\s*\/\s*(g\|kg\|ml\|l\|100g\|100ml\|n))`. |
| **9** | **Country of Origin** | **Rule 6(1)(n)** | Country of origin or manufacture declared on package (`Made in India`, `Product of India`). | Pattern matcher: `(Country of Origin\|Product of\|Made in)[\s:]*([A-Za-z\s]+)`. |

---

## 3. Assessment & Evaluation Logic (Calculation Rules)

The system computes a preliminary compliance score and status classification for each declaration.

### Status Definitions

```
                     ┌───────────────────────────────────────────────┐
                     │            Product Label OCR Text             │
                     └───────────────────────┬───────────────────────┘
                                             │
                       Is Declaration Found in OCR Text?
                                      /     \
                                     /       \
                                  YES         NO
                                  /             \
      Is formatting & mandatory   /               \  Is field mandatory
      sub-clauses present?       /                 \  for commodity?
             /     \            /                   \    /     \
            /       \          /                     \  YES     NO
          YES        NO       /                       \ /        \
           │          └──────┼────────┐                │          │
           ▼                 ▼        ▼                ▼          ▼
     ┌──────────┐   ┌───────────────────┐    ┌─────────────────┐ ┌──────────┐
     │ DETECTED │   │MANUAL VERIFICATION│    │ POTENTIAL ISSUE │ │ DETECTED │
     └──────────┘   └───────────────────┘    └─────────────────┘ └──────────┘
```

#### A. `DETECTED` (Green)
- **Condition**: Declaration exists in the OCR text AND matches standard legal formatting (e.g. MRP includes tax clause; Net Qty uses recognized standard metric unit).
- **Explanation**: "Declaration detected on label. Matches expected rule pattern."

#### B. `POTENTIAL_ISSUE` (Rust/Red)
- **Condition**: Mandatory declaration is missing from the scanned face OR lacks required legal sub-clauses (e.g., MRP declared without "inclusive of all taxes").
- **Explanation**: "Declaration appears missing or incomplete on the scanned face. Check packaging before concluding."

#### C. `MANUAL_VERIFICATION` (Amber/Yellow)
- **Condition**: OCR confidence is low (< 60%) OR entity role is ambiguous (e.g., company name detected, but OCR could not verify whether it is manufacturer or packer).
- **Explanation**: "Text detected but requires human verification for clarity, role distinction, or placement on package."

---

## 4. Academic Presentation & Viva Guide for Professors

### Q1: Why does the system evaluate status as "Preliminary Assessment" instead of "Pass/Fail"?
> **Answer**: Legal Metrology compliance involves visual inspection across all faces of a package (front, back, side panels). An automated single-image scan can only evaluate the scanned face. Labeling a product as "Legally Non-compliant" or "Pass" would be legally inaccurate. Hence, we use decision-support classifications (`DETECTED`, `POTENTIAL_ISSUE`, `MANUAL_VERIFICATION`).

### Q2: Why use Regex and Rule Engines over LLMs for information extraction?
> **Answer**: Legal compliance demands 100% deterministic, audit-traceable logic. LLMs are prone to hallucination and non-deterministic variations. Standardized Indian packaging declarations follow predictable syntax mandated by law, making regex + rule-based extraction faster, zero-cost, fully offline, and verifiable.

### Q3: How are discrepancies between old frontend mock data and official laws handled?
> **Answer**: Centralized rule metadata (`backend/compliance/rules_config.py`) serves as the single source of truth. Any outdated mock data references were audited and reconciled strictly against Rule 6(1) of LM(PC) Rules 2011 and Section 18 of the Legal Metrology Act, 2009.

---

*Document created for SIH26034 project evaluation.*
