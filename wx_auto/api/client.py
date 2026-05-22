"""SiliconFlow API client for AI chatbot."""
import time
from typing import Any, Dict, List, Optional

import requests

from wx_auto.utils.config import config
from wx_auto.utils.logger import logger


class SiliconFlowClient:
    """Client for SiliconFlow API."""

    def __init__(
        self,
        api_key: str = None,
        model: str = None,
        base_url: str = None,
    ):
        """Initialize SiliconFlow client.

        Args:
            api_key: API key. If None, uses config.
            model: Model name. If None, uses config.
            base_url: Base URL. If None, uses config.
        """
        self.api_key = api_key or config.api_key
        self.model = model or config.model
        self.base_url = base_url or config.base_url
        self.temperature = config.temperature
        self.max_tokens = config.max_tokens

        self._session = requests.Session()
        self._session.headers.update({
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        })

    def chat(
        self,
        messages: List[Dict[str, str]],
        temperature: float = None,
        max_tokens: int = None,
    ) -> str:
        """Send chat completions request.

        Args:
            messages: List of message dicts with "role" and "content"
            temperature: Sampling temperature. If None, uses default.
            max_tokens: Max tokens to generate. If None, uses default.

        Returns:
            AI response text

        Raises:
            requests.HTTPError: If API request fails
        """
        url = f"{self.base_url}/chat/completions"
        payload = {
            "model": self.model,
            "messages": messages,
            "temperature": temperature or self.temperature,
            "max_tokens": max_tokens or self.max_tokens,
        }

        try:
            response = self._session.post(url, json=payload, timeout=30)
            response.raise_for_status()
            result = response.json()

            return result["choices"][0]["message"]["content"]

        except requests.RequestException as e:
            logger.error(f"API request failed: {e}")
            raise

    def chat_with_context(
        self,
        user_message: str,
        system_prompt: str = None,
        history: List[Dict[str, str]] = None,
    ) -> str:
        """Chat with conversation context.

        Args:
            user_message: Current user message
            system_prompt: System prompt. If None, uses config.
            history: Conversation history

        Returns:
            AI response text
        """
        messages = []

        # System prompt
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        elif config.system_prompt:
            messages.append({"role": "system", "content": config.system_prompt})

        # History
        if history:
            context = history[-config.context_window:]
            messages.extend(context)

        # Current message
        messages.append({"role": "user", "content": user_message})

        # Track conversation
        if not hasattr(self, "_conversation_history"):
            self._conversation_history = []
        self._conversation_history.append({"role": "user", "content": user_message})

        # Call API
        response = self.chat(messages)

        # Save to history
        self._conversation_history.append({"role": "assistant", "content": response})

        return response

    def clear_history(self) -> None:
        """Clear conversation history."""
        if hasattr(self, "_conversation_history"):
            self._conversation_history.clear()


# Global client instance
client = SiliconFlowClient()