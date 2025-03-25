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
    VersionNotFoundError,
    VersionNumberInvalidError,
    VersionsReadingTokenInvalidError,
)
from e1004.changelog_api.model import Change, Version, VersionsPage

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


def test_it_reads_versions_without_request_params(
    client: FlaskClient, mocker: MockerFixture
):
    # given
    valid_number = "1.0.0"
    version = Version(date.today(), uuid4(), valid_number, uuid4(), None)
    read_versions = mocker.patch.object(
        service,
        "read_versions",
        return_value=VersionsPage([version], "any_prev", "any_next"),
    )

    # when
    response = client.get("/versions")

    # then
    assert response.status_code == 200
    assert set(response.json.keys()) == {"versions", "previous_token", "next_token"}
    assert set(response.json["versions"][0].keys()) == {
        "created_at",
        "project_id",
        "number",
        "id",
        "released_at",
    }
    assert response.json["versions"][0]["number"] == valid_number
    assert response.json["versions"][0]["created_at"] == version.created_at.isoformat()
    assert response.json["previous_token"] == "any_prev"
    assert response.json["next_token"] == "any_next"
    read_versions.assert_called_once_with(_KEY.project_id, 5, None)


def test_it_reads_versions_with_request_params(
    client: FlaskClient, mocker: MockerFixture
):
    # given
    read_versions = mocker.patch.object(
        service, "read_versions", return_value=VersionsPage([], None, None)
    )
    page_size = 7
    token = "any_token"

    # when
    response = client.get(f"/versions?page_size={page_size}&page_token={token}")

    # then
    assert response.status_code == 200
    assert response.json["previous_token"] is None
    assert response.json["next_token"] is None
    read_versions.assert_called_once_with(_KEY.project_id, page_size, token)


def test_it_returns_error_for_invalid_versions_reading(
    client: FlaskClient, mocker: MockerFixture
):
    # given
    mocker.patch.object(
        service, "read_versions", side_effect=VersionsReadingTokenInvalidError
    )

    # when
    response = client.get("/versions")

    # then
    assert response.status_code == 400


def test_it_reads_changes_for_version(client: FlaskClient, mocker: MockerFixture):
    # given
    valid_number = "1.0.0"
    change_1 = Change(uuid4(), uuid4(), "body", "fixed", "Bob")
    change_2 = Change(uuid4(), uuid4(), "body", "security", "Alice")
    read_changes = mocker.patch.object(
        service, "read_changes_for_version", return_value=[change_1, change_2]
    )

    # when
    response = client.get(f"/versions/{valid_number}/changes")

    # then
    assert response.status_code == 200
    assert set(response.json.keys()) == {"changes"}
    assert set(response.json["changes"][0].keys()) == {
        "id",
        "version_id",
        "kind",
        "body",
        "author",
    }
    read_changes.assert_called_once_with(valid_number, _KEY.project_id)


@pytest.mark.parametrize(
    ("error", "error_code"),
    [
        (VersionNotFoundError, 404),
        (VersionNumberInvalidError, 400),
    ],
)
def test_it_returns_error_for_invalid_changes_reading(
    client: FlaskClient, mocker: MockerFixture, error: Exception, error_code: int
):
    # given
    valid_number = "1.0.0"
    mocker.patch.object(service, "read_changes_for_version", side_effect=error)

    # when
    response = client.get(f"/versions/{valid_number}/changes")

    # then
    assert response.status_code == error_code
