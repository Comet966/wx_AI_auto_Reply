"""Keyboard and mouse controller."""
import random
import time
from typing import Optional, Tuple

import pyautogui
import pygetwindow

from wx_auto.utils.config import config
from wx_auto.utils.logger import logger


class WindowController:
    """Window controller using pygetwindow."""

    def __init__(self, title_keyword: str = None):
        """Initialize window controller.

        Args:
            title_keyword: Window title keyword to find
        """
        self.title_keyword = title_keyword or config.wechat_title
        self._window = None

    def find_window(self, activate: bool = False) -> bool:
        """Find window by title keyword.

        Args:
            activate: Whether to activate the window

        Returns:
            True if window found
        """
        try:
            windows = pygetwindow.findWindowsWithTitle(self.title_keyword)
            if windows:
                self._window = windows[0]
                if activate:
                    self._window.activate()
                    # Wait for window to become active
                    time.sleep(0.3)
                logger.debug(f"Found window: {self._window.title}")
                return True
            logger.warning(f"Window not found: {self.title_keyword}")
            return False

        except Exception as e:
            logger.error(f"Failed to find window: {e}")
            return False

    def bring_to_front(self) -> bool:
        """Bring window to front.

        Returns:
            True if successful
        """
        if self._window is None:
            return self.find_window(activate=True)
        try:
            self._window.activate()
            time.sleep(0.3)
            return True
        except Exception as e:
            logger.error(f"Failed to bring window to front: {e}")
            return False

    def get_position(self) -> Optional[Tuple[int, int]]:
        """Get window position.

        Returns:
            (left, top) or None
        """
        if self._window is None:
            return None
        return (self._window.left, self._window.top)

    def get_size(self) -> Optional[Tuple[int, int]]:
        """Get window size.

        Returns:
            (width, height) or None
        """
        if self._window is None:
            return None
        return (self._window.width, self._window.height)

    def is_active(self) -> bool:
        """Check if window is active.

        Returns:
            True if window is active
        """
        if self._window is None:
            return False
        try:
            return self._window.isActive
        except Exception:
            return False


class InputController:
    """Input controller using pyautogui."""

    def __init__(self):
        """Initialize input controller."""
        # Disable fail-safe (allows running in background)
        pyautogui.FAILSAFE = False

        # Configure default timing
        self._min_delay = config.get("safety.input_delay_min", 0.05)
        self._max_delay = config.get("safety.input_delay_max", 0.15)

    def _random_delay(self) -> None:
        """Wait for random delay."""
        delay = random.uniform(self._min_delay, self._max_delay)
        time.sleep(delay)

    def click(self, x: int, y: int, button: str = "left") -> None:
        """Click at position.

        Args:
            x: X coordinate
            y: Y coordinate
            button: Mouse button
        """
        pyautogui.click(x, y, button=button)
        self._random_delay()
        logger.debug(f"Clicked at ({x}, {y})")

    def double_click(self, x: int, y: int, button: str = "left") -> None:
        """Double click at position.

        Args:
            x: X coordinate
            y: Y coordinate
            button: Mouse button
        """
        pyautogui.doubleClick(x, y, button=button)
        self._random_delay()
        logger.debug(f"Double clicked at ({x}, {y})")

    def right_click(self, x: int, y: int) -> None:
        """Right click at position.

        Args:
            x: X coordinate
            y: Y coordinate
        """
        pyautogui.rightClick(x, y)
        self._random_delay()
        logger.debug(f"Right clicked at ({x}, {y})")

    def type_text(self, text: str) -> None:
        """Type text.

        Args:
            text: Text to type
        """
        pyautogui.write(text)
        logger.debug(f"Typed text: {text[:30]}...")

    def press(self, key: str) -> None:
        """Press key.

        Args:
            key: Key name
        """
        pyautogui.press(key)
        self._random_delay()
        logger.debug(f"Pressed key: {key}")

    def hotkey(self, *keys: str) -> None:
        """Press hotkey combination.

        Args:
            keys: Keys to press together
        """
        pyautogui.hotkey(*keys)
        self._random_delay()
        logger.debug(f"Pressed hotkey: {'+'.join(keys)}")

    def paste_text(self, text: str) -> None:
        """Paste text via clipboard (more reliable for Chinese).

        Args:
            text: Text to paste
        """
        # Save current clipboard
        import pyperclip
        original = pyperclip.paste()

        try:
            # Set new text
            pyperclip.copy(text)
            time.sleep(0.1)

            # Paste
            pyautogui.hotkey("ctrl", "v")
            self._random_delay()
            logger.debug(f"Pasted text: {text[:30]}...")

        finally:
            # Restore clipboard
            pyperclip.copy(original)

    def move_and_click(self, dx: int, dy: int) -> None:
        """Move relative and click.

        Args:
            dx: Relative X movement
            dy: Relative Y movement
        """
        x, y = pyautogui.position()
        self.click(x + dx, y + dy)


class Controller:
    """Combined window and input controller."""

    def __init__(self):
        """Initialize controller."""
        self.window = WindowController()
        self.input = InputController()

    def ensure_wechat(self) -> bool:
        """Ensure WeChat window is ready.

        Returns:
            True if successful
        """
        if not self.window.find_window():
            logger.error("Cannot find WeChat window")
            return False

        self.window.bring_to_front()
        return True

    def close(self) -> None:
        """Close resources."""
        pass


# Global controller
controller = Controller()