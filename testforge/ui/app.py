from __future__ import annotations

import json
from pathlib import Path
from datetime import datetime, timezone
import re
import shutil

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse, HTMLResponse, RedirectResponse

from frontend.dashboard import build_dashboard_html
from testforge.batch_runner import process_batch
from testforge.config import get_config
from testforge.contracts.catalog_loader import expand_api_catalog
from testforge.execution.runner import execute_generated_tests, generate_html_report
from testforge.exporters.exporter import export_results
from testforge.generation.test_generator import generate_tests

app = FastAPI(title="TestForge UI", version="0.1.0")

SUITE_PATH = Path(__file__).resolve().parent.parent.parent / "sample_project" / "generated_suite.json"
REPORT_PATH = Path(__file__).resolve().parent.parent.parent / "sample_project" / "report.html"
DASHBOARD_PATH = Path(__file__).resolve().parent.parent.parent / "sample_project" / "dashboard.html"
EXPORT_DIR = Path(__file__).resolve().parent.parent.parent / "sample_project" / "exports"
BATCH_ROOT = Path(__file__).resolve().parent.parent.parent / "sample_project" / "batches"


def _load_suite() -> dict:
    if SUITE_PATH.exists():
        return json.loads(SUITE_PATH.read_text(encoding="utf-8"))
    return {"api": {}, "tests": []}


@app.get("/")
def index() -> RedirectResponse:
    return RedirectResponse(url="/ui")


