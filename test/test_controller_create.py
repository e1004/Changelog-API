from datetime import date
from unittest.mock import Mock
from uuid import uuid4

import pytest
from flask import Flask
from flask.testing import FlaskClient
from pytest_mock import MockerFixture
from realerikrani.project import PublicKey, bearer_extractor

from e1004.changelog_api import service
from e1004.changelog_api.app import create
from e1004.changelog_api.model import Version

_KEY = Mock(autospec=PublicKey)


@pytest.fixture
def app() -> Flask:
    app = create()
    app.config.update({"TESTING": True})
    return app


@pytest.fixture
def client(app: Flask) -> FlaskClient:
    return app.test_client()


@pytest.fixture(autouse=True)
def protect(mocker: MockerFixture):
    mocker.patch.object(bearer_extractor, "protect", return_value=_KEY)


def test_it_creates_version(client: FlaskClient, mocker: MockerFixture):
    # given
    valid_number = "1.0.0"
    version = Version(date.today(), uuid4(), valid_number, uuid4(), None)
    create_version = mocker.patch.object(
        service, "create_version", return_value=version
    )

    # when
    response = client.post("/versions", json={"version_number": valid_number})

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
    assert response.json["version"]["created_at"] == version.created_at.isoformat()
    create_version.assert_called_once_with(valid_number, _KEY.project_id)


def test_it_requires_version_number(client: FlaskClient):
    # when
    response = client.post("/versions", json={})

    # then
    assert response.status_code == 400
    assert response.json["errors"][0]["code"] == "VALUE_MISSING"
    assert response.json["errors"][0]["message"] == "version number missing"
