from uuid import uuid4

import pytest
from pytest_mock import MockerFixture

from e1004.changelog_api import repository, service
from e1004.changelog_api.error import VersionNumberInvalidError
from e1004.changelog_api.service import validate_version_number


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