@app.get("/ui", response_class=HTMLResponse)
def ui_dashboard() -> str:
    suite = _load_suite()
    tests = suite.get("tests", [])
    rows = "\n".join(
        f"<tr data-id=\"{test.get('id','-')}\"><td>{test.get('id','-')}</td><td>{test.get('name','-')}</td><td>{test.get('category','-')}</td><td>{test.get('priority','P2')}</td><td>{test.get('metadata', {}).get('confidence','LOW')}</td><td><button class=\"link-button\" data-id=\"{test.get('id','-')}\">View</button></td></tr>"
        for test in tests
    )
    config = get_config()
    return f"""<!doctype html>
<html>
<head>
  <meta charset=\"utf-8\" />
  <title>TestForge</title>
  <style>
    :root {{
      --bg: #f4f7fb;
      --panel: #ffffff;
      --line: #dfe7f3;
      --primary: #2563eb;
      --primary-soft: #dbeafe;
      --success: #16a34a;
      --danger: #dc2626;
      --muted: #64748b;
      --text: #111827;
    }}
    * {{ box-sizing: border-box; }}
    body {{ font-family: Inter, Arial, sans-serif; background: linear-gradient(180deg, #eef4ff 0%, var(--bg) 100%); margin: 0; color: var(--text); }}
    .container {{ max-width: 1200px; margin: 0 auto; padding: 32px 20px 60px; }}
    .topbar {{ display: flex; justify-content: space-between; align-items: center; margin-bottom: 24px; }}
    .brand {{ font-size: 28px; font-weight: 700; }}
    .pill {{ background: var(--primary-soft); color: var(--primary); padding: 8px 12px; border-radius: 999px; font-size: 12px; font-weight: 700; letter-spacing: 0.08em; text-transform: uppercase; }}
    .grid {{ display: grid; grid-template-columns: 420px 1fr; gap: 20px; }}
    .panel {{ background: var(--panel); border: 1px solid var(--line); border-radius: 18px; box-shadow: 0 8px 20px rgba(15, 23, 42, 0.04); padding: 22px; }}
    form {{ display: grid; gap: 14px; }}
    .row {{ display: grid; grid-template-columns: 1fr 1fr; gap: 12px; }}
    label {{ display: grid; gap: 6px; font-size: 13px; font-weight: 600; color: var(--muted); }}
    input, select, textarea, button {{ font: inherit; }}
    input, select, textarea {{ width: 100%; border: 1px solid var(--line); border-radius: 10px; padding: 10px 12px; background: white; color: var(--text); }}
    textarea {{ min-height: 120px; resize: vertical; }}
    button {{ border: none; cursor: pointer; border-radius: 10px; padding: 10px 14px; font-weight: 700; }}
    .primary {{ background: var(--primary); color: white; }}
    .secondary {{ background: #e2e8f0; color: var(--text); }}
    .actions {{ display: flex; gap: 10px; margin-top: 8px; }}
    .stats {{ display: grid; grid-template-columns: repeat(3, minmax(120px, 1fr)); gap: 12px; margin-bottom: 18px; }}
    .stat {{ background: white; border: 1px solid var(--line); border-radius: 14px; padding: 16px; }}
    .stat .label {{ color: var(--muted); font-size: 11px; letter-spacing: 0.08em; text-transform: uppercase; }}
    .stat .value {{ font-size: 30px; font-weight: 700; margin-top: 8px; }}
    table {{ width: 100%; border-collapse: collapse; margin-top: 8px; }}
    th, td {{ border: 1px solid var(--line); padding: 10px 12px; text-align: left; font-size: 14px; }}
    th {{ background: #eef3fb; }}
    .status {{ display: inline-block; padding: 4px 8px; border-radius: 999px; font-weight: 700; font-size: 12px; }}
    .pass {{ background: rgba(22, 163, 74, 0.12); color: var(--success); }}
    .fail {{ background: rgba(220, 38, 38, 0.10); color: var(--danger); }}
    .link-button {{ background: transparent; color: var(--primary); padding: 0; font-weight: 700; }}
    #toast {{ position: fixed; right: 20px; bottom: 20px; background: #0f172a; color: white; padding: 12px 16px; border-radius: 10px; display: none; }}
    @media (max-width: 900px) {{
      .grid {{ grid-template-columns: 1fr; }}
      .row {{ grid-template-columns: 1fr; }}
    }}
  </style>
</head>
<body>
  <div class=\"container\">
    <div class=\"topbar\">
      <div class=\"brand\">TestForge</div>
      <div class=\"pill\">{config.environment}</div>
    </div>

    <div class=\"grid\">
      <div class=\"panel\">
        <h2>Generate API test suite</h2>
        <form id=\"apiForm\">
          <div class=\"row\">
            <label>Environment
              <select id=\"environment\">
                <option value=\"dev\">Dev</option>
                <option value=\"qa\">QA</option>
                <option value=\"staging\">Staging</option>
                <option value=\"prod\">Prod</option>
              </select>
            </label>
            <label>Method
              <select id=\"method\">
                <option value=\"GET\">GET</option>
                <option value=\"POST\" selected>POST</option>
                <option value=\"PUT\">PUT</option>
                <option value=\"DELETE\">DELETE</option>
              </select>
            </label>
          </div>

          <label>Base URL
            <input id=\"baseUrl\" type=\"text\" value=\"{config.base_url}\" />
          </label>

          <label>Endpoint URL
            <input id=\"url\" type=\"text\" value=\"/users\" />
          </label>

          <label>Headers (JSON)
            <textarea id=\"headers\">{{\"Content-Type\": \"application/json\"}}</textarea>
          </label>

          <label>Request Body (JSON)
            <textarea id=\"body\">{{\"name\": \"Test User\", \"email\": \"test.user@example.com\"}}</textarea>
          </label>

          <label>Expected Status
            <input id=\"expectedStatus\" type=\"number\" value=\"200\" />
          </label>

          <div class=\"actions\">
            <button type=\"button\" class=\"primary\" id=\"generateBtn\">Generate Suite</button>
            <button type=\"button\" class=\"secondary\" id=\"runBtn\">Run Suite</button>
          </div>
        </form>
      </div>

      <div class=\"panel\">
        <h2>Results</h2>
        <div class=\"stats\">
          <div class=\"stat\"><div class=\"label\">Total</div><div class=\"value\" id=\"totalCount\">{len(tests)}</div></div>
          <div class=\"stat\"><div class=\"label\">Passed</div><div class=\"value\" id=\"passedCount\">0</div></div>
          <div class=\"stat\"><div class=\"label\">Failed</div><div class=\"value\" id=\"failedCount\">0</div></div>
        </div>

        <table>
          <thead>
            <tr><th>ID</th><th>Name</th><th>Category</th><th>Priority</th><th>Confidence</th><th>Result</th><th>Open</th></tr>
          </thead>
          <tbody id=\"resultsTable\">{rows}</tbody>
        </table>
        <div id=\"toast\"></div>
      </div>
    </div>
  </div>

  <script>
    const suiteState = {{"api": {{}}, "tests": []}};
    const endpointMap = {{
      "generateBtn": "/api/generate",
      "runBtn": "/api/run"
    }};

    function showToast(message) {{
      const toast = document.getElementById('toast');
      toast.textContent = message;
      toast.style.display = 'block';
      setTimeout(() => toast.style.display = 'none', 2200);
    }}

    function buildApiSpec() {{
      const headersText = document.getElementById('headers').value.trim() || '{{}}';
      const bodyText = document.getElementById('body').value.trim();
      const urlInput = document.getElementById('url').value.trim();
      let resolvedUrl = urlInput;
      const baseUrl = document.getElementById('baseUrl').value.trim();
      if (resolvedUrl && !/^https?:\/\//i.test(resolvedUrl)) {{
        resolvedUrl = `${{baseUrl.replace(/\/$/, '')}}/${{resolvedUrl.replace(/^\//, '')}}`;
      }}
      return {{
        api: {{
          name: 'Manual API',
          method: document.getElementById('method').value,
          url: resolvedUrl,
          headers: JSON.parse(headersText || '{{}}'),
          body: bodyText ? JSON.parse(bodyText) : null,
          expected_status: Number(document.getElementById('expectedStatus').value || 200)
        }}
      }};
    }}

    async function generateSuite() {{
      const body = buildApiSpec();
      const response = await fetch('/api/generate', {{
        method: 'POST',
        headers: {{ 'Content-Type': 'application/json' }},
        body: JSON.stringify(body)
      }});
      const data = await response.json();
      suiteState.api = data.api;
      suiteState.tests = data.tests;
      document.getElementById('resultsTable').innerHTML = data.tests.map(test => `
        <tr>
          <td>${{test.id}}</td>
          <td>${{test.name}}</td>
          <td>${{test.category}}</td>
          <td>${{test.priority}}</td>
          <td>${{test.metadata?.confidence || 'LOW'}}</td>
          <td>-</td>
          <td><button class=\"link-button\" data-id=\"${{test.id}}\">View</button></td>
        </tr>
      `).join('');
      document.getElementById('totalCount').textContent = String(data.tests.length);
      showToast('Suite generated');
      attachDetailHandlers();
    }}

    async function runSuite() {{
      if (!suiteState.tests || suiteState.tests.length === 0) {{
        await generateSuite();
      }}
      const response = await fetch('/api/run', {{
        method: 'POST',
        headers: {{ 'Content-Type': 'application/json' }},
        body: JSON.stringify({{ tests: suiteState.tests, base_url: document.getElementById('baseUrl').value.trim() }})
      }});
      const data = await response.json();
      const results = data.results || [];
      document.getElementById('resultsTable').innerHTML = results.map(result => `
        <tr>
          <td>${{result.id}}</td>
          <td>${{result.name}}</td>
          <td>${{result.category}}</td>
          <td>${{result.priority}}</td>
          <td>${{result.metadata?.confidence || 'LOW'}}</td>
          <td><span class=\"status ${{result.passed ? 'pass' : 'fail'}}\">${{result.passed ? 'PASS' : 'FAIL'}}</span></td>
          <td><button class=\"link-button\" data-id=\"${{result.id}}\">View</button></td>
        </tr>
      `).join('');
      const passed = results.filter(r => r.passed).length;
      const failed = results.length - passed;
      document.getElementById('passedCount').textContent = String(passed);
      document.getElementById('failedCount').textContent = String(failed);
      showToast('Suite executed');
      attachDetailHandlers();
    }}

    function attachDetailHandlers() {{
      document.querySelectorAll('[data-id]').forEach(el => {{
        el.addEventListener('click', () => {{
          const id = el.getAttribute('data-id');
          if (id) window.location.href = `/ui/test/${{id}}`;
        }});
      }});
    }}

    document.getElementById('generateBtn').addEventListener('click', generateSuite);
    document.getElementById('runBtn').addEventListener('click', runSuite);
    attachDetailHandlers();
  </script>
</body>
</html>"""


