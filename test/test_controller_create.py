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
from e1004.changelog_api.error import (
    ChangeBodyInvalidError,
    ChangeKindInvalidError,
    VersionNumberInvalidError,
)
from e1004.changelog_api.model import Change, Version

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


def test_it_requires_valid_version_number(client: FlaskClient):
    # when
    response = client.post("/versions", json={"version_number": ""})

    # then
    assert response.status_code == 400
    assert response.json["errors"][0]["code"] == "VALUE_INVALID"
    assert (
        response.json["errors"][0]["message"]
        == "version number must use integers in 'major.minor.patch'"
    )


def test_create_change_requires_kind_and_body(client: FlaskClient):
    # when
    response = client.post("/versions/1.2.4/changes", json={})

    # then
    assert response.status_code == 400
    assert len(response.json["errors"]) == 2
    assert response.json["errors"][0]["code"] == "VALUE_MISSING"
    assert response.json["errors"][1]["code"] == "VALUE_MISSING"
    assert "kind" in response.json["errors"][0]["message"]
    assert "body" in response.json["errors"][1]["message"]


def test_it_creates_change(client: FlaskClient, mocker: MockerFixture):
    # given
    change = Change(uuid4(), "1.2.3", "aaa", "changed")
    create_change = mocker.patch.object(service, "create_change", return_value=change)

    # when
    response = client.post(
        "/versions/1.2.3/changes", json={"kind": change.kind, "body": change.body}
    )

    # then
    assert response.status_code == 201
    create_change.assert_called_once_with(
        "1.2.3", _KEY.project_id, change.kind, change.body
    )
    assert set(response.json.keys()) == {"change"}
    assert set(response.json["change"].keys()) == {"version_id", "id", "kind", "body"}
    assert response.json["change"]["kind"] == change.kind
    assert response.json["change"]["body"] == change.body


@pytest.mark.parametrize(
    "error", [ChangeKindInvalidError, ChangeBodyInvalidError, VersionNumberInvalidError]
)
def test_it_creates_no_change_for_invalid_input(
    client: FlaskClient, mocker: MockerFixture, error: Exception
):
    # given
    mocker.patch.object(service, "create_change", side_effect=error)

    # when
    response = client.post(
        "/versions/1.2.3/changes", json={"kind": "security", "body": "change"}
    )

    # then
    assert response.status_code == 400
    assert set(response.json.keys()) == {"errors"}
    assert len(response.json["errors"]) == 1
