from datetime import date
from unittest.mock import Mock
from uuid import uuid4

import pytest
from pytest_mock import MockerFixture
from realerikrani.base64token import encode

from e1004.changelog_api import repository, service
from e1004.changelog_api.error import (
    VersionNumberInvalidError,
    VersionReleasedAtError,
    VersionsReadingTokenInvalidError,
)
from e1004.changelog_api.model import Version
from e1004.changelog_api.service import validate_released_at, validate_version_number

_VERSION_1 = Mock(autospec=Version, number="1.0.1")
_VERSION_2 = Mock(autospec=Version, number="2.0.1")
_VERSION_3 = Mock(autospec=Version)


def test_it_raises_error_for_invalid_version_number():
    # given
    number = "1.0."

    # then
    with pytest.raises(VersionNumberInvalidError):
        # when
        validate_version_number(number)


def test_it_returns_valid_version_number():
    # given
    number = "1.0.1"
    # when
    result = validate_version_number(number)
    # then
    assert result == number


def test_creates_version_calls_repository(mocker: MockerFixture):
    # given
    create_version = mocker.patch.object(repository, "create_version")
    number = "1.2.3"
    project_id = uuid4()

    # when
    result = service.create_version(number, project_id)

    # then
    create_version.assert_called_once_with(number, project_id)
    assert result == create_version.return_value


def test_delete_version_calls_repository(mocker: MockerFixture):
    # given
    delete_version = mocker.patch.object(repository, "delete_version")
    number = "1.2.3"
    project_id = uuid4()

    # when
    result = service.delete_version(number, project_id)

    # then
    delete_version.assert_called_once_with(number, project_id)
    assert result == delete_version.return_value


def test_it_raises_error_for_invalid_released_at():
    # given
    released_at = "1.0."

    # then
    with pytest.raises(VersionReleasedAtError):
        # when
        validate_released_at(released_at)


def test_release_version_calls_repository(mocker: MockerFixture):
    # given
    release_version = mocker.patch.object(repository, "release_version")
    number = "1.2.3"
    project_id = uuid4()
    released_date = date.today()

    # when
    result = service.release_version(number, project_id, str(released_date.isoformat()))

    # then
    release_version.assert_called_once_with(number, project_id, released_date)
    assert result == release_version.return_value


def test_it_reads_no_versions(mocker: MockerFixture):
    # given
    project_id = uuid4()
    page_size = 3
    read_versions = mocker.patch.object(repository, "read_versions", return_value=[])

    # when
    result = service.read_versions(project_id, page_size, None)

    # then
    assert result.next_token is None
    assert result.prev_token is None
    assert result.versions == []
    read_versions.assert_called_once_with(project_id, page_size + 1)


def test_it_reads_versions_with_next_page_without_token(mocker: MockerFixture):
    # given
    project_id = uuid4()
    page_size = 1
    mocker.patch.object(
        repository, "read_versions", return_value=[_VERSION_1, _VERSION_2]
    )
    read_prev_versions = mocker.patch.object(
        repository, "read_prev_versions", return_value=[]
    )

    # when
    result = service.read_versions(project_id, page_size, None)

    # then
    assert result.next_token == encode(
        [("version_number", _VERSION_1.number), ("direction", "next")]
    )
    assert result.prev_token is None
    assert result.versions == [_VERSION_1]
    read_prev_versions.assert_called_once_with(project_id, 1, _VERSION_1.number)


def test_it_reads_versions_with_next_page_previous_direction(mocker: MockerFixture):
    # given
    project_id = uuid4()
    page_size = 1
    token = encode([("version_number", ""), ("direction", "previous")])

    mocker.patch.object(repository, "read_prev_versions", return_value=[_VERSION_1])
    mocker.patch.object(repository, "read_next_versions", return_value=[_VERSION_3])

    # when
    result = service.read_versions(project_id, page_size, token)

    # then
    assert result.next_token == encode(
        [("version_number", _VERSION_1.number), ("direction", "next")]
    )
    assert result.prev_token is None
    assert result.versions == [_VERSION_1]


def test_it_reads_versions_with_next_and_prev_page_without_token(mocker: MockerFixture):
    # given
    project_id = uuid4()
    page_size = 1
    mocker.patch.object(
        repository, "read_versions", return_value=[_VERSION_1, _VERSION_2]
    )
    read_prev_versions = mocker.patch.object(
        repository, "read_prev_versions", return_value=[_VERSION_3]
    )

    # when
    result = service.read_versions(project_id, page_size, None)

    # then
    assert result.next_token == encode(
        [("version_number", _VERSION_1.number), ("direction", "next")]
    )
    assert result.prev_token == encode(
        [("version_number", _VERSION_1.number), ("direction", "previous")]
    )
    assert result.versions == [_VERSION_1]
    read_prev_versions.assert_called_once_with(project_id, 1, _VERSION_1.number)


def test_it_raises_error_for_unexpected_direction():
    # given
    project_id = uuid4()
    page_size = 3
    token = encode([("version_number", ""), ("direction", "")])

    # then
    with pytest.raises(VersionsReadingTokenInvalidError):
        # when
        service.read_versions(project_id, page_size, token)


def test_it_raises_error_for_invalid_token():
    # given
    project_id = uuid4()
    page_size = 3
    token = ""

    # then
    with pytest.raises(VersionsReadingTokenInvalidError):
        # when
        service.read_versions(project_id, page_size, token)


@pytest.mark.parametrize(
    "token", [encode([("direction", "next")]), encode([("version_number", "")])]
)
def test_it_raises_error_for_missing_token_fields(token: str):
    # given
    project_id = uuid4()
    page_size = 3

    # then
    with pytest.raises(VersionsReadingTokenInvalidError):
        # when
        service.read_versions(project_id, page_size, token)


def test_it_reads_versions_with_no_previous_versions(mocker: MockerFixture):
    # given
    project_id = uuid4()
    page_size = 1
    token = encode([("version_number", ""), ("direction", "next")])

    mocker.patch.object(repository, "read_prev_versions", return_value=[])
    mocker.patch.object(repository, "read_next_versions", return_value=[_VERSION_1])

    # when
    result = service.read_versions(project_id, page_size, token)

    # then
    assert result.next_token is None
    assert result.versions == [_VERSION_1]


def test_it_reads_versions_with_previous_direction(mocker: MockerFixture):
    # given
    project_id = uuid4()
    page_size = 1
    token = encode([("version_number", ""), ("direction", "previous")])

    mocker.patch.object(
        repository, "read_prev_versions", return_value=[_VERSION_1, _VERSION_2]
    )
    mocker.patch.object(repository, "read_next_versions", return_value=[])

    # when
    result = service.read_versions(project_id, page_size, token)

    # then
    assert result.next_token is None
    assert result.prev_token == encode(
        [("version_number", _VERSION_2.number), ("direction", "previous")]
    )
    assert result.versions == [_VERSION_2]
