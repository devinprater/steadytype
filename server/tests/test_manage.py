import re

from conftest import csrf, sign_in


def test_a_teacher_creates_a_class_and_adds_a_student(client):
    sign_in(client)
    token = csrf(client, "/classes/new")
    created = client.post("/classes/new", data={"name": "Afternoon", "csrf": token},
                          follow_redirects=False)
    assert created.status_code == 303
    page = client.get("/classes")
    assert "Afternoon" in page.text

    class_id = int(re.search(r'/classes/(\d+)"', page.text.replace('href="/classes/new"', "")).group(1))
    token = csrf(client, f"/classes/{class_id}")
    added = client.post(f"/classes/{class_id}/students",
                        data={"username": "smith.ana", "display_name": "Ana Smith",
                              "csrf": token}, follow_redirects=False)
    assert added.status_code == 303
    assert "Ana Smith" in client.get(f"/classes/{class_id}").text

    again = client.post(f"/classes/{class_id}/students",
                        data={"username": "smith.ana", "csrf": token},
                        follow_redirects=False)
    assert again.status_code == 303
