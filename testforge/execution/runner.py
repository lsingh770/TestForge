from __future__ import annotations

import json
import time
from html import escape
from pathlib import Path
from typing import Any

import requests


def execute_generated_tests(tests: list[dict[str, Any]], base_url: str | None = None) -> list[dict[str, Any]]:
    return list(stream_generated_tests(tests, base_url=base_url))


def stream_generated_tests(tests: list[dict[str, Any]], base_url: str | None = None):
    for test in tests:
        yield _execute_generated_test(test, base_url=base_url)


def _execute_generated_test(test: dict[str, Any], base_url: str | None = None) -> dict[str, Any]:
    method = str(test.get("method", "GET")).upper()
    request_url = str(test.get("url") or "").strip()
    if request_url.startswith(("http://", "https://")):
        target_url = request_url
    elif base_url and request_url:
        target_url = base_url.rstrip("/") + "/" + request_url.lstrip("/")
    elif base_url:
        target_url = base_url
    else:
        raise ValueError(f"No target URL provided for test {test.get('id', 'TC-000')}")

    payload = test.get("body")
    headers = test.get("headers") or {}
    started_at = time.perf_counter()
    try:
        response = requests.request(method, target_url, json=payload if payload is not None else None, headers=headers, timeout=10)
        passed = all(_evaluate_assertion(response, assertion) for assertion in test.get("assertions", []))
    except Exception as exc:  # pragma: no cover - runtime guard
        response = None
        passed = False
        exc_text = str(exc)
    else:
        exc_text = ""

    return {
        "id": test.get("id", "TC-000"),
        "name": test.get("name", "unnamed"),
        "category": test.get("category", "functional"),
        "priority": test.get("priority", "P2"),
        "metadata": test.get("metadata", {}),
        "passed": passed,
        "status_code": getattr(response, "status_code", None) if response else None,
        "response_text": getattr(response, "text", "") if response else "",
        "error": exc_text,
        "elapsed_ms": round((time.perf_counter() - started_at) * 1000, 2),
        "request": {
            "method": method,
            "url": target_url,
            "headers": headers,
            "body": payload,
        },
        "expected": {
            "assertions": test.get("assertions", []),
            "status_code": _extract_expected_status(test.get("assertions", [])),
        },
        "summary": "Passed" if passed else "Failed",
    }


def _extract_expected_status(assertions: list[str]) -> int | None:
    for assertion in assertions:
        if assertion.startswith("assert response.status_code"):
            expected = assertion.split("==")[-1].strip()
            try:
                return int(expected)
            except ValueError:
                return None
    return None


def _evaluate_assertion(response: requests.Response | None, assertion: str) -> bool:
    if response is None:
        return False
    if assertion.startswith("assert response.status_code"):
        expected = assertion.split("==")[-1].strip()
        try:
            return response.status_code == int(expected)
        except ValueError:
            return response.status_code == int(expected.replace(" ", ""))
    if assertion.startswith("assert response is not None"):
        return True
    if assertion.startswith("assert request.method"):
        return True
    if assertion.startswith("assert response.json contains keys"):
        try:
            payload = response.json()
            expected_keys = [key.strip().strip("'") for key in assertion.split("keys", 1)[1].strip(" []").split(",")]
            if isinstance(payload, list):
                return all(isinstance(item, dict) and all(key in item for key in expected_keys) for item in payload)
            return isinstance(payload, dict) and all(key in payload for key in expected_keys)
        except (ValueError, TypeError):
            return False
    return True


def generate_html_report(results: list[dict[str, Any]], output_path: str | Path) -> Path:
    path = Path(output_path)
    detail_sections = []
    for result in results:
        status = "PASS" if result["passed"] else "FAIL"
        request_payload = json.dumps(result.get("request", {}), indent=2, default=str)
        response_payload = json.dumps(
            {
                "status_code": result.get("status_code"),
                "response_text": result.get("response_text", ""),
                "error": result.get("error", ""),
            },
            indent=2,
            default=str,
        )
        detail_sections.append(
            """
            <section class="result-card">
              <h2>{id} — {name}</h2>
              <p><strong>Category:</strong> {category} &nbsp; <strong>Priority:</strong> {priority} &nbsp; <strong>Status:</strong> <span class="{status_class}">{status}</span> &nbsp; <strong>HTTP:</strong> {status_code}</p>
              <div class="payload-grid">
                <div>
                  <h3>Request</h3>
                  <pre>{request}</pre>
                </div>
                <div>
                  <h3>Response</h3>
                  <pre>{response}</pre>
                </div>
              </div>
              <p><strong>Assertions:</strong> {assertions}</p>
              <p><strong>Error:</strong> {error}</p>
            </section>
            """.format(
                id=escape(str(result["id"])),
                name=escape(str(result["name"])),
                category=escape(str(result["category"])),
                priority=escape(str(result.get("priority", "P2"))),
                status=escape(status),
                status_class="pass" if result["passed"] else "fail",
                status_code=escape(str(result.get("status_code"))),
                request=escape(request_payload),
                response=escape(response_payload),
                assertions=escape(", ".join(result.get("expected", {}).get("assertions", []))),
                error=escape(str(result.get("error", ""))),
            )
        )

    passed_count = sum(1 for result in results if result["passed"])
    failed_count = len(results) - passed_count

    summary_cards = """
    <div class="cards">
      <div class="card"><strong>Total</strong><span>{total}</span></div>
      <div class="card success"><strong>Passed</strong><span>{passed}</span></div>
      <div class="card danger"><strong>Failed</strong><span>{failed}</span></div>
    </div>
    """.format(total=len(results), passed=passed_count, failed=failed_count)

    html = """<!doctype html>
    <html>
      <head><meta charset=\"utf-8\"><title>TestForge report</title>
      <style>
        body {{ font-family: Arial; padding: 24px; background: #f6f8fb; color: #1f2937; }}
        .dashboard {{ max-width: 1200px; margin: 0 auto; }}
        h1 {{ margin-bottom: 8px; }}
        .cards {{ display: flex; gap: 16px; margin: 24px 0; flex-wrap: wrap; }}
        .card {{ background: white; border-radius: 12px; padding: 20px; min-width: 140px; box-shadow: 0 4px 12px rgba(0,0,0,0.04); display: flex; flex-direction: column; }}
        .card strong {{ font-size: 12px; text-transform: uppercase; color: #6b7280; }}
        .card span {{ font-size: 28px; margin-top: 8px; }}
        .success {{ border-left: 6px solid #16a34a; }}
        .danger {{ border-left: 6px solid #dc2626; }}
        .result-card {{ background: white; border-radius: 12px; padding: 20px; margin-top: 20px; box-shadow: 0 4px 12px rgba(0,0,0,0.04); }}
        .payload-grid {{ display: grid; grid-template-columns: 1fr 1fr; gap: 20px; }}
        pre {{ background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 8px; padding: 12px; white-space: pre-wrap; word-break: break-word; }}
        .pass {{ color: green; font-weight: bold; }}
        .fail {{ color: red; font-weight: bold; }}
      </style>
      </head>
      <body>
      <div class="dashboard">
        <h1>TestForge API Report</h1>
        {summary_cards}
        {details}
      </div>
      </body>
    </html>""".format(summary_cards=summary_cards, details="\n".join(detail_sections))
    path.write_text(html, encoding="utf-8")
    return path
