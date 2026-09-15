from __future__ import annotations

import re
from typing import Any
from urllib.parse import urljoin


_SUPPORTED_METHODS = {"GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS", "HEAD"}
_DEFAULT_STATUS = {
    "GET": 200,
    "POST": 201,
    "PUT": 200,
    "PATCH": 200,
    "DELETE": 204,
}


def _parse_method_entry(value: Any) -> tuple[str, str, Any] | None:
    body = None
    if isinstance(value, dict):
        body = value.get("body")
        value = value.get("request")
    if not isinstance(value, str):
        return None
    match = re.match(r"^\s*([A-Za-z]+)\s+(.+?)\s*$", value)
    if not match:
        return None
    method, path = match.groups()
    method = method.upper()
    if method not in _SUPPORTED_METHODS or path.upper() == "N/A":
        return None
    return method, path, body


def expand_api_catalog(catalog: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Convert catalog records into executable endpoint request specifications.

    The catalog format describes a service and its method/path examples. Each
    supported method becomes an independent endpoint spec consumed by the
    existing generator and execution engine.
    """
    endpoints: list[dict[str, Any]] = []
    for service in catalog:
        if not isinstance(service, dict):
            continue
        base_url = str(service.get("baseUrl", "")).strip()
        if not base_url:
            raise ValueError(f"Missing baseUrl for catalog entry {service.get('name', 'unnamed')}")
        methods = service.get("methods", {})
        if not isinstance(methods, dict):
            continue

        for method_name, method_value in methods.items():
            parsed = _parse_method_entry(method_value)
            if parsed is None:
                continue
            method, path, body = parsed
            url = urljoin(base_url.rstrip("/") + "/", path.lstrip("/"))
            endpoint_name = f"{service.get('name', 'API')} {method_name}"
            endpoints.append({
                "name": endpoint_name,
                "description": service.get("description", ""),
                "method": method,
                "url": url,
                "headers": dict(service.get("headers", {})) if isinstance(service.get("headers"), dict) else {},
                "body": body if body is not None else service.get("body"),
                "auth": service.get("auth", "None"),
                "expected_status": _DEFAULT_STATUS.get(method, 200),
                "source_catalog_id": service.get("id"),
                "source_service": service.get("name"),
                "resource": service.get("resource"),
            })
    return endpoints
