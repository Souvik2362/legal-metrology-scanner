Yes. For the **root of `legal-metrology-scanner`**, I would use a README that describes the complete system rather than just the frontend.

Replace the project's root `README.md` with this:

````markdown
# Metrology Scan — Product-Label Compliance Scanner

A web-based system for performing a preliminary compliance assessment of packaged-product labels against applicable Legal Metrology requirements in India.

The system accepts a product-label image, extracts relevant declarations using OCR and image processing, applies rule-based compliance checks, and presents explainable results for each detected requirement.

> **Important:** Metrology Scan is an assistive inspection and decision-support tool. It does not provide legal certification or replace official regulatory verification.

---

## SIH Problem Statement

**SIH26034 — Product-Label Compliance Scanner**

> Software System to check compliance of Packaged Commodities under Legal Metrology (Packaged Commodities) Rules, 2011 by scanning products, images and labels.

**Theme:** Miscellaneous  
**Category:** Software

---

## Overview

Packaged commodities in India are required to display several mandatory declarations, such as:

- Maximum Retail Price (MRP)
- Net quantity
- Manufacturer / packer / importer details
- Batch or lot information, where applicable
- Date-related declarations
- Consumer care information
- Other applicable mandatory declarations

Manually checking these declarations across large numbers of products can be time-consuming.

Metrology Scan provides a digital workflow that helps inspect product labels by combining:

1. Image preprocessing
2. Optical Character Recognition (OCR)
3. Information extraction
4. Rule-based compliance checking
5. Explainable compliance assessment

---

## System Workflow

