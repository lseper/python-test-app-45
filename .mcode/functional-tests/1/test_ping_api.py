import os

import pytest
import requests

BASE_URL = f"http://{os.environ.get('HOST', '127.0.0.1')}:{os.environ.get('PORT', '8000')}"


@pytest.fixture(autouse=True)
def health_check():
    resp = requests.get(f"{BASE_URL}/ping", timeout=5)
    assert resp.status_code == 200


class TestPing:
    """GET /ping"""

    def test_ping_returns_pong(self):
        resp = requests.get(f"{BASE_URL}/ping", timeout=10)
        assert resp.status_code == 200
        assert resp.json() == "pong"
        assert resp.text == '"pong"'

    def test_ping_content_type_is_json(self):
        resp = requests.get(f"{BASE_URL}/ping", timeout=10)
        assert resp.headers["content-type"].startswith("application/json")

    def test_ping_ignores_query_params(self):
        resp = requests.get(f"{BASE_URL}/ping", params={"x": "1"}, timeout=10)
        assert resp.status_code == 200
        assert resp.json() == "pong"

    def test_ping_head_not_allowed(self):
        resp = requests.head(f"{BASE_URL}/ping", timeout=10)
        assert resp.status_code == 405


class TestPingWrongMethod:
    """Non-GET methods on /ping return 405 with Allow: GET."""

    @pytest.mark.parametrize("method", ["post", "put", "delete", "patch"])
    def test_wrong_method_returns_405(self, method):
        resp = getattr(requests, method)(f"{BASE_URL}/ping", timeout=10)
        assert resp.status_code == 405
        assert resp.json() == {"detail": "Method Not Allowed"}
        assert resp.headers.get("allow") == "GET"


class TestNotFound:
    @pytest.mark.parametrize("path", ["/nope", "/ping/extra", "/", "/PING"])
    def test_unknown_route_returns_404(self, path):
        resp = requests.get(f"{BASE_URL}{path}", timeout=10)
        assert resp.status_code == 404
        assert resp.json() == {"detail": "Not Found"}

    def test_unknown_route_post_returns_404(self):
        resp = requests.post(f"{BASE_URL}/nope", json={}, timeout=10)
        assert resp.status_code == 404


class TestDocs:
    def test_docs_served(self):
        resp = requests.get(f"{BASE_URL}/docs", timeout=10)
        assert resp.status_code == 200
        assert resp.headers["content-type"].startswith("text/html")
        assert "swagger" in resp.text.lower()
        assert "/openapi.json" in resp.text

    def test_redoc_served(self):
        resp = requests.get(f"{BASE_URL}/redoc", timeout=10)
        assert resp.status_code == 200
        assert resp.headers["content-type"].startswith("text/html")

    def test_openapi_json_describes_ping(self):
        resp = requests.get(f"{BASE_URL}/openapi.json", timeout=10)
        assert resp.status_code == 200
        spec = resp.json()
        assert spec["openapi"].startswith("3.")
        assert list(spec["paths"].keys()) == ["/ping"]
        assert list(spec["paths"]["/ping"].keys()) == ["get"]
        ok = spec["paths"]["/ping"]["get"]["responses"]["200"]
        assert ok["content"]["application/json"]["schema"]["type"] == "string"
