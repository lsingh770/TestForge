# TestForge

TestForge is an AI-powered REST API testing platform MVP. It focuses on the core principle from the specification: generate deterministic, standalone tests that can run without any AI dependency.

## Features

- Parse cURL and OpenAPI input into normalized API specifications.
- Generate deterministic positive, negative, and contract-oriented test cases.
- Execute generated suites against absolute URLs or a configured base URL.
- Evaluate status-code, response-presence, request-method, and JSON-key assertions.
- Produce HTML reports, dashboard data, and CSV/JSON/XML exports.
- Run individual suites or batches of API definitions from the command line.
- Browse generated suites and batch reports through the FastAPI web UI.
- Stream test results live over Server-Sent Events as each request completes, with a live pass/fail count and response-time chart in the browser dashboard.

## Quick start

1. Start the demo API:
   ```bash
   python demo_api.py
   ```
   This starts on `http://localhost:8001`. Every route except `/health` and `/login` requires an `Authorization: Bearer demo-token` header — requests without it will get a `401`, which is expected and is itself one of the generated negative test cases.

2. Generate a test suite:
   ```bash
   api-tester generate --method POST --url http://localhost:8001/users --expected-status 200 --output sample_project/generated_suite.json
   ```

3. Run the suite:
   ```bash
   api-tester run --suite sample_project/generated_suite.json --base-url http://localhost:8001
   ```

4. Run a catalog of REST APIs:
   ```bash
   api-tester batch --file /path/to/crud_test_apis.json --output-dir sample_project/catalog_batch
   ```

   The catalog format uses `baseUrl` and a `methods` object such as `"POST": "POST /users"`.
   Each supported method becomes an independent executable endpoint suite. Entries marked `N/A`
   are skipped. Absolute URLs from the catalog are preserved; `--base-url` is used only for
   relative endpoint definitions.

5. Use the browser batch view:
   ```bash
   uvicorn testforge.ui.app:app --reload --port 8000
   ```
   Then open `http://localhost:8000/ui/batch` and upload the catalog JSON file.

## Project structure

```text
testforge/
   contracts/           OpenAPI and catalog loaders
   execution/           HTTP execution and HTML reporting
   exporters/           CSV, JSON, and XML result exporters
   generation/          Deterministic test generation
   parsers/             cURL parsing
   ui/                  FastAPI application and browser dashboard
   batch_runner.py      Batch suite orchestration
   cli.py               api-tester command-line entry point
   config.py            Environment-based configuration
   models.py            Shared data models
frontend/              Dashboard HTML helpers
tests/                 Regression tests
demo_api.py            Local demo service
sample_project/        Example suite and generated local output
```

## Notes

This is an MVP focused on the vertical slice: parsing API input, generating tests, and executing a standalone suite without AI runtime dependencies.
