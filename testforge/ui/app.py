from __future__ import annotations

import json
import re
import shutil
from datetime import datetime, timezone
from html import escape
from pathlib import Path
from typing import Any
from urllib.parse import quote

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse, HTMLResponse, RedirectResponse, StreamingResponse

from frontend.dashboard import build_dashboard_html
from testforge.batch_runner import process_batch
from testforge.config import get_config
from testforge.contracts.catalog_loader import expand_api_catalog
from testforge.execution.runner import execute_generated_tests, generate_html_report, stream_generated_tests
from testforge.exporters.exporter import export_results
from testforge.generation.test_generator import generate_tests

app = FastAPI(title="TestForge UI", version="0.1.0")
ROOT = Path(__file__).resolve().parent.parent.parent
SUITE_PATH = ROOT / "sample_project" / "generated_suite.json"
REPORT_PATH = ROOT / "sample_project" / "report.html"
DASHBOARD_PATH = ROOT / "sample_project" / "dashboard.html"
EXPORT_DIR = ROOT / "sample_project" / "exports"
BATCH_ROOT = ROOT / "sample_project" / "batches"


def _load_suite() -> dict[str, Any]:
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
    rows = "".join(
        "<tr><td>{id}</td><td>{name}</td><td>{category}</td><td>{priority}</td>"
        "<td><button class=\"link-button\" data-id=\"{id}\">View</button></td></tr>".format(
            id=escape(str(test.get("id", "-"))),
            name=escape(str(test.get("name", "-"))),
            category=escape(str(test.get("category", "-"))),
            priority=escape(str(test.get("priority", "P2"))),
        )
        for test in tests
    )
    config = get_config()
    return f"""<!doctype html>
<html><head><meta charset="utf-8"><title>TestForge</title>
<style>
body {{ font-family: Arial, sans-serif; background: #f4f7fb; color: #111827; margin: 0; }}
.container {{ max-width: 1200px; margin: auto; padding: 32px 20px; }}
.panel {{ background: white; border: 1px solid #dfe7f3; border-radius: 12px; padding: 22px; margin-bottom: 20px; }}
.actions {{ display: flex; gap: 10px; margin: 14px 0; }}
button {{ border: 0; border-radius: 8px; padding: 10px 14px; cursor: pointer; font-weight: 700; }}
.primary {{ background: #2563eb; color: white; }} .secondary {{ background: #e2e8f0; color: #111827; }}
.stats {{ display: flex; gap: 12px; }} .stat {{ border: 1px solid #dfe7f3; padding: 12px; min-width: 100px; }}
.stat .label {{ color: #64748b; font-size: 12px; }} .stat .value {{ font-size: 24px; font-weight: 700; }}
table {{ width: 100%; border-collapse: collapse; margin-top: 16px; }} th, td {{ border: 1px solid #dfe7f3; padding: 10px; text-align: left; }}
.status {{ padding: 4px 8px; border-radius: 999px; }} .pass {{ color: #15803d; background: #dcfce7; }} .fail {{ color: #b91c1c; background: #fee2e2; }}
.charts {{ display: grid; grid-template-columns: 1fr 1fr; gap: 20px; margin-top: 20px; }}
</style></head><body><main class="container">
<div class="panel"><h1>TestForge</h1><p>Environment: {escape(str(config.environment))}</p>
<label>Base URL <input id="baseUrl" value="{escape(str(config.base_url), quote=True)}"></label>
<div class="actions"><button class="primary" id="generateBtn">Generate Suite</button><button class="secondary" id="runBtn">Run Suite</button><button class="secondary" id="liveRunBtn">Run Suite (Live)</button></div></div>
<div class="panel"><h2>Results</h2><div class="stats"><div class="stat"><div class="label">Total</div><div class="value" id="totalCount">{len(tests)}</div></div><div class="stat"><div class="label">Passed</div><div class="value" id="passedCount">0</div></div><div class="stat"><div class="label">Failed</div><div class="value" id="failedCount">0</div></div></div>
<table><thead><tr><th>ID</th><th>Name</th><th>Category</th><th>Priority</th><th>Open</th></tr></thead><tbody id="resultsTable">{rows}</tbody></table>
<div class="charts"><canvas id="passFailChart"></canvas><canvas id="latencyChart"></canvas></div><p id="toast"></p></div></main>
<script src="https://cdnjs.cloudflare.com/ajax/libs/Chart.js/4.4.1/chart.umd.min.js"></script><script>
const passFailChart = new Chart(document.getElementById('passFailChart'), {{type:'bar',data:{{labels:['Passed','Failed'],datasets:[{{data:[0,0],backgroundColor:['#16a34a','#dc2626']}}]}},options:{{animation:false,scales:{{y:{{beginAtZero:true}}}}}}}});
const latencyChart = new Chart(document.getElementById('latencyChart'), {{type:'line',data:{{labels:[],datasets:[{{label:'Response time (ms)',data:[],borderColor:'#2563eb'}}]}},options:{{animation:false}}}});
const suiteState = {{tests: {json.dumps(tests, default=str)}}};
function updateCounts(passed, failed) {{ document.getElementById('passedCount').textContent=passed; document.getElementById('failedCount').textContent=failed; }}
function addResult(result) {{ const row=document.createElement('tr'); row.innerHTML=`<td>${{result.id}}</td><td>${{result.name}}</td><td>${{result.category}}</td><td>${{result.priority}}</td><td><span class="status ${{result.passed?'pass':'fail'}}">${{result.passed?'PASS':'FAIL'}} (${{result.status_code ?? 'ERR'}})</span></td>`; document.getElementById('resultsTable').appendChild(row); }}
async function runSuite() {{ const response=await fetch('/api/run',{{method:'POST',headers:{{'Content-Type':'application/json'}},body:JSON.stringify({{tests:suiteState.tests,base_url:document.getElementById('baseUrl').value}})}}); const data=await response.json(); document.getElementById('resultsTable').innerHTML=''; data.results.forEach(addResult); updateCounts(data.results.filter(r=>r.passed).length,data.results.filter(r=>!r.passed).length); }}
function runSuiteLive() {{ document.getElementById('resultsTable').innerHTML=''; let passed=0, failed=0; const source=new EventSource('/api/run/stream?base_url='+encodeURIComponent(document.getElementById('baseUrl').value)); source.onmessage=(event)=>{{const result=JSON.parse(event.data); addResult(result); if(result.passed) passed++; else failed++; updateCounts(passed,failed); passFailChart.data.datasets[0].data=[passed,failed]; passFailChart.update(); latencyChart.data.labels.push(result.id); latencyChart.data.datasets[0].data.push(result.elapsed_ms); latencyChart.update();}}; source.addEventListener('done',()=>{{source.close(); document.getElementById('toast').textContent=`Suite complete: ${{passed}} passed, ${{failed}} failed`;}}); source.onerror=()=>source.close(); }}
document.getElementById('runBtn').onclick=runSuite; document.getElementById('liveRunBtn').onclick=runSuiteLive;
</script></body></html>"""


