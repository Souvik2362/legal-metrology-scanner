"""Unit tests for OpenCV preprocessor and PaddleOCR pipeline."""

import os
import sys
import unittest
import numpy as np
import cv2

# Ensure project root is in python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from backend.image_processing.preprocessor import (
    decode_image_bytes,
    preprocess_for_ocr,
    resize_if_needed,
)
from backend.ocr.ocr_engine import run_ocr_pipeline


class TestOCRPreprocessing(unittest.TestCase):

    def setUp(self):
        # Create a synthetic image with text in memory
        img = np.full((400, 600, 3), 255, dtype=np.uint8)
        cv2.putText(img, "MRP Rs 189.00", (50, 100), cv2.FONT_HERSHEY_SIMPLEX, 1.0, (0, 0, 0), 2)
        cv2.putText(img, "Net Qty: 1 L", (50, 200), cv2.FONT_HERSHEY_SIMPLEX, 1.0, (0, 0, 0), 2)
        cv2.putText(img, "Batch: SR24B0417", (50, 300), cv2.FONT_HERSHEY_SIMPLEX, 1.0, (0, 0, 0), 2)
        
        is_success, buffer = cv2.imencode(".png", img)
        self.assertTrue(is_success)
        self.sample_bytes = buffer.tobytes()
        self.sample_img = img

    def test_decode_image_bytes(self):
        decoded = decode_image_bytes(self.sample_bytes)
        self.assertIsNotNone(decoded)
        self.assertEqual(len(decoded.shape), 3)
        self.assertEqual(decoded.shape[2], 3)

    def test_decode_invalid_bytes(self):
        decoded = decode_image_bytes(b"invalid image bytes")
        self.assertIsNone(decoded)

    def test_preprocess_for_ocr(self):
        processed = preprocess_for_ocr(self.sample_img)
        self.assertIsNotNone(processed)
        # Should be grayscale (2D array)
        self.assertEqual(len(processed.shape), 2)

    def test_resize_if_needed(self):
        # Test downscaling very large image
        large_img = np.zeros((3000, 4000, 3), dtype=np.uint8)
        resized = resize_if_needed(large_img, max_dim=2000)
        self.assertLessEqual(max(resized.shape[:2]), 2000)

        # Test upscaling small image
        small_img = np.zeros((200, 300, 3), dtype=np.uint8)
        resized_small = resize_if_needed(small_img, min_dim=600)
        self.assertGreaterEqual(min(resized_small.shape[:2]), 600)

    def test_run_ocr_pipeline_invalid_bytes(self):
        res = run_ocr_pipeline(b"bad bytes")
        self.assertEqual(res["status"], "error")
        self.assertEqual(res["line_count"], 0)


if __name__ == "__main__":
    unittest.main()
