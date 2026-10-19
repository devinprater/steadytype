from fastapi.testclient import TestClient
from steadytype_server.config import Settings
from steadytype_server.main import create_app
from steadytype_server.setup import create_admin


def test_admin_can_sign_in_after_setup(tmp_path):
    settings = Settings(database_url=f"sqlite:///{tmp_path / 'setup.db'}", secret="test")
    create_admin(settings, "Owner", "a long admin password", "Owner")
    client = TestClient(create_app(settings))
    response = client.post("/api/v1/auth/staff",
                           json={"username": "owner", "password": "a long admin password"})
    assert response.status_code == 200
    assert response.json()["user"]["role"] == "admin"
