from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class ApiSpec:
    name: str
    method: str
    url: str
    headers: dict[str, str] = field(default_factory=dict)
    params: dict[str, Any] = field(default_factory=dict)
    body: Any = None
    auth: dict[str, Any] = field(default_factory=dict)
    expected_status: int = 200
    response_schema: dict[str, Any] = field(default_factory=dict)
    description: str = ""
