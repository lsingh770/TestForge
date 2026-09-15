from __future__ import annotations

import os
from dataclasses import dataclass


@dataclass(frozen=True)
class AppConfig:
    environment: str = "dev"
    base_url: str = "http://localhost:8001"
    auth_token: str | None = None
    api_key: str | None = None

    @classmethod
    def from_env(cls) -> "AppConfig":
        env = os.getenv("TESTFORGE_ENV", "dev").lower()
        base_url = os.getenv("TESTFORGE_BASE_URL", {
            "dev": "http://localhost:8001",
            "qa": "https://qa.example.com",
            "staging": "https://staging.example.com",
            "prod": "https://api.example.com",
        }.get(env, "http://localhost:8001"))
        return cls(
            environment=env,
            base_url=base_url,
            auth_token=os.getenv("TESTFORGE_AUTH_TOKEN"),
            api_key=os.getenv("TESTFORGE_API_KEY"),
        )


def get_config() -> AppConfig:
    return AppConfig.from_env()
