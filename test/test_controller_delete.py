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
    ChangeNotFoundError,
    VersionCannotBeDeletedError,
    VersionNotFoundError,
    VersionNumberInvalidError,
    VersionReleasedError,
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


def test_it_deletes_version(client: FlaskClient, mocker: MockerFixture):
    # given
    valid_number = "1.0.0"
    version = Version(date.today(), uuid4(), valid_number, uuid4(), None)
    delete_version = mocker.patch.object(
        service, "delete_version", return_value=version
    )

    # when
    response = client.delete(f"/versions/{valid_number}")

    # then
    assert response.status_code == 200
    assert set(response.json.keys()) == {"version"}
    assert set(response.json["version"].keys()) == {
        "created_at",
        "project_id",
        "number",
        "id",
        "released_at",
    }
    delete_version.assert_called_once_with(valid_number, _KEY.project_id)


def test_it_returns_400_for_released_version(
    client: FlaskClient, mocker: MockerFixture
):
    # given
    valid_number = "1.0.0"
    mocker.patch.object(
        service, "delete_version", side_effect=VersionCannotBeDeletedError
    )

    # when
    response = client.delete(f"/versions/{valid_number}")

    # then
    assert response.status_code == 400
    assert response.json["errors"][0]["code"] == "RESOURCE_PERMANENT"
    assert response.json["errors"][0]["message"] == "version is released"


def test_it_returns_400_for_invalid_version(client: FlaskClient):
    # when
    response = client.delete("/versions/uuu")

    # then
    assert response.status_code == 400
    assert response.json["errors"][0]["code"] == "VALUE_INVALID"
    assert (
        response.json["errors"][0]["message"]
        == "version number must use integers in 'major.minor.patch'"
    )


def test_it_returns_404_for_missing_version(client: FlaskClient, mocker: MockerFixture):
    # given
    valid_number = "1.0.0"
    mocker.patch.object(service, "delete_version", side_effect=VersionNotFoundError)

    # when
    response = client.delete(f"/versions/{valid_number}")

    # then
    assert response.status_code == 404
    assert response.json["errors"][0]["code"] == "RESOURCE_MISSING"
    assert response.json["errors"][0]["message"] == "version missing"


def test_it_deletes_change(client: FlaskClient, mocker: MockerFixture):
    # given
    valid_number = "1.0.0"
    change = Change(uuid4(), uuid4(), "body", "added", "Bob")
    delete_change = mocker.patch.object(service, "delete_change", return_value=change)

    # when
    response = client.delete(f"/versions/{valid_number}/changes/{change.id}")

    # then
    assert response.status_code == 200
    assert set(response.json.keys()) == {"change"}
    assert set(response.json["change"].keys()) == {
        "id",
        "version_id",
        "body",
        "kind",
        "author",
    }
    delete_change.assert_called_once_with(valid_number, change.id, _KEY.project_id)


@pytest.mark.parametrize(
    ("error", "error_code"),
    [
        (VersionNotFoundError, 404),
        (VersionReleasedError, 400),
        (ChangeNotFoundError, 404),
        (VersionNumberInvalidError, 400),
    ],
)
def test_it_returns_error_for_invalid_change_deletion(
    client: FlaskClient, mocker: MockerFixture, error: Exception, error_code: int
):
    # given
    valid_number = "1.0.0"
    mocker.patch.object(service, "delete_change", side_effect=error)

    # when
    response = client.delete(f"/versions/{valid_number}/changes/{uuid4()}")

    # then
    assert response.status_code == error_code
