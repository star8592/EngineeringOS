from __future__ import annotations

import os

from jev_http_provider import JevCompatibleHTTPProvider


class LayaLocalProvider(JevCompatibleHTTPProvider):
    def __init__(
        self,
        *,
        base_url: str | None = None,
        model: str | None = None,
        api_key: str | None = None,
        timeout_seconds: float = 10.0,
    ) -> None:
        super().__init__(
            name="laya-local",
            base_url=(
                base_url
                or os.environ.get(
                    "ENGINEERINGOS_LAYA_BASE_URL"
                )
                or "http://127.0.0.1:8017"
            ),
            model=(
                model
                or os.environ.get(
                    "ENGINEERINGOS_LAYA_MODEL"
                )
                or "typed-decisions"
            ),
            api_key=(
                api_key
                or os.environ.get(
                    "ENGINEERINGOS_LAYA_API_KEY"
                )
            ),
            timeout_seconds=timeout_seconds,
            health_path="/health",
        )
