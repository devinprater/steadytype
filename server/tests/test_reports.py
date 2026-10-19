from conftest import csrf, sign_in


def test_the_goal_can_be_changed_and_is_audited(client, app):
    sign_in(client)
    class_id = app.state.ids["morning"]
    page = client.get(f"/classes/{class_id}/settings")
    assert page.status_code == 200
    token = csrf(client, f"/classes/{class_id}/settings")
    saved = client.post(f"/classes/{class_id}/settings",
                        data={"goal_minutes": "25", "csrf": token})
    assert "Saved." in saved.text
    assert "25 minutes" in client.get(f"/classes/{class_id}").text
    audit = client.get(f"/classes/{class_id}/audit")
    assert "class.goal" in audit.text
    assert "25 minutes a day" in audit.text


def test_a_goal_of_zero_means_no_goal(client, app):
    sign_in(client)
    class_id = app.state.ids["morning"]
    token = csrf(client, f"/classes/{class_id}/settings")
    client.post(f"/classes/{class_id}/settings",
                data={"goal_minutes": "0", "csrf": token})
    assert "Daily goal:  none" in client.get(f"/classes/{class_id}").text


def test_certification_shows_who_meets_the_requirement(client, app):
    sign_in(client)
    page = client.get(f"/classes/{app.state.ids['morning']}/certification")
    assert page.status_code == 200
    assert "Meets the requirement" in page.text
    assert "Not yet" in page.text
    assert "approved tester" in page.text
    assert "55" in page.text


def test_creating_a_class_is_audited(client, app):
    from steadytype_server.models import Class

    sign_in(client)
    token = csrf(client, "/classes/new")
    client.post("/classes/new", data={"name": "Evening Two", "csrf": token})
    with app.state.Session() as db:
        class_id = db.query(Class).filter(Class.name == "Evening Two").one().id
    assert "class.create" in client.get(f"/classes/{class_id}/audit").text
