from conftest import sign_in


def test_class_page_lists_students_and_numbers(client, app):
    sign_in(client)
    page = client.get(f"/classes/{app.state.ids['morning']}")
    assert page.status_code == 200
    assert "Devin Prater" in page.text
    assert "Jane Doe" in page.text
    assert "Words per minute" in page.text
    assert "Students in Morning" in page.text


def test_csv_has_a_header_and_one_row_per_student(client, app):
    sign_in(client)
    response = client.get(f"/classes/{app.state.ids['morning']}/export.csv")
    lines = response.text.strip().splitlines()
    assert lines[0].startswith("username,display_name,lessons")
    assert len(lines) == 3
    assert any("prater.devin" in line for line in lines)


def test_student_page_shows_weak_keys(client, app):
    sign_in(client)
    page = client.get(
        f"/classes/{app.state.ids['morning']}/students/{app.state.ids['dana']}")
    assert "Keys to practise" in page.text
    assert "prater.devin" in page.text
