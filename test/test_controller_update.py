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
    VersionCannotBeReleasedError,
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


def test_it_releases_version(client: FlaskClient, mocker: MockerFixture):
    # given
    version_number = "1.0.0"
    version = Version(
        date.today(), uuid4(), version_number, uuid4(), date(2000, 12, 24)
    )
    release_version = mocker.patch.object(
        service, "release_version", return_value=version
    )

    # when
    response = client.patch(
        f"/versions/{version_number}", json={"released_at": "2000-12-24"}
    )

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
    assert response.json["version"]["released_at"] == "2000-12-24"
    release_version.assert_called_once_with(
        version_number, _KEY.project_id, "2000-12-24"
    )


def test_it_returns_400_for_released_version(
    client: FlaskClient, mocker: MockerFixture
):
    # given
    valid_number = "1.0.0"
    mocker.patch.object(
        service, "release_version", side_effect=VersionCannotBeReleasedError
    )

    # when
    response = client.patch(f"/versions/{valid_number}", json={"released_at": ""})

    # then
    assert response.status_code == 400
    assert response.json["errors"][0]["code"] == "RESOURCE_PERMANENT"
    assert response.json["errors"][0]["message"] == "version is released"


def test_it_returns_400_for_invalid_version(client: FlaskClient):
    # when
    response = client.patch("/versions/uuu", json={"released_at": ""})

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
    mocker.patch.object(service, "release_version", side_effect=VersionNotFoundError)

    # when
    response = client.patch(f"/versions/{valid_number}", json={"released_at": ""})

    # then
    assert response.status_code == 404
    assert response.json["errors"][0]["code"] == "RESOURCE_MISSING"
    assert response.json["errors"][0]["message"] == "version missing"


def test_it_requires_valid_released_at(client: FlaskClient):
    # when
    response = client.patch("/versions/1.2.3", json={"released_at": ""})

    # then
    assert response.status_code == 400
    assert response.json["errors"][0]["code"] == "VALUE_INVALID"
    assert response.json["errors"][0]["message"] == "invalid released at"


def test_it_requires_released_at(client: FlaskClient):
    # when
    response = client.patch("/versions/1.2.3", json={"abc": ""})

    # then
    assert response.status_code == 400
    assert response.json["errors"][0]["code"] == "VALUE_MISSING"
    assert response.json["errors"][0]["message"] == "released at missing"


def test_it_moves_change_to_other_version(client: FlaskClient, mocker: MockerFixture):
    # given
    version_number_1 = "1.0.0"
    version_number_2 = "2.0.0"
    change = Change(uuid4(), uuid4(), "body", "fixed")
    move_change = mocker.patch.object(
        service, "move_change_to_other_version", return_value=change
    )

    # when
    response = client.patch(
        f"/versions/{version_number_1}/changes/{change.id}",
        json={"version_number": version_number_2},
    )

    # then
    assert response.status_code == 200
    assert set(response.json.keys()) == {"change"}
    assert set(response.json["change"].keys()) == {
        "id",
        "version_id",
        "kind",
        "body",
    }
    move_change.assert_called_once_with(
        version_number_1, version_number_2, _KEY.project_id, change.id
    )


def test_moving_change_requires_target_version_number(client: FlaskClient):
    # when
    response = client.patch(f"/versions/1.2.3/changes/{uuid4()}", json={"": ""})

    # then
    assert response.status_code == 400
    assert response.json["errors"][0]["code"] == "VALUE_MISSING"
    assert response.json["errors"][0]["message"] == "version number missing"


@pytest.mark.parametrize(
    ("error", "error_code"),
    [
        (VersionNotFoundError, 404),
        (VersionReleasedError, 400),
        (ChangeNotFoundError, 404),
        (VersionNumberInvalidError, 400),
    ],
)
def test_it_returns_error_for_invalid_change_moving(
    client: FlaskClient, mocker: MockerFixture, error: Exception, error_code: int
):
    # given
    valid_number = "1.0.0"
    mocker.patch.object(service, "move_change_to_other_version", side_effect=error)

    # when
    response = client.patch(
        f"/versions/{valid_number}/changes/{uuid4()}",
        json={"version_number": valid_number},
    )

    # then
    assert response.status_code == error_code
