# TestForge

TestForge is an AI-powered REST API testing platform MVP. It focuses on the core principle from the specification: generate deterministic, standalone tests that can run without any AI dependency.

## Features


## Quick start

1. Start the demo API:
   ```bash
   python demo_api.py
   ```

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


## Notes

This is an MVP focused on the vertical slice: parsing API input, generating tests, and executing a standalone suite without AI runtime dependencies.
