from __future__ import annotations

import argparse
import json
from pathlib import Path

from frontend.dashboard import build_dashboard_html
from testforge.batch_runner import process_batch
from testforge.config import get_config
from testforge.contracts.catalog_loader import expand_api_catalog
from testforge.exporters.exporter import export_results
from testforge.generation.test_generator import generate_tests
from testforge.parsers.curl_parser import parse_curl
from testforge.execution.runner import execute_generated_tests, generate_html_report


DEFAULT_SUITE = Path(__file__).resolve().parent.parent / "sample_project" / "generated_suite.json"


def _generate_from_curl(curl_text: str):
    api_spec = parse_curl(curl_text)
    tests = generate_tests({
        "name": api_spec.name,
        "method": api_spec.method,
        "url": api_spec.url,
        "headers": api_spec.headers,
        "body": api_spec.body,
        "expected_status": api_spec.expected_status,
    })
    return {"api": api_spec.__dict__, "tests": tests}


def _handle_generate(args):
    if args.curl:
        payload = _generate_from_curl(args.curl)
    else:
        payload = {
            "api": {
                "name": "Manual API",
                "method": args.method,
                "url": args.url,
                "headers": {},
                "body": None,
                "expected_status": args.expected_status,
            },
            "tests": generate_tests({
                "name": "Manual API",
                "method": args.method,
                "url": args.url,
                "headers": {},
                "body": None,
                "expected_status": args.expected_status,
            }),
        }

    out_path = Path(args.output) if args.output else DEFAULT_SUITE.parent / "generated_suite.json"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    print(f"Generated {len(payload['tests'])} tests at {out_path}")


def _handle_run(args):
    suite_path = Path(args.suite) if args.suite else DEFAULT_SUITE
    if not suite_path.exists():
        raise FileNotFoundError(f"Suite file not found: {suite_path}")
    suite = json.loads(suite_path.read_text(encoding="utf-8"))
    results = execute_generated_tests(suite["tests"], base_url=args.base_url)
    report_path = Path(args.report) if args.report else DEFAULT_SUITE.parent / "report.html"
    dashboard_path = Path(args.dashboard) if args.dashboard else DEFAULT_SUITE.parent / "dashboard.html"
    export_dir = Path(args.export_dir) if args.export_dir else DEFAULT_SUITE.parent / "exports"
    generate_html_report(results, report_path)
    build_dashboard_html(results, dashboard_path)
    exported = export_results(results, export_dir)
    passed = sum(1 for r in results if r["passed"])
    failed = sum(1 for r in results if not r["passed"])
    print(f"Run complete: {passed} passed, {failed} failed")
    print(f"HTML report written to {report_path}")
    print(f"Dashboard written to {dashboard_path}")
    print(f"Structured exports written to {export_dir}: {exported}")


def _handle_batch(args):
    batch_dir = args.dir
    if args.file:
        catalog = json.loads(Path(args.file).read_text(encoding="utf-8"))
        output_dir = Path(args.output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)
        for index, api_spec in enumerate(expand_api_catalog(catalog), start=1):
            api_name = str(api_spec.get("name", f"api_{index}"))
            safe_name = "".join(char if char.isalnum() else "_" for char in api_name).strip("_").lower()
            api_dir = output_dir / f"api_{index:03d}_{safe_name or index}"
            api_dir.mkdir(parents=True, exist_ok=True)
            (api_dir / "api.json").write_text(json.dumps(api_spec, indent=2), encoding="utf-8")
        batch_dir = str(output_dir)
    summary = process_batch(batch_dir, base_url=args.base_url)
    total = len(summary["apis"])
    passed = sum(api["passed"] for api in summary["apis"])
    failed = sum(api["failed"] for api in summary["apis"])
    print(f"Batch complete: {total} API(s) processed")
    print(f"Aggregate results: {passed} passed, {failed} failed")
    for api in summary["apis"]:
        print(f"- {api['api_name']}: {api['passed']} passed, {api['failed']} failed -> {api['report_file']}")


def build_parser():
    config = get_config()
    parser = argparse.ArgumentParser(description="TestForge API quality tool")
    subparsers = parser.add_subparsers(dest="command", required=True)

    generate_parser = subparsers.add_parser("generate", help="Generate a reusable test suite")
    generate_parser.add_argument("--curl", type=str)
    generate_parser.add_argument("--method", type=str, default="POST")
    generate_parser.add_argument("--url", type=str, default=f"{config.base_url}/api/users")
    generate_parser.add_argument("--expected-status", type=int, default=201)
    generate_parser.add_argument("--output", type=str, default=str(DEFAULT_SUITE.parent / "generated_suite.json"))
    generate_parser.set_defaults(func=_handle_generate)

    run_parser = subparsers.add_parser("run", help="Execute a generated suite")
    run_parser.add_argument("--suite", type=str, default=str(DEFAULT_SUITE))
    run_parser.add_argument("--base-url", type=str, default=config.base_url)
    run_parser.add_argument("--report", type=str, default=str(DEFAULT_SUITE.parent / "report.html"))
    run_parser.add_argument("--dashboard", type=str, default=str(DEFAULT_SUITE.parent / "dashboard.html"))
    run_parser.add_argument("--export-dir", type=str, default=str(DEFAULT_SUITE.parent / "exports"))
    run_parser.set_defaults(func=_handle_run)

    batch_parser = subparsers.add_parser("batch", help="Process a directory of API definitions")
    batch_parser.add_argument("--dir", type=str, help="Directory containing api.json files")
    batch_parser.add_argument("--file", type=str, help="Catalog JSON file containing services and CRUD methods")
    batch_parser.add_argument("--output-dir", type=str, default="sample_project/catalog_batch", help="Output directory for catalog suites")
    batch_parser.add_argument("--base-url", type=str, default=config.base_url)
    batch_parser.set_defaults(func=_handle_batch)

    return parser


def main():
    parser = build_parser()
    args = parser.parse_args()
    if args.command == "batch" and not args.dir and not args.file:
        parser.error("batch requires --dir or --file")
    args.func(args)


if __name__ == "__main__":
    main()
