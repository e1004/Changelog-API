import pytest
from e1004.changelog_api.app import create


@pytest.fixture
def app():
    app = create()
    app.config.update({"TESTING": True})
    return app


@pytest.fixture()
def client(app):
    return app.test_client()


def test_it_creates_version(client):
    response = client.post("/versions")
    assert response.status_code == 201
    assert set(response.json.keys()) == {"version"}
    assert response.json["version"] == "1.0.0"
