from __future__ import annotations

import os

from jev_http_provider import JevCompatibleHTTPProvider


class DecisProvider(JevCompatibleHTTPProvider):
    def __init__(
        self,
        *,
        base_url: str | None = None,
        model: str | None = None,
        api_key: str | None = None,
        timeout_seconds: float = 30.0,
        name: str = "decis",
    ) -> None:
        super().__init__(
            name=name,
            base_url=(
                base_url
                or os.environ.get(
                    "ENGINEERINGOS_DECIS_BASE_URL"
                )
                or "http://127.0.0.1:8018"
            ),
            model=(
                model
                or os.environ.get(
                    "ENGINEERINGOS_DECIS_MODEL"
                )
                or "jev-latest"
            ),
            api_key=(
                api_key
                or os.environ.get(
                    "ENGINEERINGOS_DECIS_API_KEY"
                )
                or "local"
            ),
            timeout_seconds=timeout_seconds,
            health_path="/healthz",
            readiness_path="/readyz",
        )
