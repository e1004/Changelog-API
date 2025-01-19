import pytest
from flask import Flask
from flask.testing import FlaskClient

from e1004.changelog_api.app import create


@pytest.fixture
def app() -> Flask:
    app = create()
    app.config.update({"TESTING": True})
    return app


@pytest.fixture
def client(app: Flask) -> FlaskClient:
    return app.test_client()


def test_it_requires_auth(client: FlaskClient):
    result = {
        client.post("/versions", json={}).status_code,
        client.post("/versions/1.2.3/changes", json={}).status_code,
        client.delete("/versions/1.2.3").status_code,
    }
    assert result == {401}
