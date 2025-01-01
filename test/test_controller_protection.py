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
    response = client.post("/versions", json={})
    assert response.status_code == 401
