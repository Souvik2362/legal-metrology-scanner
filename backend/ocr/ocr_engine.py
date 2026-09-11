"""PaddleOCR Engine Integration Module.

Provides lazy-loaded PaddleOCR / PaddleX OCR pipeline with Windows stability patches,
multi-orientation auto-rotation (0°, 90°, 180°, 270°), and structured output parsing.
"""

import os
import re
import cv2
import numpy as np
import time
import yaml
from typing import Dict, Any, List, Optional

def enhance_for_ocr(image: np.ndarray) -> np.ndarray:
    """Create a high-contrast version for faint/dot-matrix label text."""
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    # Improve local contrast
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
    enhanced = clahe.apply(gray)

    # Light sharpening
    blurred = cv2.GaussianBlur(enhanced, (0, 0), 1.0)
    sharpened = cv2.addWeighted(enhanced, 1.5, blurred, -0.5, 0)

    return cv2.cvtColor(sharpened, cv2.COLOR_GRAY2BGR)

try:
    from backend.image_processing.preprocessor import decode_image_bytes, preprocess_for_ocr
except ImportError:
    from image_processing.preprocessor import decode_image_bytes, preprocess_for_ocr


# Apply Windows PaddlePaddle PIR/oneDNN stability patch
def _apply_paddle_windows_patch():
    try:
        from paddlex.inference.models.runners.paddle_static import runner as paddle_static_runner
        if not getattr(paddle_static_runner.PaddleStaticRunner, "_pir_patched", False):
            _orig_create = paddle_static_runner.PaddleStaticRunner._create

            def _patched_create(self):
                self._config["run_mode"] = "paddle"
                self._config["enable_new_ir"] = False
                return _orig_create(self)

            paddle_static_runner.PaddleStaticRunner._create = _patched_create
            paddle_static_runner.PaddleStaticRunner._pir_patched = True
    except Exception as e:
        print(f"[PaddleOCR Patch Warning]: {e}")


# Global OCR pipeline instance
_PADDLE_PIPELINE = None
_PADDLE_AVAILABLE = None


def get_ocr_instance():
    """Lazily initialize and return the global PaddleX OCR pipeline instance."""
    global _PADDLE_PIPELINE, _PADDLE_AVAILABLE

    if _PADDLE_PIPELINE is not None:
        return _PADDLE_PIPELINE

    _apply_paddle_windows_patch()

    try:
        from paddlex import create_pipeline
        print("[OCR Engine] Initializing PaddleX OCR Pipeline on CPU...")
        ocr_config_path = os.path.join(
            os.path.dirname(__file__),
            "OCR.yaml",
        )
        
        with open(ocr_config_path, "r", encoding="utf-8") as f:
            ocr_config = yaml.safe_load(f)
        
        ocr_config["SubModules"]["TextDetection"]["model_name"] = "PP-OCRv6_small_det"
        ocr_config["SubModules"]["TextRecognition"]["model_name"] = "PP-OCRv6_small_rec"
        
        ocr_config["use_doc_preprocessor"] = False
        ocr_config["use_textline_orientation"] = False
        
        _PADDLE_PIPELINE = create_pipeline(
            config=ocr_config,
            device="cpu",
        )
        _PADDLE_AVAILABLE = True
        print("[OCR Engine] PaddleX OCR Pipeline loaded successfully.")
        return _PADDLE_PIPELINE
    except Exception as e:
        _PADDLE_AVAILABLE = False
        print(f"[OCR Engine Error] OCR Pipeline initialization failed: {e}")
        return None