@app.get("/ui/test/{test_id}", response_class=HTMLResponse)
def ui_detail(test_id: str) -> str:
    suite = _load_suite()
    test = next((item for item in suite.get("tests", []) if item.get("id") == test_id), None)
    if not test:
        raise HTTPException(status_code=404, detail="Test not found")
    details = json.dumps(test, indent=2)
    return f"""<!doctype html>
<html>
<head>
  <meta charset=\"utf-8\" />
  <title>{test_id}</title>
  <style>
    body {{ font-family: Arial, sans-serif; background: #f4f7fb; margin: 0; padding: 32px; }}
    .container {{ max-width: 980px; margin: auto; }}
    .panel {{ background: white; border-radius: 16px; padding: 24px; box-shadow: 0 8px 20px rgba(15,23,42,0.04); }}
    h1 {{ margin-top: 0; }}
    .meta {{ margin-bottom: 16px; color: #475569; }}
    pre {{ background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 12px; padding: 16px; overflow: auto; white-space: pre-wrap; }}
    a {{ color: #2563eb; text-decoration: none; }}
  </style>
</head>
<body>
  <div class=\"container\">
    <div class=\"panel\">
      <a href=\"/ui\">← Back to dashboard</a>
      <h1>{test.get('name','Unknown')}</h1>
      <div class=\"meta\">
        <strong>ID:</strong> {test.get('id','-')}<br>
        <strong>Category:</strong> {test.get('category','-')}<br>
        <strong>Priority:</strong> {test.get('priority','P2')}
      </div>
      <pre>{details}</pre>
    </div>
  </div>
</body>
</html>"""


