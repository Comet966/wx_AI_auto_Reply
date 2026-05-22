"""Responder with keyword matching and AI response."""
import random
import time
from typing import Dict, List, Optional, Tuple

from wx_auto.api.client import SiliconFlowClient
from wx_auto.core.controller import Controller
from wx_auto.core.screen import OCREngine, ScreenCapture
from wx_auto.utils.config import config
from wx_auto.utils.logger import logger


class Message:
    """Represents a WeChat message."""

    def __init__(
        self,
        sender: str,
        content: str,
        timestamp: str = "",
    ):
        self.sender = sender
        self.content = content
        self.timestamp = timestamp

    def __repr__(self) -> str:
        return f"Message({self.sender}: {self.content})"


class KeywordResponder:
    """Keyword-based responder."""

    def __init__(self, replies: Dict[str, str] = None):
        """Initialize keyword responder.

        Args:
            replies: Mapping of keywords to replies
        """
        self.replies = replies or config.keywords_replies

    def match(self, message: str) -> Optional[str]:
        """Match keyword and return reply.

        Args:
            message: Message content

        Returns:
            Reply if matched, None otherwise
        """
        for keyword, reply in self.replies.items():
            if keyword in message:
                logger.debug(f"Keyword matched: {keyword}")
                return reply

        return None


class Responder:
    """Main responder with keyword and AI support."""

    def __init__(self):
        """Initialize responder."""
        self.keyword_responder = KeywordResponder()
        self.ai_client = SiliconFlowClient()
        self.ctrl = Controller()
        self.ocr = OCREngine()
        self._reply_count = 0
        self._last_reply_time = 0
        self._conversation_history: List[Dict[str, str]] = []

    def _get_random_interval(self) -> float:
        """Get random reply interval.

        Returns:
            Random interval in seconds
        """
        return random.uniform(config.reply_min, config.reply_max)

    def _check_safety_limits(self) -> bool:
        """Check if safety limits are exceeded.

        Returns:
            True if can reply
        """
        from datetime import datetime

        now = datetime.now()
        hour = now.hour

        # Night mode check
        if config.night_mode_start <= 24 and config.night_mode_end >= 0:
            if config.night_mode_start > config.night_mode_end:
                # Night spans midnight (e.g., 23:00-08:00)
                if hour >= config.night_mode_start or hour < config.night_mode_end:
                    logger.info("Night mode active, skipping reply")
                    return False
            else:
                if config.night_mode_start <= hour < config.night_mode_end:
                    logger.info("Night mode active, skipping reply")
                    return False

        # Daily limit check
        if self._reply_count >= config.max_daily:
            logger.warning("Daily reply limit reached")
            return False

        return True

    def generate_reply(self, message: str) -> str:
        """Generate reply for message.

        Args:
            message: Input message

        Returns:
            Reply text
        """
        # Check keyword first
        if config.keywords_enabled:
            reply = self.keyword_responder.match(message)
            if reply:
                return reply

        # AI fallback
        if config.ai_fallback:
            try:
                return self.ai_client.chat_with_context(
                    message,
                    history=self._conversation_history,
                )
            except Exception as e:
                logger.error(f"AI reply failed: {e}")
                return "抱歉，我现在有点忙，请稍后再试。"

        return "好的，我会尽快回复您。"

    def send_reply(self, message: str) -> bool:
        """Send reply to WeChat.

        Args:
            message: Reply text to send
        """
        try:
            # Check safety
            if not self._check_safety_limits():
                return False

            # Random interval between messages
            interval = self._get_random_interval()
            elapsed = time.time() - self._last_reply_time
            if elapsed < interval:
                time.sleep(interval - elapsed)

            # Ensure WeChat is ready
            if not self.ctrl.ensure_wechat():
                return False

            # Type/reply
            # Note: Actual implementation depends on WeChat UI positions
            # This is a placeholder - you'll need to adjust coordinates
            self.ctrl.input.paste_text(message)
            time.sleep(0.3)
            self.ctrl.input.press("enter")

            # Update counters
            self._reply_count += 1
            self._last_reply_time = time.time()

            # Save to history
            self._conversation_history.append({
                "role": "user",
                "content": message,
            })
            self._conversation_history.append({
                "role": "assistant",
                "content": message,
            })

            # Trim history
            keep = config.context_window * 2
            if len(self._conversation_history) > keep:
                self._conversation_history = self._conversation_history[-keep:]

            logger.info(f"Reply sent: {message[:30]}...")
            return True

        except Exception as e:
            logger.error(f"Failed to send reply: {e}")
            return False

    def get_reply_count(self) -> int:
        """Get today's reply count."""
        return self._reply_count

    def reset_daily_count(self) -> None:
        """Reset daily reply count."""
        self._reply_count = 0

    def close(self) -> None:
        """Close resources."""
        self.ctrl.close()
        self.ocr = None


# Global responder
responder = Responder()