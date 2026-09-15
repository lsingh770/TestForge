# TestForge User Guide

TestForge generates and executes reusable REST API tests. It accepts individual API requests, cURL commands, normalized JSON endpoint definitions, and multi-service CRUD catalogs.

## 1. Requirements

- Python 3.11 or newer
- Network access to the APIs being tested
- Credentials supplied in the request headers when an API requires authentication

TestForge sends real HTTP requests. Run it only against systems you are authorized to test.

## 2. Installation

From the project directory:

```bash
python3 -m venv .venv
. .venv/bin/activate
pip install -e .
```

Verify the installation:

```bash
api-tester --help
python -m pytest -q
```

## 3. Quick start with the demo API

Start the demo service in one terminal:

```bash
. .venv/bin/activate
python demo_api.py
```

The demo service listens on `http://localhost:8002`. Use the same port in the TestForge commands:

```bash
api-tester generate \
  --method POST \
  --url http://localhost:8002/users \
  --expected-status 200 \
  --output sample_project/generated_suite.json

api-tester run \
  --suite sample_project/generated_suite.json \
  --base-url http://localhost:8002
```

The run command writes an HTML report, dashboard, and structured exports under `sample_project/`.

## 4. CLI commands

### Generate a suite from request options

```bash
api-tester generate \
  --method POST \
  --url https://api.example.com/users \
  --expected-status 201 \
  --output sample_project/generated_suite.json
```

This creates a JSON suite. Review or edit the suite before execution when the target API requires a specific body, headers, status code, or assertion.

### Generate from cURL

```bash
api-tester generate \
  --curl 'curl -X POST https://api.example.com/users -H "Content-Type: application/json" -d '\''{"name":"Ada","email":"ada@example.com"}'\'' ' \
  --output sample_project/generated_suite.json
```

The cURL parser extracts the method, absolute URL, headers, and JSON body. A body supplied by the user is retained as JSON.

### Execute a suite

```bash
api-tester run \
  --suite path/to/generated_suite.json \
  --base-url https://api.example.com \
  --report output/report.html \
  --dashboard output/dashboard.html \
  --export-dir output/exports
```

Absolute URLs in the suite are used unchanged. Relative URLs are resolved against `--base-url`.

### Process a directory batch

A directory batch contains one folder per API, with an `api.json` file in each folder:

```text
api_batch/
  users/api.json
  orders/api.json
```

Run it with:

```bash
api-tester batch --dir api_batch --base-url https://api.example.com
```

Each API folder receives a generated suite and report. The batch root receives `summary_report.html`.

### Process a CRUD catalog file

```bash
api-tester batch \
  --file /path/to/crud_test_apis_with_bodies.json \
  --output-dir sample_project/catalog_batch
```

The catalog adapter understands records with:

- `baseUrl`
- `headers`
- `auth`
- `resource`
- `methods`

Each method can be a string:

```json
"GET": "GET /posts/1"
```

or an object containing its own request body:

```json
"POST": {
  "request": "POST /posts",
  "body": {
    "title": "foo",
    "body": "bar",
    "userId": 1
  }
}
```

The method-level body is sent only with that method. GET and DELETE requests without a supplied body are sent without JSON. Methods whose request is marked `N/A` are skipped.

## 5. Browser UI

Start the UI:

```bash
. .venv/bin/activate
uvicorn testforge.ui.app:app --reload --port 8000
```

Open:

```text
http://localhost:8000/ui
```

The main page supports manual request generation and execution.

For multi-API projects open:

```text
http://localhost:8000/ui/batch
```

The batch page supports:

1. Uploading a catalog JSON file or pasting a JSON array.
2. Setting a base URL for relative requests.
3. Creating a timestamped project named `batch_report_YYYYMMDD_HHMMSS`.
4. Viewing existing projects.
5. Downloading the consolidated summary report.
6. Deleting old projects.

Absolute URLs from an uploaded catalog take precedence over the UI base URL.

## 6. Request and response behavior

Every generated test stores:

- Test ID and name
- HTTP method
- Final request URL
- Request headers
- Request JSON body
- Assertions
- Category and priority
- Generation metadata

Every execution result stores:

- Pass or fail status
- HTTP response status code
- Response body text
- Error text, if the request failed
- Full request details
- Expected assertions

The HTML reports display request and response details for every test.

## 7. Generated coverage

For each endpoint, TestForge can generate cases such as:

- Valid request
- Missing required fields
- Invalid field values
- Boundary values
- Duplicate or replay request for write methods
- Resource-not-found path cases
- Unauthorized request when authorization is configured
- Response contract checks when `response_schema` is supplied

Generated tests are deterministic JSON artifacts. AI is not required at execution time.

## 8. Reports and exports

The CLI and UI can produce:

- HTML execution report
- HTML dashboard
- JSON results
- CSV results
- JUnit XML results
- Batch summary HTML report

Reports are generated locally in the output paths supplied to the command or in the default `sample_project/` directories.

## 9. Configuration

Runtime defaults are controlled by environment variables:

```bash
export TESTFORGE_ENV=qa
export TESTFORGE_BASE_URL=https://qa.example.com
export TESTFORGE_API_KEY=your-key
```

Supported environment names include `dev`, `qa`, `staging`, and `prod`. An explicit URL supplied in a request, catalog entry, UI form, or CLI option should be used for that request.

Do not commit tokens, API keys, cookies, or other secrets to JSON suites or reports.

## 10. Troubleshooting

### The UI will not start

Check that the port is available and that the virtual environment is active:

```bash
. .venv/bin/activate
python -m py_compile testforge/ui/app.py
uvicorn testforge.ui.app:app --reload --port 8000
```

Use another port if needed:

```bash
uvicorn testforge.ui.app:app --reload --port 8001
```

### Requests go to the wrong host

Use an absolute URL in the API definition or catalog. Relative URLs use the supplied `--base-url` or UI base URL. TestForge does not replace an absolute user-provided URL with a local default.

### JSON body is missing

For a normalized endpoint, use a JSON object in `body`. For the catalog format, put the body inside the method object beside `request`. Confirm the generated `generated_suite.json` before running it.

### Authentication fails

Provide the required header in the service-level `headers` object or endpoint definition. Descriptive text in `auth` documents the requirement but does not create a credential or replace a placeholder token.

### Old batch projects cannot be deleted

Restart the UI server after upgrading. Both timestamped projects and legacy UUID-named projects are supported by the delete route.

### Runs are slow

Execution sends real requests sequentially and uses a network timeout for each request. Large catalogs can therefore take time, especially when an external service is unavailable.

## 11. Project layout

```text
README.md                         Short project overview
USER_GUIDE.md                     This guide
Master Prompt ...md               Product specification
testforge/cli.py                  CLI commands
testforge/contracts/              Catalog and OpenAPI input adapters
testforge/generation/             Deterministic test generation
testforge/execution/              HTTP execution and HTML reports
testforge/exporters/               JSON, CSV, and JUnit output
testforge/ui/                     Browser UI and batch project routes
testforge/batch_runner.py         Folder batch orchestration
frontend/dashboard.py             Dashboard HTML generation
demo_api.py                       Local demo REST API
tests/                            Regression tests
```

## 12. Development validation

Run the complete test suite:

```bash
python -m pytest -q
```

For fast catalog-only validation:

```bash
python -m pytest tests/test_generator.py -k catalog -q
```

The tests that process batches may call real local or external URLs. Use mocked tests for fast unit-level validation when changing request execution behavior.
