"""OpenCV Image Preprocessor for Product Label OCR Enhancement.

Preprocesses product label photos to optimize text legibility for PaddleOCR.
Routines include contrast adjustment (CLAHE), grayscale conversion, noise reduction,
and resolution scaling.
"""

from typing import Tuple, Optional
import cv2
import numpy as np


def decode_image_bytes(image_bytes: bytes) -> Optional[np.ndarray]:
    """Decode raw image bytes (JPEG, PNG, WEBP) into an OpenCV BGR matrix."""
    if not image_bytes:
        return None
    try:
        np_arr = np.frombuffer(image_bytes, np.uint8)
        image = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)
        return image
    except Exception:
        return None


def resize_if_needed(image: np.ndarray, max_dim: int = 2000, min_dim: int = 600) -> np.ndarray:
    """Resize image to maintain resolution in optimal OCR range [min_dim, max_dim]."""
    h, w = image.shape[:2]
    max_side = max(h, w)
    min_side = min(h, w)

    # Downscale if image is excessively large
    if max_side > max_dim:
        scale = max_dim / float(max_side)
        new_w = int(w * scale)
        new_h = int(h * scale)
        return cv2.resize(image, (new_w, new_h), interpolation=cv2.INTER_AREA)

    # Upscale if image is too small for small text legibility
    if min_side < min_dim:
        scale = min_dim / float(min_side)
        new_w = int(w * scale)
        new_h = int(h * scale)
        return cv2.resize(image, (new_w, new_h), interpolation=cv2.INTER_CUBIC)

    return image


def preprocess_for_ocr(
    image: np.ndarray,
    use_clahe: bool = True,
    use_denoise: bool = True,
) -> np.ndarray:
    """Preprocess image matrix to maximize OCR detection & recognition accuracy.

    Steps:
    1. Dimension normalization / scaling
    2. Grayscale conversion
    3. CLAHE contrast enhancement (Contrast Limited Adaptive Histogram Equalization)
    4. Bilateral filter noise reduction (preserves sharp text edges)
    """
    if image is None or image.size == 0:
        raise ValueError("Invalid or empty image matrix provided for preprocessing.")

    # 1. Scale image to optimal OCR dimensions
    processed = resize_if_needed(image)

    # 2. Grayscale conversion
    if len(processed.shape) == 3 and processed.shape[2] == 3:
        gray = cv2.cvtColor(processed, cv2.COLOR_BGR2GRAY)
    else:
        gray = processed.copy()

    # 3. CLAHE Contrast Enhancement
    if use_clahe:
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
        gray = clahe.apply(gray)

    # 4. Noise Reduction preserving edges
    if use_denoise:
        gray = cv2.bilateralFilter(gray, d=7, sigmaColor=50, sigmaSpace=50)

    return gray


def binarize_for_text(gray: np.ndarray) -> np.ndarray:
    """Adaptive Gaussian thresholding to binarize text against complex packaging backgrounds."""
    return cv2.adaptiveThreshold(
        gray,
        255,
        cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
        cv2.THRESH_BINARY,
        blockSize=11,
        C=2,
    )
