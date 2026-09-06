def test_root_endpoint(client):
    """Test the root welcome endpoint."""
    response = client.get("/")
    assert response.status_code == 200
    payload = response.json()
    assert "MindOS" in payload["message"]
    assert payload["version"] == "0.1.0"
    assert "health" in payload


def test_api_v1_health_endpoint(client):
    """Test the /api/v1/health endpoint returns 200 and expected payload structure."""
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert data["app"] == "MindOS"
    assert data["version"] == "0.1.0"
    assert data["environment"] in ["development", "production", "test"]
    assert "database" in data
    assert "status" in data["database"]
    assert data["database"]["database"] == "postgresql"


def test_root_health_endpoint(client):
    """Test the /health alias endpoint returns 200."""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"


def test_openapi_docs_accessible(client):
    """Verify OpenAPI schema is served correctly under /api/v1/openapi.json."""
    response = client.get("/api/v1/openapi.json")
    assert response.status_code == 200
    schema = response.json()
    assert schema["info"]["title"] == "MindOS"
