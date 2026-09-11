# SIH26034 — Legal Metrology Compliance Scanner Backend

Backend microservice built with **Python 3.13**, **FastAPI**, **OpenCV**, **PaddleOCR**, and **Regex Normalization Rules** to perform preliminary compliance assessments against Indian Legal Metrology regulations.

---

## Technical Stack
- **Framework**: FastAPI + Uvicorn
- **Image Preprocessing**: OpenCV (`cv2`), NumPy, Pillow
- **OCR Engine**: PaddleOCR (with text angle classification)
- **Extraction Engine**: Python Regex, Keyword Parsing, Unit Normalization
- **Rule Engine**: Modular Legal Metrology Rule Registry (`rules_config.py`)

---

## Setup & Running Locally

### 1. Virtual Environment & Installation
```powershell
cd backend
python -m venv venv
.\venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Start FastAPI Server
```powershell
uvicorn main:app --reload --port 8000
```
Server runs at: `http://localhost:8000`  
Swagger API Docs available at: `http://localhost:8000/docs`

---

## API Endpoints

### Health Check
`GET /api/v1/health`

### Label Scan Endpoint
`POST /api/v1/scan`
- **Request**: `multipart/form-data` with `image` file field.
- **Response**: JSON matching `ScanResult` schema.

```json
{
  "scanId": "SCN-582910",
  "imageUrl": "uploaded_label.jpg",
  "scannedAt": "2026-09-11T04:15:00.000Z",
  "product": {
    "name": "Refined Sunflower Oil",
    "brand": "Sunridge",
    "netQuantity": "1 L",
    "mrp": "₹189.00 (incl. of all taxes)",
    "batchNumber": "SR24B0417",
    "mfgDate": "03/2026",
    "packerAddress": "Sunridge Agro Pvt. Ltd., MIDC Nashik 422010",
    "customerCareText": "care@sunridge.com",
    "bestBefore": "Best before 9 months"
  },
  "checks": [
    {
      "id": "mrp",
      "label": "MRP / Retail Sale Price declaration",
      "status": "detected",
      "reading": "₹189.00 (incl. of all taxes)",
      "ruleRef": "Rule 6(1)(e) — Legal Metrology (Packaged Commodities) Rules, 2011",
      "reason": null
    }
  ]
}
```

---

## Automated Unit Tests

Run all test suites:
```powershell
.\venv\Scripts\python.exe -m unittest discover -s tests
```

---

## Statutory References

All backend rules enforce:
- **Parent Law**: Section 18 — Legal Metrology Act, 2009
- **Operating Rules**: Legal Metrology (Packaged Commodities) Rules, 2011 — Rule 6(1)
  - `mrp`: Rule 6(1)(e)
  - `net_quantity`: Rule 6(1)(c) + Rule 11 + Rule 12
  - `manufacturer_packer`: Rule 6(1)(a)
  - `batch_lot`: Rule 6(1)(b)
  - `mfg_date`: Rule 6(1)(d)
  - `best_before`: Rule 6(1)(da)
  - `consumer_care`: Rule 6(1)(f)

For detailed presentation guides and viva Q&A, refer to [`LEGAL_RULES_AND_ASSESSMENT_GUIDE.md`](LEGAL_RULES_AND_ASSESSMENT_GUIDE.md).
