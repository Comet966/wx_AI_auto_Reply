"""Message detector by comparing screenshots."""
import hashlib
import random
import time
from pathlib import Path
from typing import List, Optional, Tuple

import cv2
import numpy as np
from PIL import Image

from wx_auto.core.screen import ScreenCapture
from wx_auto.utils.config import config
from wx_auto.utils.logger import logger


class MessageDetector:
    """Detect new WeChat messages by comparing screenshots."""

    def __init__(self, capture: ScreenCapture = None):
        """Initialize message detector.

        Args:
            capture: Screen capture instance
        """
        self.capture = capture or ScreenCapture()
        self._baseline: Optional[np.ndarray] = None
        self._last_check_time = 0
        self._region = None

    def set_region(self, region: Tuple[int, int, int, int]) -> None:
        """Set detection region.

        Args:
            region: (left, top, width, height)
        """
        self._region = region
        logger.info(f"Detection region set: {region}")

    def _compute_hash(self, img: np.ndarray) -> str:
        """Compute image hash.

        Args:
            img: Image array

        Returns:
            MD5 hash string
        """
        # Resize for consistent hashing
        resized = cv2.resize(img, (100, 50))
        return hashlib.md5(resized.tobytes()).hexdigest()

    def _image_diff_ratio(self, img1: np.ndarray, img2: np.ndarray) -> float:
        """Calculate difference ratio between two images.

        Args:
            img1: First image
            img2: Second image

        Returns:
            Difference ratio (0-1)
        """
        if img1.shape != img2.shape:
            img2 = cv2.resize(img2, (img1.shape[1], img1.shape[0]))

        # Convert to grayscale
        gray1 = cv2.cvtColor(img1, cv2.COLOR_BGR2GRAY)
        gray2 = cv2.cvtColor(img2, cv2.COLOR_BGR2GRAY)

        # Calculate difference
        diff = cv2.absdiff(gray1, gray2)
        _, mask = cv2.threshold(diff, 25, 255, cv2.THRESH_BINARY)

        # Calculate ratio
        diff_ratio = np.sum(mask) / (mask.shape[0] * mask.shape[1] * 255)
        return diff_ratio

    def initialize(self) -> bool:
        """Initialize baseline for comparison.

        Returns:
            True if successful
        """
        try:
            # Capture baseline
            pil_img = self.capture.capture(self._region)
            self._baseline = np.array(pil_img)

            logger.info("Baseline captured for message detection")
            return True

        except Exception as e:
            logger.error(f"Failed to initialize detector: {e}")
            return False

    def detect_new_message(self, threshold: float = 0.01) -> bool:
        """Detect if there is a new message.

        Args:
            threshold: Difference threshold (0-1)

        Returns:
            True if new message detected
        """
        try:
            current_time = time.time()

            # Too soon since last check
            if current_time - self._last_check_time < config.check_interval:
                return False

            # Capture current screen
            pil_img = self.capture.capture(self._region)
            current = np.array(pil_img)

            # Compare with baseline
            if self._baseline is None:
                self.initialize()
                return False

            diff_ratio = self._image_diff_ratio(self._baseline, current)

            # Update baseline periodically
            if diff_ratio > threshold:
                self._last_check_time = current_time
                # Update baseline to current after a small delay
                time.sleep(0.5)
                self._baseline = np.array(self.capture.capture(self._region))
                logger.debug(f"New message detected (diff: {diff_ratio:.3f})")
                return True

            # Update baseline for next comparison
            self._baseline = current
            self._last_check_time = current_time

            return False

        except Exception as e:
            logger.error(f"Message detection error: {e}")
            return False

    def close(self) -> None:
        """Close resources."""
        self.capture.close()


# Global detector
detector = MessageDetector()