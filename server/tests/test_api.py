from datetime import timedelta

from conftest import sign_in  # noqa: F401
from steadytype_server.db import utcnow
from steadytype_server.models import Device, User
from steadytype_server.security import token_hash


def student_token(client, username="prater.devin"):
    response = client.post("/api/v1/auth/student", json={"username": username})
    assert response.status_code == 200, response.text
    return response.json()["token"]


def test_student_sign_in_issues_a_token(client):
    token = student_token(client)
    me = client.get("/api/v1/me", headers={"Authorization": f"Bearer {token}"})
    assert me.status_code == 200
    assert me.json()["username"] == "prater.devin"


def test_unknown_student_is_refused(client):
    response = client.post("/api/v1/auth/student", json={"username": "nobody.here"})
    assert response.status_code == 404


def test_staff_need_the_password(client):
    bad = client.post("/api/v1/auth/staff",
                      json={"username": "teach.one", "password": "wrong"})
    assert bad.status_code == 401
    good = client.post("/api/v1/auth/staff",
                       json={"username": "teach.one", "password": "a long password"})
    assert good.status_code == 200


def test_expired_token_is_refused(client, app):
    token = student_token(client)
    with app.state.Session() as db:
        device = db.query(Device).filter(Device.token_hash == token_hash(token)).first()
        device.expires_at = utcnow() - timedelta(days=1)
        db.commit()
    response = client.get("/api/v1/me", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 401


def test_disabled_account_is_refused(client, app):
    token = student_token(client)
    with app.state.Session() as db:
        user = db.query(User).filter(User.username == "prater.devin").first()
        user.disabled_at = utcnow()
        db.commit()
    response = client.get("/api/v1/me", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 401


def test_attempts_are_idempotent(client):
    token = student_token(client)
    payload = [{"id": "11111111-1111-1111-1111-111111111111", "lesson_id": 3,
                "kind": "practice", "started_at": "2026-10-19T14:00:00",
                "active_seconds": 120, "wpm": 20, "accuracy": 95, "stars": 4,
                "key_stats": [{"key": "p", "presses": 5, "errors": 2}]}]
    headers = {"Authorization": f"Bearer {token}"}
    first = client.post("/api/v1/attempts", json=payload, headers=headers)
    second = client.post("/api/v1/attempts", json=payload, headers=headers)
    assert first.json() == {"accepted": 1, "ignored": 0}
    assert second.json() == {"accepted": 0, "ignored": 1}


def test_uploads_need_a_token(client):
    response = client.post("/api/v1/attempts", json=[])
    assert response.status_code == 401


def test_course_comes_from_the_content_directory(client):
    token = student_token(client)
    response = client.get("/api/v1/course", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    assert response.json()["lessons"][0]["id"] == 1