@app.get("/ui/test/{test_id}", response_class=HTMLResponse)
def ui_detail(test_id: str) -> str:
    test = next((item for item in _load_suite().get("tests", []) if item.get("id") == test_id), None)
    if not test:
        raise HTTPException(status_code=404, detail="Test not found")
    return f"<html><body><a href='/ui'>Back</a><h1>{escape(str(test.get('name', 'Unknown')))}</h1><pre>{escape(json.dumps(test, indent=2, default=str))}</pre></body></html>"


@app.get("/ui/batch", response_class=HTMLResponse)
def ui_batch_dashboard() -> str:
    projects = []
    if BATCH_ROOT.exists():
        projects = sorted(item.name for item in BATCH_ROOT.iterdir() if item.is_dir())
    rows = "".join(f"<li>{escape(project)}</li>" for project in projects) or "<li>No batch projects created yet.</li>"
    return f"<html><body><a href='/ui'>Back</a><h1>Batch API Projects</h1><ul>{rows}</ul></body></html>"


def _batch_project_path(project_id: str) -> Path | None:
    if not re.fullmatch(r"(?:batch_report_[0-9]{8}_[0-9]{6}(?:_[0-9]+)?|[0-9a-f]{32})", project_id):
        return None
    return BATCH_ROOT / project_id


@app.delete("/api/batch/{project_id}")
def delete_batch_project(project_id: str) -> dict[str, str]:
    project_dir = _batch_project_path(project_id)
    if project_dir is None or not project_dir.is_dir():
        raise HTTPException(status_code=404, detail="Project not found")
    shutil.rmtree(project_dir)
    return {"project_id": project_id, "status": "deleted"}


@app.get("/api/batch/download")
def download_batch_report(project_id: str, file: str = "summary_report.html") -> FileResponse:
    project_dir = _batch_project_path(project_id)
    if project_dir is None or not project_dir.exists():
        raise HTTPException(status_code=404, detail="Project not found")
    target = (project_dir / file).resolve()
    if project_dir.resolve() not in target.parents or not target.is_file():
        raise HTTPException(status_code=404, detail="Report not found")
    return FileResponse(target, media_type="text/html", filename=file)


@app.post("/api/batch/upload")
def upload_batch_project(payload: dict) -> dict:
    items = payload.get("apis", [])
    base_url = payload.get("base_url")
    if not isinstance(items, list) or not items:
        raise HTTPException(status_code=400, detail="Expected a JSON array of API entries")
    if isinstance(items[0], dict) and "baseUrl" in items[0] and "methods" in items[0]:
        items = expand_api_catalog(items)
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    project_id = f"batch_report_{timestamp}"
    project_dir = BATCH_ROOT / project_id
    project_dir.mkdir(parents=True, exist_ok=True)
    for index, api_spec in enumerate(items):
        api_dir = project_dir / f"api_{index + 1:02d}_{quote(str(api_spec.get('name', 'api')), safe='').lower()}"
        api_dir.mkdir(parents=True, exist_ok=True)
        (api_dir / "api.json").write_text(json.dumps(api_spec, indent=2), encoding="utf-8")
    summary = process_batch(project_dir, base_url=base_url or get_config().base_url)
    summary.update(project_id=project_id, project_dir=str(project_dir))
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
    results = execute_generated_tests(payload.get("tests", []), base_url=payload.get("base_url"))
    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    generate_html_report(results, REPORT_PATH)
    build_dashboard_html(results, DASHBOARD_PATH)
    export_results(results, EXPORT_DIR)
    return {"results": results, "report_path": str(REPORT_PATH), "dashboard_path": str(DASHBOARD_PATH), "export_dir": str(EXPORT_DIR)}


@app.get("/api/run/stream")
def stream_suite(base_url: str | None = None, suite: str | None = None) -> StreamingResponse:
    suite_data = _load_suite()
    if suite:
        try:
            suite_data = json.loads(suite)
        except json.JSONDecodeError as exc:
            raise HTTPException(status_code=400, detail="Invalid suite JSON") from exc

    def event_stream():
        for result in stream_generated_tests(suite_data.get("tests", []), base_url=base_url):
            yield f"data: {json.dumps(result, default=str)}\n\n"
        yield "event: done\ndata: {}\n\n"

    return StreamingResponse(event_stream(), media_type="text/event-stream")
