from testforge.generation.test_generator import generate_tests


def test_generate_tests_creates_executable_cases():
    api_spec = {
        "name": "Create User",
        "method": "POST",
        "url": "https://example.com/api/users",
        "headers": {"Content-Type": "application/json"},
        "body": {"name": "Lokesh", "email": "lokesh@example.com", "age": 35},
        "expected_status": 201,
        "response_schema": {
            "id": {"type": "integer"},
            "name": {"type": "string"},
            "email": {"type": "string"},
        },
    }

    tests = generate_tests(api_spec)

    assert len(tests) >= 5
    assert all(test["method"] == "POST" for test in tests)
    assert all("assertions" in test for test in tests)
    assert all("metadata" in test for test in tests)
    assert all("priority" in test["metadata"] for test in tests)
    assert any(test["category"] == "positive" for test in tests)
    assert any(test["category"] == "negative" for test in tests)
    assert any(test["category"] == "contract" for test in tests)


def test_report_includes_request_and_response_details(tmp_path):
    from testforge.execution.runner import execute_generated_tests, generate_html_report

    result = execute_generated_tests([
        {
            "id": "TC-REPORT-1",
            "name": "report_detail",
            "category": "positive",
            "method": "POST",
            "url": "https://example.com/api/users",
            "headers": {"Content-Type": "application/json"},
            "body": {"name": "Lokesh"},
            "assertions": ["assert response.status_code == 200"],
            "priority": "P1",
        }
    ], base_url="https://example.com")

    report_path = tmp_path / "report.html"
    generate_html_report(result, report_path)
    html = report_path.read_text(encoding="utf-8")

    assert "Request" in html
    assert "Response" in html
    assert "https://example.com/api/users" in html
    assert "Lokesh" in html


def test_batch_runner_processes_multiple_apis(tmp_path):
    from testforge.batch_runner import process_batch

    first = tmp_path / "api_01_users"
    second = tmp_path / "api_02_orders"
    first.mkdir()
    second.mkdir()

    (first / "api.json").write_text('{"name": "Users API", "method": "POST", "url": "http://localhost:8001/users", "headers": {"Content-Type": "application/json"}, "body": {"name": "Lokesh"}, "expected_status": 200}', encoding="utf-8")
    (second / "api.json").write_text('{"name": "Orders API", "method": "GET", "url": "http://localhost:8001/orders", "headers": {}, "expected_status": 200}', encoding="utf-8")

    summary = process_batch(tmp_path, base_url="http://localhost:8001")

    assert len(summary["apis"]) == 2
    assert summary["apis"][0]["suite_file"].endswith("generated_suite.json")
    assert (first / "generated_suite.json").exists()
    assert (second / "report.html").exists()


def test_batch_runner_creates_summary_report(tmp_path):
    from testforge.batch_runner import process_batch

    first = tmp_path / "api_01_users"
    second = tmp_path / "api_02_orders"
    first.mkdir()
    second.mkdir()

    (first / "api.json").write_text('{"name": "Users API", "method": "POST", "url": "http://localhost:8001/users", "headers": {"Content-Type": "application/json"}, "body": {"name": "Lokesh"}, "expected_status": 200}', encoding="utf-8")
    (second / "api.json").write_text('{"name": "Orders API", "method": "GET", "url": "http://localhost:8001/orders", "headers": {}, "expected_status": 200}', encoding="utf-8")

    summary = process_batch(tmp_path, base_url="http://localhost:8001")

    assert (tmp_path / "summary_report.html").exists()
    assert "Batch Summary" in (tmp_path / "summary_report.html").read_text(encoding="utf-8")
    assert "Users API" in summary["summary_html"]


def test_generate_tests_creates_dynamic_payload_when_body_missing():
    from testforge.generation.test_generator import generate_tests

    tests = generate_tests({
        "name": "Create User",
        "method": "POST",
        "url": "/users",
        "headers": {"Content-Type": "application/json"},
        "expected_status": 201,
    })

    assert tests[0]["body"] is not None
    assert "email" in tests[0]["body"]
    assert "@" in tests[0]["body"]["email"]