```text
                Product Label Image
                        │
                        ▼
                Image Processing
              OpenCV / Preprocessing
                        │
                        ▼
                       OCR
                    PaddleOCR
                        │
                        ▼
              Information Extraction
          Regex / Keywords / Normalization
                        │
                        ▼
             Compliance Rule Engine
             Legal Metrology Rules
                        │
                        ▼
            Compliance Assessment
       Detected / Needs Verification / Not Found
                        │
                        ▼
              Explainable Results
          Rule Reference + Reason + Text
````

---

## Key Features

### 1. Product Image Upload

Users can upload a product-label image through the web interface.

Supported workflow includes:

* File selection
* Drag and drop
* Image preview
* Scan initiation

### 2. Image Preprocessing

The backend preprocesses product images before OCR to improve text recognition.

Processing may include:

* Resizing
* Denoising
* Contrast enhancement
* Rotation handling
* Image enhancement for faint text

OpenCV is used for image-processing operations.

### 3. OCR-Based Text Extraction

PaddleOCR is used to detect and recognize text present on product labels.

The OCR pipeline can provide:

* Extracted text
* Text regions / bounding boxes
* Recognition confidence
* Multiple OCR passes when important declarations are missing

### 4. Information Extraction

Relevant declarations are extracted from OCR output using:

* Regular expressions
* Keywords
* Pattern matching
* Text normalization

Examples include:

* MRP
* Net quantity
* Batch / lot number
* Manufacturing date
* Best-before / use-by information
* Manufacturer / packer / importer details
* Consumer care information

### 5. Rule-Based Compliance Engine

Extracted information is evaluated against configurable Legal Metrology requirements.

The compliance engine is modular so that additional rules and product categories can be added without redesigning the entire application.

### 6. Explainable Results

The system does not reduce the result to a simple "Pass" or "Fail".

Each requirement can be reported as:

* **Detected**
* **Needs Verification**
* **Not Found**

The result can provide:

* Requirement being checked
* Detected information
* Reason for the assessment
* Applicable rule reference
* Items requiring manual verification

---

## Compliance Assessment

A detected declaration does not automatically mean that the product is legally compliant.

For example:

```text
MRP
├── Detected
├── Needs Verification
└── Not Found
```

The system is intended to identify potentially missing, unclear, or questionable declarations and assist an inspector or user in further verification.

This approach helps reduce false certainty caused by OCR errors or ambiguous packaging information.

---

## Technology Stack

### Frontend

* Next.js
* React
* TypeScript
* Tailwind CSS

### Backend

* Python
* FastAPI
* Uvicorn
* Pydantic

### OCR

* PaddleOCR
* PaddlePaddle
* PaddleX

### Image Processing

* OpenCV
* Pillow
* NumPy

### Information Extraction

* Python Regular Expressions
* Keyword matching
* Text normalization

### Compliance Engine

* Python
* Modular rule-based architecture
* Data-driven rule configuration
* YAML / JSON configuration where applicable

### Testing

* Pytest

---

## Project Structure

```text
legal-metrology-scanner/
│
├── backend/
│   ├── compliance/
│   │   ├── engine.py
│   │   ├── models.py
│   │   └── rules_config.py
│   │
│   ├── extraction/
│   │   ├── extractors.py
│   │   └── normalizer.py
│   │
│   ├── image_processing/
│   │   └── preprocessor.py
│   │
│   ├── ocr/
│   │   ├── ocr_engine.py
│   │   └── OCR.yaml
│   │
│   ├── main.py
│   ├── requirements.txt
│   └── tests/
│
├── frontend/
│   ├── app/
│   │   └── page.tsx
│   │
│   ├── components/
│   │   ├── UploadScreen.tsx
│   │   ├── ScanningScreen.tsx
│   │   └── ResultsScreen.tsx
│   │
│   ├── lib/
│   │   ├── types.ts
│   │   └── mock-data.ts
│   │
│   ├── package.json
│   └── README.md
│
├── Test_Images/
│   └── product_01 ... product_17
│
├── .gitignore
└── README.md
```

---

# Installation

## Prerequisites

Install the following:

* Python 3.12
* Node.js
* npm
* Git

Python 3.12 is recommended for the current PaddleOCR/PaddlePaddle setup.

---

## Backend Setup

Open a terminal in the project directory:

```bash
cd backend
```

Create and activate a virtual environment if desired:

### Windows

```bat
py -3.12 -m venv .venv
.venv\Scripts\activate
```

Install dependencies:

```bat
py -3.12 -m pip install -r requirements.txt
```

Start the FastAPI server:

```bat
py -3.12 -m uvicorn main:app --reload --host 127.0.0.1 --port 8000
```

The backend will be available at:

```text
http://localhost:8000
```

Health check:

```text
http://localhost:8000/api/v1/health
```

---

## Frontend Setup

Open another terminal:

```bash
cd frontend
```

Install dependencies:

```bash
npm install
```

Start the development server:

```bash
npm run dev
```

The frontend will be available at:

```text
http://localhost:3000
```

---

# Running the Application

Start both services.

### Terminal 1 — Backend

```bat
cd backend
py -3.12 -m uvicorn main:app --reload --host 127.0.0.1 --port 8000
```

### Terminal 2 — Frontend

```bat
cd frontend
npm run dev
```

Then open:

```text
http://localhost:3000
```

Upload a product-label image and start a scan.

The frontend sends the image to:

```text
POST /api/v1/scan
```

The backend processes the image and returns the scan result to the frontend.

---

# API

## Health Check

```http
GET /api/v1/health
```

Used to verify that the backend is running.

---

## Scan Product Label

```http
POST /api/v1/scan
```

### Request

Multipart form-data containing:

```text
image: <product label image>
```

### Processing

```text
Image
  ↓
Preprocessing
  ↓
OCR
  ↓
Information Extraction
  ↓
Compliance Assessment
  ↓
