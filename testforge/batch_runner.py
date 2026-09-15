from __future__ import annotations

import json
from html import escape
from pathlib import Path
from typing import Any

from testforge.execution.runner import execute_generated_tests, generate_html_report
from testforge.generation.test_generator import generate_tests


def _write_summary_report(batch_root: Path, api_entries: list[dict[str, Any]]) -> str:
    total_passed = sum(api["passed"] for api in api_entries)
    total_failed = sum(api["failed"] for api in api_entries)
    rows = "\n".join(
        "<tr><td>{name}</td><td>{passed}</td><td>{failed}</td><td><a href=\"{report}\">Open report</a></td></tr>".format(
            name=escape(str(api["api_name"])),
            passed=api["passed"],
            failed=api["failed"],
            report=escape(str(api["report_file"])),
        )
        for api in api_entries
    )
    html = """<!doctype html>
<html>
<head>
  <meta charset=\"utf-8\">
  <title>Batch Summary</title>
  <style>
    body {{ font-family: Arial, sans-serif; background: #f4f7fb; padding: 24px; }}
    .container {{ max-width: 1000px; margin: 0 auto; }}
    .card {{ background: white; border-radius: 12px; padding: 20px; box-shadow: 0 4px 12px rgba(0,0,0,0.04); }}
    table {{ width: 100%; border-collapse: collapse; margin-top: 20px; }}
    th, td {{ border: 1px solid #dfe7f3; padding: 12px; text-align: left; }}
    th {{ background: #eef3fb; }}
    .stats {{ display: flex; gap: 16px; margin: 18px 0; }}
    .stat {{ background: #fff; border-radius: 12px; padding: 16px 20px; min-width: 140px; box-shadow: 0 4px 12px rgba(0,0,0,0.04); }}
  </style>
</head>
<body>
  <div class=\"container\">
    <h1>Batch Summary</h1>
    <div class=\"stats\">
      <div class=\"stat\"><strong>APIs</strong><br>{api_count}</div>
      <div class=\"stat\"><strong>Passed</strong><br>{passed}</div>
      <div class=\"stat\"><strong>Failed</strong><br>{failed}</div>
    </div>
    <div class=\"card\">
      <table>
        <thead><tr><th>API</th><th>Passed</th><th>Failed</th><th>Report</th></tr></thead>
        <tbody>{rows}</tbody>
      </table>
    </div>
  </div>
</body>
</html>""".format(api_count=len(api_entries), passed=total_passed, failed=total_failed, rows=rows)
    summary_path = batch_root / "summary_report.html"
    summary_path.write_text(html, encoding="utf-8")
    return str(summary_path)


def process_batch(batch_dir: str | Path, base_url: str | None = None) -> dict[str, Any]:
    """Process every API folder under a batch directory as an independent suite.

    Each folder is expected to contain an api.json file with the API definition.
    The runner creates a generated_suite.json, executes it, and writes report output
    for each API in that folder.
    """
    batch_root = Path(batch_dir)
    if not batch_root.exists():
        raise FileNotFoundError(f"Batch directory not found: {batch_root}")

    api_entries: list[dict[str, Any]] = []
    for api_dir in sorted(batch_root.iterdir()):
        if not api_dir.is_dir():
            continue
        api_file = api_dir / "api.json"
        if not api_file.exists():
            continue

        api_spec = json.loads(api_file.read_text(encoding="utf-8"))
        tests = generate_tests(api_spec)
        suite_path = api_dir / "generated_suite.json"
        suite = {"api": api_spec, "tests": tests}
        suite_path.write_text(json.dumps(suite, indent=2), encoding="utf-8")

        results = execute_generated_tests(suite["tests"], base_url=base_url or api_spec.get("url"))
        report_path = api_dir / "report.html"
        generate_html_report(results, report_path)

        api_entries.append({
            "api_name": api_spec.get("name", api_dir.name),
            "api_dir": str(api_dir),
            "suite_file": str(suite_path),
            "report_file": str(report_path),
            "passed": sum(1 for item in results if item["passed"]),
            "failed": sum(1 for item in results if not item["passed"]),
        })

    summary_path = _write_summary_report(batch_root, api_entries)
    return {
        "batch_dir": str(batch_root),
        "summary_file": summary_path,
        "summary_html": (batch_root / "summary_report.html").read_text(encoding="utf-8"),
        "apis": api_entries,
    }