@app.get("/ui/batch", response_class=HTMLResponse)
def ui_batch_dashboard() -> str:
    projects = []
    if BATCH_ROOT.exists():
        for project_dir in sorted(BATCH_ROOT.iterdir(), key=lambda item: item.name):
            if not project_dir.is_dir():
                continue
            manifest_path = project_dir / "summary_report.html"
            projects.append({
                "id": project_dir.name,
              "name": project_dir.name,
                "report": str(manifest_path),
                "exists": manifest_path.exists(),
            })

    project_rows = "\n".join(
      f"<tr><td>{p['name']}</td><td>{'Ready' if p['exists'] else 'Pending'}</td><td><a href=\"/api/batch/download?project_id={p['id']}&file=summary_report.html\">Download</a> <button class=\"delete-button\" data-project=\"{p['id']}\">Delete</button></td></tr>"
        for p in projects
    ) or "<tr><td colspan=\"3\">No batch projects created yet.</td></tr>"

    return f"""<!doctype html>
<html>
<head>
  <meta charset=\"utf-8\" />
  <title>TestForge Batch Projects</title>
  <style>
    body {{ font-family: Arial, sans-serif; background: #f4f7fb; margin: 0; padding: 32px; }}
    .container {{ max-width: 1100px; margin: auto; }}
    .controls {{ display: grid; grid-template-columns: 1fr 1.2fr; gap: 22px; }}
    .panel {{ background: white; border-radius: 16px; padding: 22px; box-shadow: 0 8px 20px rgba(15,23,42,0.04); }}
    textarea {{ width: 100%; min-height: 220px; border: 1px solid #dfe7f3; border-radius: 10px; padding: 12px; font-family: monospace; }}
    button {{ background: #2563eb; color: white; border: none; border-radius: 10px; padding: 10px 14px; font-weight: 700; cursor: pointer; }}
    .delete-button {{ background: #dc2626; padding: 7px 10px; }}
    input {{ width: 100%; border: 1px solid #dfe7f3; border-radius: 10px; padding: 10px 12px; }}
    table {{ width: 100%; border-collapse: collapse; margin-top: 12px; }}
    th, td {{ border: 1px solid #dfe7f3; padding: 12px; text-align: left; }}
    th {{ background: #eef3fb; }}
    .muted {{ color: #64748b; }}
    a {{ color: #2563eb; text-decoration: none; }}
    .row {{ display: flex; gap: 12px; margin-top: 10px; }}
  </style>
</head>
<body>
  <div class=\"container\">
    <h1>Batch API Project View</h1>
    <p class=\"muted\">Upload multiple API JSON entries, generate suites for each API, and download a consolidated batch report.</p>
    <div class=\"controls\">
      <div class=\"panel\">
        <h2>Upload JSON project</h2>
        <label>Base URL</label>
        <input id=\"batchBaseUrl\" value=\"http://localhost:8001\" />
        <div class=\"row\">
          <input id=\"batchFile\" type=\"file\" accept=\".json\" />
        </div>
        <div class=\"row\">
          <textarea id=\"batchJson\" placeholder='[{{"name": "Users API", "method": "POST", "url": "/users", "headers": {{"Content-Type": "application/json"}}, "body": {{"name": "Lokesh"}}, "expected_status": 200}}, {{"name": "Orders API", "method": "GET", "url": "/orders", "expected_status": 200}}]'></textarea>
        </div>
        <div class=\"row\">
          <button id=\"uploadBtn\">Create Batch Project</button>
        </div>
      </div>

      <div class=\"panel\">
        <h2>Existing batch projects</h2>
        <table>
          <thead><tr><th>Project</th><th>Status</th><th>Download</th></tr></thead>
          <tbody>{project_rows}</tbody>
        </table>
      </div>
    </div>
  </div>

  <script>
    async function uploadBatchProject() {{
      const raw = document.getElementById('batchJson').value.trim();
      const fileInput = document.getElementById('batchFile');
      let payload = raw ? JSON.parse(raw) : [];
      if (fileInput.files && fileInput.files[0]) {{
        const text = await fileInput.files[0].text();
        payload = JSON.parse(text);
      }}
      const response = await fetch('/api/batch/upload', {{
        method: 'POST',
        headers: {{ 'Content-Type': 'application/json' }},
        body: JSON.stringify({{ apis: payload, base_url: document.getElementById('batchBaseUrl').value.trim() }})
      }});
      const data = await response.json();
      if (!response.ok) {{
        alert(data.detail || 'Upload failed');
        return;
      }}
      window.location.href = `/ui/batch?project_id=${{data.project_id}}`;
    }}

    document.getElementById('uploadBtn').addEventListener('click', uploadBatchProject);
    document.querySelectorAll('.delete-button').forEach(button => {{
      button.addEventListener('click', async () => {{
        const projectId = button.dataset.project;
        if (!confirm(`Delete ${{projectId}} and all generated reports?`)) return;
        const response = await fetch(`/api/batch/${{projectId}}`, {{ method: 'DELETE' }});
        if (response.ok) window.location.reload();
        else alert('Unable to delete batch project');
      }});
    }});
  </script>
</body>
</html>"""


