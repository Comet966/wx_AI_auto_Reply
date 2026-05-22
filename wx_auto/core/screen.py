"""Screen capture and OCR for WeChat Auto Reply Bot."""
from pathlib import Path
from typing import List, Optional, Tuple

import cv2
import mss
import numpy as np
from PIL import Image

from wx_auto.utils.logger import logger


class ScreenCapture:
    """Screen capture using mss."""

    def __init__(self):
        """Initialize screen capture."""
        self._sct = mss.mss()

    def capture(
        self,
        region: Tuple[int, int, int, int] = None,
    ) -> Image.Image:
        """Capture screen or region.

        Args:
            region: (left, top, width, height). If None, captures entire screen.

        Returns:
            PIL Image
        """
        if region:
            left, top, width, height = region
            monitor = {"left": left, "top": top, "width": width, "height": height}
        else:
            monitor = self._sct.monitors[0]

        # Capture using mss
        screenshot = self._sct.grab(monitor)

        # Convert to PIL Image
        img = Image.frombytes("RGB", screenshot.size, screenshot.bgra, "raw", "BGRX")
        return img

    def capture_to_file(
        self,
        filepath: str,
        region: Tuple[int, int, int, int] = None,
    ) -> None:
        """Capture and save to file.

        Args:
            filepath: Output file path
            region: (left, top, width, height)
        """
        img = self.capture(region)
        img.save(filepath)
        logger.debug(f"Screenshot saved to {filepath}")

    def close(self) -> None:
        """Close screen capture."""
        self._sct.close()


class OCREngine:
    """OCR engine using cnocr."""

    def __init__(self):
        """Initialize OCR engine."""
        try:
            from cnocr import CnOcr

            self._ocr = CnOcr()
            logger.info("OCR engine initialized")
        except ImportError:
            logger.warning("cnocr not installed, OCR will be disabled")
            self._ocr = None

    def recognize(self, image: Image.Image) -> List[str]:
        """Recognize text from image.

        Args:
            image: PIL Image

        Returns:
            List of recognized text lines
        """
        if self._ocr is None:
            logger.warning("OCR not available, install cnocr: pip install cnocr")
            return []

        try:
            # Convert PIL Image to cnocr format
            img_np = np.array(image)
            results = self._ocr.ocr(img_np)

            texts = []
            for line in results:
                if line and "text" in line:
                    texts.append(line["text"])

            return texts

        except Exception as e:
            logger.error(f"OCR recognition failed: {e}")
            return []

    def recognize_text(self, image: Image.Image) -> str:
        """Recognize and join all text.

        Args:
            image: PIL Image

        Returns:
            Concatenated text
        """
        texts = self.recognize(image)
        return "\n".join(texts)


class ScreenReader:
    """Combined screen capture and OCR."""

    def __init__(self):
        """Initialize screen reader."""
        self.capture = ScreenCapture()
        self.ocr = OCREngine()

    def read_wechat_messages(
        self,
        region: Tuple[int, int, int, int] = None,
    ) -> List[str]:
        """Read messages from WeChat window.

        Args:
            region: (left, top, width, height) of message area

        Returns:
            List of message texts
        """
        img = self.capture.capture(region)
        return self.ocr.recognize(img)

    def close(self) -> None:
        """Close resources."""
        self.capture.close()


# Global instances
screen_capture = ScreenCapture()
ocr_engine = OCREngine()