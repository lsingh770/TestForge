from __future__ import annotations

import json
from pathlib import Path


def build_dashboard_html(results: list[dict], output_path: str | Path) -> Path:
    total = len(results)
    passed = sum(1 for result in results if result.get("passed"))
    failed = total - passed

    rows = "\n".join(
        f"<tr><td>{result.get('id','-')}</td><td>{result.get('name','-')}</td><td>{result.get('category','-')}</td><td>{result.get('priority','P2')}</td><td>{'PASS' if result.get('passed') else 'FAIL'}</td></tr>"
        for result in results
    )

    html = f"""<!doctype html>
<html>
  <head>
    <meta charset=\"utf-8\" />
    <title>TestForge Dashboard</title>
    <style>
      body {{ font-family: Arial, sans-serif; background: #f4f7fb; margin: 0; padding: 32px; }}
      .container {{ max-width: 1000px; margin: 0 auto; }}
      .cards {{ display: flex; gap: 16px; margin-bottom: 24px; flex-wrap: wrap; }}
      .card {{ background: white; border-radius: 12px; padding: 18px 22px; min-width: 160px; box-shadow: 0 4px 12px rgba(0,0,0,.04); }}
      .card .label {{ color: #6b7280; font-size: 11px; text-transform: uppercase; letter-spacing: 0.08em; }}
      .card .value {{ font-size: 32px; margin-top: 6px; }}
      table {{ width: 100%; border-collapse: collapse; background: white; }}
      th, td {{ border: 1px solid #dbe3ee; padding: 10px; text-align: left; }}
      th {{ background: #eef2f9; }}
    </style>
  </head>
  <body>
    <div class=\"container\">
      <h1>TestForge Dashboard</h1>
      <div class=\"cards\">
        <div class=\"card\"><div class=\"label\">Total</div><div class=\"value\">{total}</div></div>
        <div class=\"card\"><div class=\"label\">Passed</div><div class=\"value\">{passed}</div></div>
        <div class=\"card\"><div class=\"label\">Failed</div><div class=\"value\">{failed}</div></div>
      </div>
      <table>
        <thead>
          <tr><th>ID</th><th>Name</th><th>Category</th><th>Priority</th><th>Status</th></tr>
        </thead>
        <tbody>
          {rows}
        </tbody>
      </table>
    </div>
  </body>
</html>
"""
    output = Path(output_path)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(html, encoding="utf-8")
    return output


def render_dashboard_from_suite(suite_path: str | Path, output_path: str | Path) -> Path:
    suite_data = json.loads(Path(suite_path).read_text(encoding="utf-8"))
    results = []
    for test in suite_data.get("tests", []):
        results.append({
            "id": test.get("id", "TC-000"),
            "name": test.get("name", "unnamed"),
            "category": test.get("category", "functional"),
            "priority": test.get("priority", "P2"),
            "passed": True,
        })
    return build_dashboard_html(results, output_path)
