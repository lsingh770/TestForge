from __future__ import annotations

import json
from pathlib import Path
from typing import Any


def parse_openapi_document(source: str | Path | dict[str, Any]) -> list[dict[str, Any]]:
    """Return a lightweight list of endpoint specs from an OpenAPI JSON document."""
    if isinstance(source, (str, Path)):
        raw = Path(source).read_text(encoding="utf-8")
        data = json.loads(raw)
    elif isinstance(source, dict):
        data = source
    else:
        raise TypeError("OpenAPI source must be a path, JSON string, or dict")

    paths = data.get("paths", {})
    endpoints: list[dict[str, Any]] = []

    for route, methods in paths.items():
        for method_name, spec in methods.items():
            if method_name.upper() not in {"GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS", "HEAD"}:
                continue
            endpoints.append({
                "path": route,
                "method": method_name.upper(),
                "summary": spec.get("summary", ""),
                "description": spec.get("description", ""),
                "operation_id": spec.get("operationId", ""),
                "parameters": spec.get("parameters", []),
                "requestBody": spec.get("requestBody", {}),
            })
    return endpoints
