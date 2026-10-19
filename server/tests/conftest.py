import re

import pytest
from fastapi.testclient import TestClient
from steadytype_server.config import Settings
from steadytype_server.db import utcnow
from steadytype_server.main import create_app
from steadytype_server.models import Attempt, Class, Enrollment, User
from steadytype_server.security import hash_password


@pytest.fixture
def app(tmp_path):
    application = create_app(Settings(
        database_url=f"sqlite:///{tmp_path / 'test.db'}", secret="test-secret"))
    with application.state.Session() as db:
        teacher = User(username="teach.one", display_name="Teacher One", role="teacher",
                       password_hash=hash_password("a long password"))
        other = User(username="teach.two", display_name="Teacher Two", role="teacher",
                     password_hash=hash_password("another password"))
        dana = User(username="prater.devin", display_name="Devin Prater", role="student")
        jane = User(username="doe.jane", display_name="Jane Doe", role="student")
        db.add_all([teacher, other, dana, jane])
        db.commit()
        morning = Class(name="Morning", teacher_id=teacher.id)
        evening = Class(name="Evening", teacher_id=other.id)
        db.add_all([morning, evening])
        db.commit()
        db.add_all([Enrollment(class_id=morning.id, student_id=dana.id),
                    Enrollment(class_id=morning.id, student_id=jane.id)])
        db.add_all([
            Attempt(id="a1", student_id=dana.id, lesson_id=3, kind="practice",
                    started_at=utcnow(), active_seconds=120, wpm=20, accuracy=95, stars=4,
                    body={"key_stats": [{"key": "p", "presses": 5, "errors": 3}]}),
            Attempt(id="a2", student_id=dana.id, lesson_id=4, kind="practice",
                    started_at=utcnow(), active_seconds=180, wpm=30, accuracy=98, stars=5,
                    body={"key_stats": [{"key": "q", "presses": 4, "errors": 1}]}),
            Attempt(id="a3", student_id=jane.id, lesson_id=3, kind="practice",
                    started_at=utcnow(), active_seconds=60, wpm=12, accuracy=85, stars=2,
                    body={}),
            Attempt(id="t1", student_id=dana.id, lesson_id=72, kind="timed_test",
                    started_at=utcnow(), active_seconds=300, wpm=55, accuracy=92,
                    errors=8, body={}),
            Attempt(id="t2", student_id=jane.id, lesson_id=72, kind="timed_test",
                    started_at=utcnow(), active_seconds=300, wpm=40, accuracy=97,
                    errors=2, body={}),
        ])
        db.commit()
        application.state.ids = {"morning": morning.id, "evening": evening.id,
                                 "dana": dana.id}
    return application


@pytest.fixture
def client(app):
    return TestClient(app)


def csrf(client, path="/signin"):
    html = client.get(path).text
    match = re.search(r'name="csrf" value="([^"]+)"', html)
    return match.group(1) if match else ""


def sign_in(client, username="teach.one", password="a long password"):
    return client.post("/signin", data={"username": username, "password": password,
                                        "csrf": csrf(client)}, follow_redirects=False)
