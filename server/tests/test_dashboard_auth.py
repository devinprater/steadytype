from conftest import csrf, sign_in


def test_unauthenticated_pages_redirect(client):
    response = client.get("/classes", follow_redirects=False)
    assert response.status_code == 303
    assert response.headers["location"] == "/signin"


def test_wrong_password_stays_on_the_page(client):
    response = client.post("/signin", data={"username": "teach.one",
                                            "password": "wrong",
                                            "csrf": csrf(client)})
    assert response.status_code == 200
    assert "do not match" in response.text


def test_a_missing_csrf_token_is_refused(client):
    response = client.post("/signin", data={"username": "teach.one",
                                            "password": "a long password",
                                            "csrf": "bogus"})
    assert "expired" in response.text


def test_teacher_sees_only_their_own_classes(client):
    assert sign_in(client).status_code == 303
    page = client.get("/classes")
    assert "Morning" in page.text
    assert "Evening" not in page.text


def test_another_teachers_class_is_forbidden(client, app):
    sign_in(client, "teach.two", "another password")
    response = client.get(f"/classes/{app.state.ids['morning']}")
    assert response.status_code == 403


def test_sign_out_requires_csrf_and_clears_the_session(client):
    sign_in(client)
    token = csrf(client, "/classes")
    client.post("/signout", data={"csrf": token})
    assert client.get("/classes", follow_redirects=False).status_code == 303
