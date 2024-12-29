from datetime import UTC, datetime
from uuid import uuid4

import pytest
from flask import Flask
from flask.testing import FlaskClient
from pytest_mock import MockerFixture

from e1004.changelog_api import service
from e1004.changelog_api.app import create
from e1004.changelog_api.model import Version


@pytest.fixture
def app() -> Flask:
    app = create()
    app.config.update({"TESTING": True})
    return app


@pytest.fixture
def client(app: Flask) -> FlaskClient:
    return app.test_client()


def test_it_creates_version(client: FlaskClient, mocker: MockerFixture):
    # given
    valid_number = "1.0.0"
    version = Version(datetime.now(tz=UTC), uuid4(), valid_number, uuid4(), None)
    create_version = mocker.patch.object(
        service, "create_version", return_value=version
    )

    # when
    response = client.post("/versions")

    # then
    assert response.status_code == 201
    assert set(response.json.keys()) == {"version"}
    assert set(response.json["version"].keys()) == {
        "created_at",
        "project_id",
        "number",
        "id",
        "released_at",
    }
    assert response.json["version"]["number"] == valid_number
    create_version.assert_called_once_with(valid_number)
