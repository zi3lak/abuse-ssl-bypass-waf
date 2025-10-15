"""Entry point for running the dashboard with ``python -m dashboard``."""

from .app import create_app
from .config import settings


def main() -> None:
    app = create_app()
    app.run(host=settings.host, port=settings.port, debug=settings.debug)


if __name__ == "__main__":  # pragma: no cover - manual execution helper
    main()
