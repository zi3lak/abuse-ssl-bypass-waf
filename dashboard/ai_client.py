"""Utility classes for interacting with the upstream AI server."""

from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple

import requests

from .config import settings

LOGGER = logging.getLogger(__name__)


@dataclass
class AIMessage:
    """Represents a single chat message."""

    role: str
    content: str


class BaseAIBackend:
    """Abstract backend interface."""

    def send(self, messages: List[AIMessage]) -> Tuple[str, Dict[str, int]]:
        raise NotImplementedError


class EchoBackend(BaseAIBackend):
    """Fallback backend used when no remote AI server is configured."""

    def send(self, messages: List[AIMessage]) -> Tuple[str, Dict[str, int]]:
        user_message = messages[-1].content if messages else ""
        reply = (
            "(Fallback response) Zostałem uruchomiony w trybie demonstracyjnym. "
            "Otrzymałem następującą wiadomość: "
            f"\"{user_message}\""
        )
        usage = {
            "prompt_tokens": estimate_tokens(" ".join(m.content for m in messages)),
            "completion_tokens": estimate_tokens(reply),
        }
        return reply, usage


class WebhookBackend(BaseAIBackend):
    """HTTP backend sending the full conversation to an upstream service."""

    def __init__(self, endpoint: str, api_key: Optional[str], model: str, timeout: float) -> None:
        self._endpoint = endpoint
        self._api_key = api_key
        self._model = model
        self._timeout = timeout

    def send(self, messages: List[AIMessage]) -> Tuple[str, Dict[str, int]]:
        payload = {
            "model": self._model,
            "messages": [message.__dict__ for message in messages],
        }
        headers = {"Content-Type": "application/json"}
        if self._api_key:
            headers["Authorization"] = f"Bearer {self._api_key}"

        response = requests.post(
            self._endpoint,
            json=payload,
            headers=headers,
            timeout=self._timeout,
        )
        response.raise_for_status()
        data = response.json()
        reply = data.get("response") or data.get("message") or data.get("content")
        if not isinstance(reply, str):
            raise ValueError("Unexpected response payload - missing 'response' key")
        usage = data.get("usage", {})
        usage.setdefault("prompt_tokens", estimate_tokens(" ".join(m.content for m in messages)))
        usage.setdefault("completion_tokens", estimate_tokens(reply))
        return reply, usage


def estimate_tokens(text: str) -> int:
    """Very small heuristic for estimating token counts without external dependencies."""

    normalized = text.strip()
    if not normalized:
        return 0
    return max(1, len(normalized.split()))


class ChatSession:
    """Maintains chat history and token usage totals."""

    def __init__(self, backend: Optional[BaseAIBackend] = None) -> None:
        if backend is None:
            backend = (
                WebhookBackend(
                    settings.ai_endpoint,
                    settings.ai_api_key,
                    settings.ai_model,
                    settings.request_timeout,
                )
                if settings.ai_endpoint
                else EchoBackend()
            )
        self._backend = backend
        self._messages: List[AIMessage] = []
        self._usage = {"prompt_tokens": 0, "completion_tokens": 0}

    @property
    def usage(self) -> Dict[str, int]:
        return dict(self._usage)

    @property
    def messages(self) -> List[Dict[str, str]]:
        return [message.__dict__ for message in self._messages]

    def reset(self) -> None:
        self._messages.clear()
        self._usage = {"prompt_tokens": 0, "completion_tokens": 0}

    def send(self, content: str) -> Dict[str, object]:
        user_message = AIMessage(role="user", content=content)
        self._messages.append(user_message)
        try:
            reply, usage = self._backend.send(self._messages)
        except Exception as exc:  # pragma: no cover - defensive fallback
            LOGGER.exception("Chat backend failed: %s", exc)
            reply = (
                "Wystąpił problem z komunikacją z serwerem AI. "
                "Sprawdź konfigurację i spróbuj ponownie."
            )
            usage = {
                "prompt_tokens": estimate_tokens(content),
                "completion_tokens": estimate_tokens(reply),
            }
        assistant_message = AIMessage(role="assistant", content=reply)
        self._messages.append(assistant_message)

        self._usage["prompt_tokens"] += usage.get("prompt_tokens", 0)
        self._usage["completion_tokens"] += usage.get("completion_tokens", 0)

        return {
            "messages": [user_message.__dict__, assistant_message.__dict__],
            "usage": usage,
        }


session = ChatSession()
