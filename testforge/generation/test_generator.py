from __future__ import annotations

from typing import Any

from testforge.test_data import TestData


def _parse_body(value: Any) -> Any:
    if not isinstance(value, str):
        return value
    try:
        import json

        return json.loads(value)
    except json.JSONDecodeError:
        return value


def _base_assertions(method: str, status: int) -> list[str]:
    return [
        f"assert response.status_code == {status}",
        f"assert request.method == '{method}'",
    ]


def _metadata_for(test_id: str, category: str, priority: str) -> dict[str, Any]:
    return {
        "test_id": test_id,
        "category": category,
        "priority": priority,
        "severity": "P1" if priority == "P0" else "P2",
        "description": "Generated from API contract and input example",
        "source": "manual_input",
        "confidence": "HIGH",
        "ai_generated": True,
        "human_modified": False,
    }


def _case(
    number: int,
    name: str,
    category: str,
    method: str,
    url: str,
    headers: dict[str, Any],
    body: Any,
    priority: str,
    assertions: list[str],
) -> dict[str, Any]:
    test_id = f"TC-{number:03d}"
    return {
        "id": test_id,
        "name": name,
        "category": category,
        "method": method,
        "url": url,
        "headers": headers,
        "body": body,
        "assertions": assertions,
        "priority": priority,
        "metadata": _metadata_for(test_id, category, priority),
    }


def _invalid_body(body: Any) -> Any:
    if not isinstance(body, dict) or not body:
        return None
    invalid = dict(body)
    first_key = next(iter(invalid))
    invalid[first_key] = "" if isinstance(invalid[first_key], str) else "invalid-value"
    return invalid


def _boundary_body(body: Any) -> Any:
    if not isinstance(body, dict) or not body:
        return body
    boundary = dict(body)
    for key, value in boundary.items():
        if isinstance(value, int) and not isinstance(value, bool):
            boundary[key] = 0
            break
        if isinstance(value, float):
            boundary[key] = 0.0
            break
        if isinstance(value, str):
            boundary[key] = "x"
            break
    return boundary


def generate_tests(api_spec: dict[str, Any]) -> list[dict[str, Any]]:
    method = str(api_spec.get("method", "GET")).upper()
    url = str(api_spec.get("url", ""))
    headers = api_spec.get("headers", {}) or {}
    if "body" in api_spec and api_spec["body"] is not None:
        body = _parse_body(api_spec["body"])
    elif method in {"POST", "PUT", "PATCH"}:
        body = TestData.user()
    else:
        body = None
    status = int(api_spec.get("expected_status", 200))

    validation_status = int(api_spec.get("validation_status", 400))
    tests = [
        _case(1, "valid_request", "positive", method, url, headers, body, "P1", _base_assertions(method, status) + ["assert response is not None"]),
        _case(2, "missing_required_fields", "negative", method, url, headers, {} if isinstance(body, dict) else None, "P0", [f"assert response.status_code == {validation_status}", "assert response is not None"]),
        _case(3, "invalid_field_value", "negative", method, url, headers, _invalid_body(body), "P1", [f"assert response.status_code == {validation_status}", "assert response is not None"]),
        _case(4, "boundary_values", "boundary", method, url, headers, _boundary_body(body), "P2", _base_assertions(method, status)),
    ]

    if method in {"POST", "PUT", "PATCH"}:
        duplicate_status = int(api_spec.get("duplicate_status", status))
        tests.append(_case(5, "duplicate_or_replay_request", "idempotency", method, url, headers, body, "P2", [f"assert response.status_code == {duplicate_status}", "assert response is not None"]))

    if "{" in url and "}" in url:
        missing_path = url.replace("{", "missing-").replace("}", "")
        not_found_status = int(api_spec.get("not_found_status", 404))
        tests.append(_case(len(tests) + 1, "resource_not_found", "negative", method, missing_path, headers, body if method in {"POST", "PUT", "PATCH"} else None, "P1", [f"assert response.status_code == {not_found_status}", "assert response is not None"]))

    if api_spec.get("auth") or any(key.lower() == "authorization" for key in headers):
        unauthorized_status = int(api_spec.get("unauthorized_status", 401))
        unauth_headers = {key: value for key, value in headers.items() if key.lower() != "authorization"}
        tests.append(_case(len(tests) + 1, "unauthorized_request", "security", method, url, unauth_headers, body, "P0", [f"assert response.status_code == {unauthorized_status}", "assert response is not None"]))

    response_schema = api_spec.get("response_schema")
    if isinstance(response_schema, dict) and response_schema:
        tests.append(_case(len(tests) + 1, "response_contract", "contract", method, url, headers, body, "P1", _base_assertions(method, status) + [f"assert response.json contains keys {list(response_schema)}"]))

    return tests
