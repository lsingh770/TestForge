# API Contract

## Core endpoints

### GET /health
Returns service health status.

### POST /api/generate
Accepts a JSON object with an `api` specification. The response contains the original API specification, generated tests, and the path of the persisted suite.

### POST /api/run
Accepts `{ "tests": [...], "base_url": "http://localhost:8001" }`. It executes each test and returns result objects plus paths for the generated report, dashboard, and exports.

Each result includes the test identity, pass/fail status, HTTP status, response text, request details, evaluated assertions, and `elapsed_ms` request duration.

### GET /api/run/stream
Streams the same suite results as Server-Sent Events. Each completed test is sent as `data: {JSON}` followed by a blank line; the final event is `event: done` with an empty JSON object.

## Example payload

```json
{
  "api": {
    "name": "Demo API",
    "method": "POST",
    "url": "http://localhost:8001/users",
    "headers": {"Content-Type": "application/json"},
    "body": {"name": "Lokesh", "email": "lokesh@example.com", "age": 35},
    "expected_status": 200
  }
}
```

### POST /api/batch/upload
Accepts either a normalized endpoint array or a CRUD catalog array. Creates a timestamped batch project and returns its project ID and summary.

### GET /api/batch/download
Downloads a project report. Required query parameter: `project_id`. Optional query parameter: `file`, defaulting to `summary_report.html`.

### DELETE /api/batch/{project_id}
Deletes a generated batch project. Timestamped projects and legacy UUID-named projects are supported.
