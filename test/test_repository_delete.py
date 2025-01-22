from datetime import date
from uuid import uuid4

import pytest
from realerikrani.project import Project, project_repo

from e1004.changelog_api.error import (
    VersionCannotBeDeletedError,
    VersionNotFoundError,
)
from e1004.changelog_api.repository import (
    create_change,
    create_version,
    delete_change,
    delete_version,
    release_version,
)


@pytest.fixture
def project_1():
    p, _ = project_repo.create_project_with_key("name", "a")
    yield p
    project_repo.delete_project(p.id)


def test_it_deletes_version(project_1: Project):
    # given
    version_number = "2.3.5"
    version = create_version(version_number, project_1.id)

    # when
    result = delete_version(version_number, project_1.id)

    # then
    assert result == version


def test_it_raises_error_for_missing_version():
    # given
    version_number = "2.3.5"

    # then
    with pytest.raises(VersionNotFoundError):
        # when
        delete_version(version_number, uuid4())


def test_it_raises_error_for_released_version(project_1: Project):
    # given
    version_number = "2.3.5"
    create_version(version_number, project_1.id)
    release_version(version_number, project_1.id, date.today())

    # then
    with pytest.raises(VersionCannotBeDeletedError):
        # when
        delete_version(version_number, project_1.id)


def test_it_deletes_change(project_1: Project):
    # given
    version_number = "2.3.5"
    create_version(version_number, project_1.id)
    change = create_change(version_number, project_1.id, "added", "aaaa")

    # when
    result = delete_change(version_number, change.id, project_1.id)

    # then
    assert result == change


def test_deleting_change_raises_error_for_missing_change():
    with pytest.raises(VersionNotFoundError):
        # when
        delete_change("2.3.5", uuid4(), uuid4())
