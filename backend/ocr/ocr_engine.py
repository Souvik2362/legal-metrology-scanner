"""PaddleOCR Engine Integration Module.

Provides lazy-loaded PaddleOCR model execution with angle classification,
preprocessed image pipeline, and structured output parsing.
"""

from typing import Dict, Any, List, Optional
import numpy as np
try:
    from backend.image_processing.preprocessor import decode_image_bytes, preprocess_for_ocr
except ImportError:
    from image_processing.preprocessor import decode_image_bytes, preprocess_for_ocr


# Lazy global OCR instance
_PADDLE_OCR_INSTANCE = None
_PADDLE_AVAILABLE = None


def get_ocr_instance():
    """Lazily initialize and return the global PaddleOCR instance."""
    global _PADDLE_OCR_INSTANCE, _PADDLE_AVAILABLE

    if _PADDLE_OCR_INSTANCE is not None:
        return _PADDLE_OCR_INSTANCE

    try:
        from paddleocr import PaddleOCR
        # Initialize PaddleOCR with English language model and angle classification enabled
        _PADDLE_OCR_INSTANCE = PaddleOCR(
            use_angle_cls=True,
            lang="en",
            show_log=False,
            enable_mkldnn=True,
        )
        _PADDLE_AVAILABLE = True
        return _PADDLE_OCR_INSTANCE
    except Exception as e:
        _PADDLE_AVAILABLE = False
        print(f"[OCR Engine Warning] PaddleOCR initialization skipped or failed: {e}")
        return None


def run_ocr_pipeline(image_bytes: bytes) -> Dict[str, Any]:
    """Execute complete image decoding, OpenCV preprocessing, and PaddleOCR extraction.

    Returns:
        Dict containing:
        - 'raw_text': Full concatenated string of detected label text
        - 'lines': List of dicts with 'text', 'confidence', 'box'
        - 'avg_confidence': Mean confidence score across all lines
        - 'line_count': Total number of detected text lines
        - 'status': 'success' or 'error'
    """
    # 1. Decode image bytes
    image_matrix = decode_image_bytes(image_bytes)
    if image_matrix is None:
        return {
            "status": "error",
            "error_message": "Could not decode image file bytes.",
            "raw_text": "",
            "lines": [],
            "avg_confidence": 0.0,
            "line_count": 0,
        }

    # 2. Preprocess image with OpenCV
    try:
        preprocessed = preprocess_for_ocr(image_matrix)
    except Exception:
        preprocessed = image_matrix  # Fallback to raw matrix if preprocessing fails

    # 3. Obtain PaddleOCR engine instance
    ocr_engine = get_ocr_instance()
    if ocr_engine is None:
        # Fallback response if PaddleOCR is not installed/loading in test environment
        return {
            "status": "ocr_unavailable",
            "error_message": "PaddleOCR engine is not loaded.",
            "raw_text": "",
            "lines": [],
            "avg_confidence": 0.0,
            "line_count": 0,
        }

    # 4. Perform OCR inference
    try:
        # PaddleOCR accepts numpy image array directly
        results = ocr_engine.ocr(preprocessed, cls=True)
    except Exception as e:
        return {
            "status": "error",
            "error_message": f"OCR inference error: {str(e)}",
            "raw_text": "",
            "lines": [],
            "avg_confidence": 0.0,
            "line_count": 0,
        }

    # 5. Parse PaddleOCR detection output structure: [[box, (text, confidence)], ...]
    extracted_lines: List[Dict[str, Any]] = []
    text_blocks: List[str] = []
    total_conf = 0.0

    if results and len(results) > 0 and results[0] is not None:
        for line in results[0]:
            try:
                box = line[0]
                text, confidence = line[1]
                text = str(text).strip()
                confidence = float(confidence)

                if text:
                    text_blocks.append(text)
                    extracted_lines.append({
                        "text": text,
                        "confidence": round(confidence, 4),
                        "box": box,
                    })
                    total_conf += confidence
            except (IndexError, ValueError):
                continue

    line_count = len(extracted_lines)
    avg_confidence = round(total_conf / line_count, 4) if line_count > 0 else 0.0
    raw_text = "\n".join(text_blocks)

    return {
        "status": "success",
        "raw_text": raw_text,
        "lines": extracted_lines,
        "avg_confidence": avg_confidence,
        "line_count": line_count,
    }
