"""Configuration loader for WeChat Auto Reply Bot."""
import os
from pathlib import Path
from typing import Any, Dict

import yaml


class Config:
    """Configuration manager that loads from YAML file."""

    def __init__(self, config_path: str = None):
        """Load configuration from YAML file.

        Args:
            config_path: Path to config.yaml. If None, uses default location.
        """
        if config_path is None:
            base_dir = Path(__file__).parent.parent.parent
            config_path = base_dir / "config.yaml"

        self.config_path = Path(config_path)
        self._data: Dict[str, Any] = {}
        self._load()

    def _load(self) -> None:
        """Load configuration from file."""
        if not self.config_path.exists():
            raise FileNotFoundError(f"Config file not found: {self.config_path}")

        with open(self.config_path, "r", encoding="utf-8") as f:
            self._data = yaml.safe_load(f)

    def reload(self) -> None:
        """Reload configuration from file."""
        self._load()

    def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value by dot-notation key.

        Args:
            key: Dot-separated key path, e.g., "api.key"
            default: Default value if key not found

        Returns:
            Configuration value

        Examples:
            config.get("api.key")
            config.get("safety.max_daily", 200)
        """
        keys = key.split(".")
        value = self._data

        for k in keys:
            if isinstance(value, dict):
                value = value.get(k)
                if value is None:
                    return default
            else:
                return default

        return value

    @property
    def api_key(self) -> str:
        """Get API key."""
        return self.get("api.key", "")

    @property
    def model(self) -> str:
        """Get model name."""
        return self.get("api.model", "deepseek-ai/DeepSeek-V3")

    @property
    def base_url(self) -> str:
        """Get API base URL."""
        return self.get("api.base_url", "https://api.siliconflow.cn/v1")

    @property
    def temperature(self) -> float:
        """Get temperature parameter."""
        return self.get("api.temperature", 0.7)

    @property
    def max_tokens(self) -> int:
        """Get max tokens parameter."""
        return self.get("api.max_tokens", 500)

    @property
    def check_interval(self) -> int:
        """Get message check interval in seconds."""
        return self.get("interval.check", 3)

    @property
    def reply_min(self) -> int:
        """Get minimum reply interval in seconds."""
        return self.get("interval.reply_min", 2)

    @property
    def reply_max(self) -> int:
        """Get maximum reply interval in seconds."""
        return self.get("interval.reply_max", 5)

    @property
    def max_daily(self) -> int:
        """Get maximum daily reply count."""
        return self.get("safety.max_daily", 200)

    @property
    def night_mode_start(self) -> int:
        """Get night mode start hour."""
        return self.get("safety.night_mode_start", 23)

    @property
    def night_mode_end(self) -> int:
        """Get night mode end hour."""
        return self.get("safety.night_mode_end", 8)

    @property
    def keywords_enabled(self) -> bool:
        """Check if keyword reply is enabled."""
        return self.get("keywords.enabled", True)

    @property
    def keywords_replies(self) -> Dict[str, str]:
        """Get keyword to reply mapping."""
        return self.get("keywords.replies", {})

    @property
    def ai_fallback(self) -> bool:
        """Check if AI fallback is enabled for unmatched keywords."""
        return self.get("keywords.ai_fallback", True)

    @property
    def system_prompt(self) -> str:
        """Get AI system prompt."""
        return self.get("ai.system_prompt", "")

    @property
    def context_window(self) -> int:
        """Get conversation context window size."""
        return self.get("ai.context_window", 5)

    @property
    def wechat_title(self) -> str:
        """Get WeChat window title keyword."""
        return self.get("wechat.title_keyword", "微信")


# Global config instance
config = Config()