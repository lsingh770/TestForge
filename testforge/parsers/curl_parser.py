from __future__ import annotations

import json
import shlex
from typing import Any

from testforge.models import ApiSpec


def _coerce_json(value: str) -> Any:
    try:
        return json.loads(value)
    except json.JSONDecodeError:
        return value


def parse_curl(curl_command: str) -> ApiSpec:
    tokens = shlex.split(curl_command)
    if not tokens:
        raise ValueError("Empty cURL command provided")

    method = "GET"
    headers: dict[str, str] = {}
    body: Any = None
    url = ""
    index = 0

    while index < len(tokens):
        token = tokens[index]

        if token in {"-X", "--request"} and index + 1 < len(tokens):
            method = tokens[index + 1].upper()
            index += 2
            continue

        if token in {"-H", "--header"} and index + 1 < len(tokens):
            header = tokens[index + 1]
            if ":" in header:
                key, value = header.split(":", 1)
                headers[key.strip()] = value.strip()
            index += 2
            continue

        if token in {"-d", "--data", "--data-raw", "--data-binary"} and index + 1 < len(tokens):
            body = _coerce_json(tokens[index + 1])
            index += 2
            continue

        if token in {"--url"} and index + 1 < len(tokens):
            url = tokens[index + 1]
            index += 2
            continue

        if token.startswith("http://") or token.startswith("https://"):
            url = token
            index += 1
            continue

        if token == "--location":
            index += 1
            continue

        index += 1

    if not url:
        raise ValueError("No URL found in cURL command")

    if body is not None and method.upper() == "GET":
        method = "POST"

    if method.upper() == "POST" and body is None and any("Content-Type" in key for key in headers):
        body = {}

    return ApiSpec(
        name="Parsed cURL request",
        method=method.upper(),
        url=url,
        headers=headers,
        params={},
        body=body,
        auth={},
        expected_status=200,
        description="Generated from cURL input",
    )