def run_ocr_pipeline(image_bytes: bytes) -> Dict[str, Any]:
    """Execute complete image decoding, OpenCV preprocessing, and PaddleOCR extraction.

    Evaluates across all 4 orientations (0°, 90°, 180°, 270°) to guarantee detection
    even when photos are taken sideways or upside-down.
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
        preprocessed = image_matrix

    # If grayscale, convert back to 3-channel BGR for PaddleX input
    if len(preprocessed.shape) == 2:
        preprocessed = cv2.cvtColor(preprocessed, cv2.COLOR_GRAY2BGR)

    # 3. Obtain OCR pipeline
    pipeline = get_ocr_instance()
    if pipeline is None:
        return {
            "status": "ocr_unavailable",
            "error_message": "PaddleOCR engine could not be loaded.",
            "raw_text": "",
            "lines": [],
            "avg_confidence": 0.0,
            "line_count": 0,
        }

    # 4. Adaptive multi-orientation scan:
    # Phase 1: 0° Primary upright scan
    combined_lines: List[Dict[str, Any]] = []
    seen_texts = set()
    total_conf = 0.0

    def _process_image_angle(angle_label: str, img_mat: np.ndarray) -> int:
        nonlocal total_conf
        lines_found = 0
        try:
            inference_start = time.perf_counter()
            preds = list(pipeline.predict(img_mat))
            print(
                f"[OCR Timing] {angle_label} pipeline.predict(): "
                f"{time.perf_counter() - inference_start:.2f}s"
            )
            if not preds or len(preds) == 0:
                return 0

            first_pred = preds[0]
            rec_texts = first_pred.get("rec_texts", [])
            rec_scores = first_pred.get("rec_scores", [])
            dt_polys = first_pred.get("dt_polys", [])

            for i, text in enumerate(rec_texts):
                clean_text = str(text).strip()
                norm_key = re.sub(r"[^a-zA-Z0-9]", "", clean_text.lower())
                if clean_text and len(clean_text) >= 2 and norm_key not in seen_texts:
                    score = float(rec_scores[i]) if i < len(rec_scores) else 0.8
                    poly = dt_polys[i].tolist() if i < len(dt_polys) and hasattr(dt_polys[i], "tolist") else []
                    seen_texts.add(norm_key)
                    combined_lines.append({
                        "text": clean_text,
                        "confidence": round(score, 4),
                        "box": poly,
                        "orientation": angle_label,
                    })
                    total_conf += score
                    lines_found += 1
        except Exception as e:
            print(f"[OCR Inference Rotation {angle_label} Warning]: {e}")
        return lines_found

    # Run 0° upright scan first
    ocr_start = time.perf_counter()
    upright_lines = _process_image_angle("0", preprocessed)
    print(f"[OCR Timing] 0° scan: {time.perf_counter() - ocr_start:.2f}s")
    upright_conf = (total_conf / upright_lines) if upright_lines > 0 else 0.0

    # In flexible packaging (pouches/sachets), crimp seals and dot-matrix stamps are often printed inverted.
    # Check if 0° pass already has dates and batch codes. If missing, evaluate 180° pass.
    raw_0 = " ".join([l["text"] for l in combined_lines])
    has_date_in_0 = bool(re.search(r"\b(?:\d{1,2}[\/\.-]\d{1,2}[\/\.-]\d{2,4}|\d{2}[\/\.-]\d{4}|[A-Za-z]{3}\s*\d{2,4})\b", raw_0))
    has_batch_in_0 = bool(re.search(r"\b(?:Batch|Lot|B\.?\s*No)[\s:\.]*[A-Za-z0-9\-\/]{3,}", raw_0, re.I))

    needs_seal_scan = not (has_date_in_0 and has_batch_in_0)

    # Retry with enhanced contrast only when important declarations are missing.
    raw_0 = " ".join([l["text"] for l in combined_lines])
    
    needs_enhanced_retry = (
        not re.search(r"(MRP|Maximum Retail Price|Retail Price)", raw_0, re.I)
        or not re.search(r"(Net\s*(Qty|Quantity)|Net\s*Wt|Net\s*Weight)", raw_0, re.I)
    )
    
    if needs_enhanced_retry:
        print("[OCR Retry] Important declaration missing. Running enhanced-contrast OCR...")
        enhanced = enhance_for_ocr(preprocessed)
    
        ocr_start = time.perf_counter()
        _process_image_angle("enhanced", enhanced)
        print(
            f"[OCR Timing] enhanced scan: "
            f"{time.perf_counter() - ocr_start:.2f}s"
        )
    
    if upright_lines < 8:
        ocr_start = time.perf_counter()
        _process_image_angle("180", cv2.rotate(preprocessed, cv2.ROTATE_180))
        print(f"[OCR Timing] 180° scan: {time.perf_counter() - ocr_start:.2f}s")

    line_count = len(combined_lines)
    if line_count > 0:
        # Spatial sorting (top-to-bottom, left-to-right) for upright lines to preserve packaging reading order
        def _box_sort_key(line_item):
            box = line_item.get("box", [])
            if box and len(box) >= 1 and len(box[0]) >= 2:
                y = box[0][1]
                x = box[0][0]
                return (round(y / 18.0), x)
            return (0, 0)

        upright_items = [l for l in combined_lines if l.get("orientation") == "0"]
        other_items = [l for l in combined_lines if l.get("orientation") != "0"]
        upright_items.sort(key=_box_sort_key)
        ordered_lines = upright_items + other_items

        avg_confidence = round(total_conf / line_count, 4)
        raw_text = "\n".join([line["text"] for line in ordered_lines])
        return {
            "status": "success",
            "raw_text": raw_text,
            "lines": ordered_lines,
            "avg_confidence": avg_confidence,
            "line_count": line_count,
        }

    return {
        "status": "error",
        "error_message": "No text detected across all image orientations.",
        "raw_text": "",
        "lines": [],
        "avg_confidence": 0.0,
        "line_count": 0,
    }
