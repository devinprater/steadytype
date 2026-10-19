from steadytype_client.sync import SyncClient, remote_token


class Response:
    def __init__(self, payload, status=200):
        self._payload, self.status_code = payload, status

    def json(self):
        return self._payload

    def raise_for_status(self):
        if self.status_code >= 400:
            raise __import__("httpx").HTTPStatusError("bad", request=None, response=None)


class Client:
    def __init__(self, payload):
        self.payload, self.calls = payload, []

    def post(self, url, json=None, headers=None, timeout=None):
        self.calls.append((url, json, headers))
        return Response(self.payload)


def test_upload_sends_the_bearer_token_and_returns_the_count():
    fake = Client({"accepted": 2, "ignored": 0})
    sync = SyncClient("https://school.test/", "abc", client=fake)
    accepted = sync.upload([{"id": "a1"}, {"id": "a2"}])
    assert accepted == 2
    url, body, headers = fake.calls[0]
    assert url == "https://school.test/api/v1/attempts"
    assert headers == {"Authorization": "Bearer abc"}
    assert len(body) == 2


def test_nothing_to_upload_makes_no_request():
    fake = Client({"accepted": 0})
    assert SyncClient("https://school.test", "abc", client=fake).upload([]) == 0
    assert fake.calls == []


def test_a_student_token_is_fetched_by_username():
    fake = Client({"token": "tok"})
    assert remote_token("https://school.test", "prater.devin", client=fake) == "tok"
    assert fake.calls[0][0] == "https://school.test/api/v1/auth/student"
    assert fake.calls[0][1] == {"username": "prater.devin"}


def test_an_unreachable_server_returns_no_token():
    class Broken:
        def post(self, *args, **kwargs):
            raise __import__("httpx").ConnectError("no route")

    assert remote_token("https://school.test", "prater.devin", client=Broken()) is None
