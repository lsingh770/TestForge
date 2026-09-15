# API Contract

## Core endpoints

### GET /health
Returns service health status.

### POST /api/generate
Accepts either:

Returns:

### POST /api/run
Consumes a test suite and returns execution results.

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
