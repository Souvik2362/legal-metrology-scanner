"""FastAPI Application Entrypoint for SIH26034 Legal Metrology Scanner."""

import os
import sys
import asyncio
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

# Ensure parent and current directories are in python path
backend_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(backend_dir, ".."))
for p in (backend_dir, project_root):
    if p not in sys.path:
        sys.path.insert(0, p)

try:
    from backend.ocr.ocr_engine import run_ocr_pipeline
    from backend.extraction.extractors import extract_all_declarations
    from backend.compliance.engine import run_compliance_assessment
    from backend.compliance.models import ScanResult
except ImportError:
    from ocr.ocr_engine import run_ocr_pipeline
    from extraction.extractors import extract_all_declarations
    from compliance.engine import run_compliance_assessment
    from compliance.models import ScanResult


app = FastAPI(
    title="SIH26034 Legal Metrology Compliance Scanner",
    description="Backend API for preliminary Legal Metrology label compliance scanning against Indian LM(PC) Rules 2011.",
    version="1.0.0",
)

# Enable CORS for Next.js frontend (localhost:3000)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/api/v1/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "ok",
        "service": "SIH26034 Product-Label Compliance Scanner API",
        "version": "1.0.0",
    }


@app.post("/api/v1/scan", response_model=ScanResult)
async def scan_label(image: UploadFile = File(...)):
    """Main image scan endpoint.

    Accepts an uploaded label photo (JPEG, PNG, WEBP), performs OpenCV preprocessing,
    extracts text via PaddleOCR, parses the 7 mandatory Legal Metrology declarations,
    and returns a preliminary compliance assessment.
    """
    if not image or not image.filename:
        raise HTTPException(status_code=400, detail="No image file provided.")

    try:
        image_bytes = await image.read()
        if not image_bytes or len(image_bytes) == 0:
            raise HTTPException(status_code=400, detail="Empty image file uploaded.")
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to read image bytes: {str(e)}")

    # 1. Run OCR Pipeline asynchronously in threadpool to prevent blocking event loop
    ocr_res = await asyncio.to_thread(run_ocr_pipeline, image_bytes)
    
    if ocr_res.get("status") == "ocr_unavailable":
        raise HTTPException(status_code=503, detail="OCR engine is currently initializing or unavailable.")

    if ocr_res.get("status") == "error" and ocr_res.get("line_count", 0) == 0:
        raise HTTPException(
            status_code=422,
            detail="No legible text detected on the uploaded image. Please ensure the label is in focus, evenly lit, and not blurred.",
        )

    raw_text = ocr_res.get("raw_text", "")
    avg_confidence = ocr_res.get("avg_confidence", 0.85)

    # 2. Extract Mandatory Legal Metrology Fields (9 statutory checks)
    extracted_declarations = extract_all_declarations(raw_text)

    # 3. Evaluate Preliminary Compliance Assessment
    scan_result = run_compliance_assessment(
        extracted_declarations=extracted_declarations,
        avg_ocr_confidence=avg_confidence,
        image_url=image.filename,
        raw_ocr_text=raw_text,
    )

    return scan_result


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
