from testforge.parsers.curl_parser import parse_curl


def test_parse_curl_extracts_method_url_headers_and_body():
    curl = """curl --location 'https://example.com/api/users' \
    --header 'Authorization: Bearer token-123' \
    --header 'Content-Type: application/json' \
    --data '{\"name\":\"Lokesh\",\"email\":\"lokesh@example.com\"}'"""

    api_spec = parse_curl(curl)

    assert api_spec.method == "POST"
    assert api_spec.url == "https://example.com/api/users"
    assert api_spec.headers["Authorization"] == "Bearer token-123"
    assert api_spec.headers["Content-Type"] == "application/json"
    assert api_spec.body == {"name": "Lokesh", "email": "lokesh@example.com"}


def test_parse_curl_for_get_request_without_body():
    curl = "curl 'https://example.com/api/users?active=true'"

    api_spec = parse_curl(curl)

    assert api_spec.method == "GET"
    assert api_spec.url == "https://example.com/api/users?active=true"
    assert api_spec.body is None