def test_json_string_body_is_parsed_into_executable_payload():
    from testforge.generation.test_generator import generate_tests

    tests = generate_tests({
        "name": "Create User",
        "method": "POST",
        "url": "https://api.example.com/users",
        "body": '{"name":"Ada","email":"ada@example.com"}',
    })

    assert tests[0]["body"] == {"name": "Ada", "email": "ada@example.com"}


def test_runner_preserves_absolute_url_and_json_body(monkeypatch):
    from testforge.execution.runner import execute_generated_tests

    captured = {}

    class Response:
        status_code = 201
        text = '{"id": 1}'

        def json(self):
            return {"id": 1}

    def fake_request(method, url, **kwargs):
        captured.update(method=method, url=url, kwargs=kwargs)
        return Response()

    monkeypatch.setattr("testforge.execution.runner.requests.request", fake_request)
    execute_generated_tests([{
        "id": "TC-URL-BODY",
        "method": "POST",
        "url": "https://user-api.example.com/users",
        "body": {"name": "Ada"},
        "assertions": ["assert response.status_code == 201"],
    }], base_url="http://localhost:8001")

    assert captured["url"] == "https://user-api.example.com/users"
    assert captured["kwargs"]["json"] == {"name": "Ada"}


def test_catalog_loader_expands_crud_methods_and_skips_na():
    from testforge.contracts.catalog_loader import expand_api_catalog

    endpoints = expand_api_catalog([{
        "id": 8,
        "name": "Swagger Petstore",
        "baseUrl": "https://petstore.swagger.io/v2",
        "resource": "/pet",
        "methods": {
            "GET": "GET /pet/{petId}",
            "POST": "POST /pet",
            "PATCH": "N/A (Petstore uses PUT)",
            "DELETE": "DELETE /pet/{petId}",
        },
    }])

    assert [endpoint["method"] for endpoint in endpoints] == ["GET", "POST", "DELETE"]
    assert endpoints[0]["url"] == "https://petstore.swagger.io/v2/pet/{petId}"
    assert endpoints[1]["expected_status"] == 201


def test_catalog_loader_uses_body_from_each_method_request():
    from testforge.contracts.catalog_loader import expand_api_catalog

    endpoints = expand_api_catalog([{
        "name": "Posts",
        "baseUrl": "https://api.example.com",
        "methods": {
            "GET": {"request": "GET /posts/1"},
            "POST": {"request": "POST /posts", "body": {"title": "foo"}},
            "PATCH": {"request": "PATCH /posts/1", "body": {"title": "updated"}},
        },
    }])

    assert endpoints[0]["body"] is None
    assert endpoints[1]["body"] == {"title": "foo"}
    assert endpoints[2]["body"] == {"title": "updated"}


def test_read_endpoints_do_not_receive_synthetic_request_bodies():
    from testforge.generation.test_generator import generate_tests

    tests = generate_tests({"name": "List users", "method": "GET", "url": "https://api.example.com/users"})

    assert all(test["body"] is None for test in tests)


def test_legacy_batch_project_ids_can_be_deleted(tmp_path):
    from importlib import import_module
    from fastapi.testclient import TestClient
    from unittest.mock import patch

    ui = import_module("testforge.ui.app")
    legacy_id = "c53abb5c5d084da7a752fa95fd3c708d"
    legacy_project = tmp_path / legacy_id
    legacy_project.mkdir()

    with patch.object(ui, "BATCH_ROOT", tmp_path):
        response = TestClient(ui.app).delete(f"/api/batch/{legacy_id}")

    assert response.status_code == 200
    assert not legacy_project.exists()


def test_config_uses_environment_specific_defaults(monkeypatch):
    from testforge.config import get_config

    monkeypatch.setenv("TESTFORGE_ENV", "qa")
    monkeypatch.setenv("TESTFORGE_BASE_URL", "https://qa.example.com")
    config = get_config()

    assert config.environment == "qa"
    assert config.base_url == "https://qa.example.com"