ScanResult
```

The frontend consumes the returned `ScanResult` and displays the extracted information and compliance findings.

---

# Legal and Regulatory Basis

The compliance engine is designed around applicable provisions of Indian Legal Metrology regulations, including relevant declarations under the:

**Legal Metrology (Packaged Commodities) Rules, 2011**

Examples of requirements considered by the prototype include:

| Declaration                      | Example Rule Reference          |
| -------------------------------- | ------------------------------- |
| Manufacturer / Packer / Importer | Rule 6(1)(a)                    |
| Batch / Lot                      | Rule 6(1)(b), where applicable  |
| Net Quantity                     | Rule 6(1)(c)                    |
| Date Declaration                 | Rule 6(1)(d)                    |
| Best Before / Use By             | Rule 6(1)(da), where applicable |
| MRP / Retail Sale Price          | Rule 6(1)(e)                    |
| Consumer Care                    | Rule 6(1)(f)                    |

The parent legislation is the **Legal Metrology Act, 2009**, including Section 18 concerning packaged commodities.

The exact applicability of individual requirements can depend on the product category and applicable provisions. Therefore, the system uses **Needs Verification** where automated assessment cannot establish compliance with sufficient confidence.

---

# Accuracy and Limitations

The system is designed as a prototype and has limitations.

### OCR limitations

OCR performance can be affected by:

* Blurry images
* Low-resolution photographs
* Small text
* Faint inkjet or dot-matrix printing
* Reflections
* Shadows
* Curved packaging
* Complex backgrounds
* Unusual fonts
* Rotated text

### Compliance limitations

The system cannot reliably establish every aspect of legal compliance from OCR alone.

For example, some requirements may depend on:

* Text placement
* Font size
* Physical dimensions
* Product category
* Packaging characteristics
* Visual readability
* Applicable exceptions

Therefore, automated results should be treated as a **preliminary assessment** and manually verified where necessary.

---

# Design Principles

The project follows several design principles:

### Explainability

The system should explain why a declaration was detected, flagged, or not found.

### Modularity

OCR, extraction, preprocessing, and compliance rules are separated into independent modules.

### Rule-Based Compliance

Legal requirements are represented through configurable rules rather than relying on an opaque model to make the final compliance decision.

### Human Verification

Uncertain cases are explicitly marked for manual verification rather than being presented as definitive legal violations.

### Extensibility

The architecture allows additional:

* Product categories
* Compliance rules
* Extraction patterns
* OCR improvements
* Reporting functionality

to be added later.

---

# Testing

The repository contains a collection of product-label test images under:

```text
Test_Images/
```

The current prototype includes 17 test images representing different product labels and packaging conditions.

Backend tests can be run using:

```bash
pytest
```

---

# Current Prototype Scope

The current implementation focuses on the core end-to-end workflow:

```text
Upload
  ↓
Image Processing
  ↓
OCR
  ↓
Information Extraction
  ↓
Rule-Based Assessment
  ↓
Explainable Results
```

The prototype prioritizes high-confidence declaration detection and transparent rule evaluation rather than attempting complete automated legal certification.

---

# Future Enhancements

Potential future improvements include:

* Visual highlighting of detected violations
* More advanced readability analysis
* Automated font-size estimation
* Expanded product-category rules
* Multilingual label support
* Improved handling of curved packaging
* Better detection of faint and low-contrast text
* Compliance history and scan repository
* Search and dashboard functionality
* PDF and editable compliance reports
* Role-based access
* Larger real-world product-label datasets
* Improved confidence scoring
* Human-in-the-loop verification workflows

---

# Team

**Team Minions**

| Member    | Responsibility                              |
| --------- | ------------------------------------------- |
| Souvik    | Integration & Core Development              |
| Suraj     | OCR + Backend                               |
| Subhankar | Legal Metrology Research + Compliance Rules |
| Maitry    | Frontend / UI                               |
| Raman     | Testing + Product-Label Dataset             |
| Suchandra | Documentation / PPT / Demo                  |

---

# Disclaimer

Metrology Scan is a software prototype developed for the Smart India Hackathon problem statement **SIH26034**.

The system provides a preliminary automated assessment of product-label declarations. Its output should not be interpreted as official legal advice, certification, or a final determination of compliance.

Official regulatory requirements and their applicability should be verified against the latest applicable legislation, rules, notifications, and competent-authority guidance.

---

# License

This project is developed as part of the Smart India Hackathon 2026 and is intended for educational, demonstration, and prototype purposes.

