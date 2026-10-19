from fastapi.testclient import TestClient
from steadytype_server.config import Settings
from steadytype_server.main import create_app


def make_client(tmp_path):
    settings = Settings(database_url=f"sqlite:///{tmp_path / 'test.db'}", secret="test")
    return TestClient(create_app(settings))


def test_healthz(tmp_path):
    client = make_client(tmp_path)
    response = client.get("/healthz")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}
