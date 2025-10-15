"""Configuration helpers for the AI server dashboard."""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from typing import Optional


@dataclass
class Settings:
    """Runtime configuration loaded from environment variables."""

    host: str = field(default_factory=lambda: os.getenv("DASHBOARD_HOST", "0.0.0.0"))
    port: int = field(default_factory=lambda: int(os.getenv("DASHBOARD_PORT", "8000")))
    debug: bool = field(default_factory=lambda: os.getenv("DASHBOARD_DEBUG", "false").lower() in {"1", "true", "yes"})
    metrics_refresh_seconds: float = field(
        default_factory=lambda: float(os.getenv("DASHBOARD_METRICS_REFRESH_SECONDS", "5"))
    )
    ai_endpoint: Optional[str] = field(default_factory=lambda: os.getenv("AI_SERVER_ENDPOINT"))
    ai_api_key: Optional[str] = field(default_factory=lambda: os.getenv("AI_SERVER_API_KEY"))
    ai_model: str = field(default_factory=lambda: os.getenv("AI_SERVER_MODEL", "gpt-4o-mini"))
    request_timeout: float = field(default_factory=lambda: float(os.getenv("AI_SERVER_TIMEOUT", "30")))
    prompt_cost_per_1k: float = field(default_factory=lambda: float(os.getenv("TOKEN_COST_PROMPT", "0.0")))
    completion_cost_per_1k: float = field(default_factory=lambda: float(os.getenv("TOKEN_COST_COMPLETION", "0.0")))
    currency: str = field(default_factory=lambda: os.getenv("TOKEN_COST_CURRENCY", "USD"))


settings = Settings()