@app.get("/api/batch/download")
def download_batch_report(project_id: str, file: str = "summary_report.html") -> FileResponse:
    project_dir = _batch_project_path(project_id)
    if project_dir is None or not project_dir.exists():
      raise HTTPException(status_code=404, detail="Project not found")
    target = (project_dir / file).resolve()
    if project_dir.resolve() not in target.parents or not target.is_file():
      raise HTTPException(status_code=404, detail="Report not found")
    return FileResponse(target, media_type="text/html", filename=file)


def _batch_project_path(project_id: str) -> Path | None:
  valid_timestamped_id = r"batch_report_[0-9]{8}_[0-9]{6}(?:_[0-9]+)?"
  valid_legacy_id = r"[0-9a-f]{32}"
  if not re.fullmatch(f"(?:{valid_timestamped_id}|{valid_legacy_id})", project_id):
    return None
  return BATCH_ROOT / project_id


@app.delete("/api/batch/{project_id}")
def delete_batch_project(project_id: str) -> dict[str, str]:
    project_dir = _batch_project_path(project_id)
    if project_dir is None or not project_dir.is_dir():
        raise HTTPException(status_code=404, detail="Project not found")
    shutil.rmtree(project_dir)
    return {"project_id": project_id, "status": "deleted"}


@app.post("/api/batch/upload")
def upload_batch_project(payload: dict) -> dict:
    items = payload.get("apis") if isinstance(payload, dict) else payload
    base_url = payload.get("base_url") if isinstance(payload, dict) else None
    if not isinstance(items, list) or not items:
        raise HTTPException(status_code=400, detail="Expected a JSON array of API entries")

    try:
        if items and isinstance(items[0], dict) and "baseUrl" in items[0] and "methods" in items[0]:
            items = expand_api_catalog(items)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    project_id = f"batch_report_{timestamp}"
    suffix = 1
    while (BATCH_ROOT / project_id).exists():
      suffix += 1
      project_id = f"batch_report_{timestamp}_{suffix}"
    project_dir = BATCH_ROOT / project_id
    project_dir.mkdir(parents=True, exist_ok=True)

    for index, api_spec in enumerate(items):
        api_name = str(api_spec.get("name") or f"api_{index + 1}").strip()
        safe_name = "".join(ch if ch.isalnum() else "_" for ch in api_name).strip("_") or f"api_{index + 1}"
        api_dir = project_dir / f"api_{index + 1:02d}_{safe_name.lower()}"
        api_dir.mkdir(parents=True, exist_ok=True)
        (api_dir / "api.json").write_text(json.dumps(api_spec, indent=2), encoding="utf-8")

    summary = process_batch(project_dir, base_url=base_url or get_config().base_url)
    summary["project_id"] = project_id
    summary["project_dir"] = str(project_dir)
    return summary


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/api/generate")
def generate_api_tests(payload: dict) -> dict:
    api_spec = payload.get("api", {})
    tests = generate_tests(api_spec)
    suite = {"api": api_spec, "tests": tests}
    SUITE_PATH.parent.mkdir(parents=True, exist_ok=True)
    SUITE_PATH.write_text(json.dumps(suite, indent=2), encoding="utf-8")
    return {"api": api_spec, "tests": tests, "suite_path": str(SUITE_PATH)}


@app.post("/api/run")
def run_suite(payload: dict) -> dict:
    tests = payload.get("tests", [])
    base_url = payload.get("base_url")
    results = execute_generated_tests(tests, base_url=base_url)
    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    generate_html_report(results, REPORT_PATH)
    build_dashboard_html(results, DASHBOARD_PATH)
    export_results(results, EXPORT_DIR)
    return {
        "results": results,
        "report_path": str(REPORT_PATH),
        "dashboard_path": str(DASHBOARD_PATH),
        "export_dir": str(EXPORT_DIR),
    }
