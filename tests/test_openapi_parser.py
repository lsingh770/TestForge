from testforge.contracts.openapi_loader import parse_openapi_document


def test_parse_openapi_document_extracts_endpoint_metadata():
    spec = {
        "paths": {
            "/users": {
                "post": {
                    "summary": "Create user",
                    "operationId": "createUser",
                    "parameters": [{"name": "tenant", "in": "header"}],
                    "requestBody": {"required": True},
                }
            },
            "/users/{id}": {
                "get": {
                    "summary": "Fetch user",
                    "operationId": "getUser",
                }
            },
        }
    }

    endpoints = parse_openapi_document(spec)

    assert len(endpoints) == 2
    assert endpoints[0]["method"] == "POST"
    assert endpoints[0]["path"] == "/users"
    assert endpoints[1]["method"] == "GET"
    assert endpoints[1]["path"] == "/users/{id}"
