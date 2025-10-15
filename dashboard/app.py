"""Flask application powering the AI server dashboard."""

from __future__ import annotations

import logging
from datetime import datetime
from typing import Dict

from flask import Flask, jsonify, render_template, request

from .ai_client import session
from .config import settings
from .metrics import collector

LOGGER = logging.getLogger(__name__)


def create_app() -> Flask:
    app = Flask(__name__, static_folder="static", template_folder="templates")

    @app.route("/")
    def index() -> str:
        return render_template(
            "dashboard.html",
            refresh_seconds=settings.metrics_refresh_seconds,
            currency=settings.currency,
            prompt_cost_per_1k=settings.prompt_cost_per_1k,
            completion_cost_per_1k=settings.completion_cost_per_1k,
        )

    @app.route("/api/metrics")
    def metrics() -> Dict[str, object]:
        data = collector.collect()
        data["readable_timestamp"] = datetime.fromtimestamp(data["timestamp"]).isoformat()
        return jsonify(data)

    @app.route("/api/chat", methods=["GET", "POST"])
    def chat() -> Dict[str, object]:
        if request.method == "GET":
            return jsonify(
                {
                    "messages": session.messages,
                    "usage": session.usage,
                    "cost": _calculate_cost(session.usage),
                }
            )

        payload = request.get_json(force=True)
        message = payload.get("message", "").strip()
        if not message:
            return jsonify({"error": "Brak treści wiadomości."}), 400

        result = session.send(message)
        usage = session.usage
        result.update(
            {
                "total_usage": usage,
                "cost": _calculate_cost(result["usage"]),
                "total_cost": _calculate_cost(usage),
            }
        )
        return jsonify(result)

    @app.route("/api/chat/reset", methods=["POST"])
    def reset_chat() -> Dict[str, str]:
        session.reset()
        return jsonify({"status": "reset"})

    return app


def _calculate_cost(usage: Dict[str, int]) -> Dict[str, float]:
    prompt_tokens = usage.get("prompt_tokens", 0)
    completion_tokens = usage.get("completion_tokens", 0)
    prompt_cost = (prompt_tokens / 1000.0) * settings.prompt_cost_per_1k
    completion_cost = (completion_tokens / 1000.0) * settings.completion_cost_per_1k
    total_cost = prompt_cost + completion_cost
    return {
        "currency": settings.currency,
        "prompt": round(prompt_cost, 6),
        "completion": round(completion_cost, 6),
        "total": round(total_cost, 6),
    }


if __name__ == "__main__":  # pragma: no cover - manual execution helper
    logging.basicConfig(level=logging.INFO)
    create_app().run(host=settings.host, port=settings.port, debug=settings.debug)
