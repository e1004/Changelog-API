from datetime import UTC, datetime
import sqlite3
from uuid import UUID, uuid4

import pytest
from realerikrani.project import Project, project_repo
from pytest_mock import MockerFixture
from e1004.changelog_api import repository
from e1004.changelog_api.repository import create_version
from e1004.changelog_api.error import ProjectNotFoundError, VersionDuplicateError


@pytest.fixture
def project_1():
    p, _ = project_repo.create_project_with_key("name", "a")
    yield p
    project_repo.delete_project(p.id)


def test_it_creates_version(project_1: Project):
    # given
    version_number = "2.3.5"
    current_time = datetime.now(UTC).date()

    # when
    result = create_version(version_number, project_1.id)

    # then
    assert isinstance(result.id, UUID)
    assert version_number == result.number
    assert project_1.id == result.project_id
    assert result.created_at == current_time
    assert result.released_at is None

def test_it_raises_error_for_missing_project():
    # given
    version_number = "2.3.5"

    # then
    with pytest.raises(ProjectNotFoundError):
        # when
        create_version(version_number, uuid4())

def test_it_creates_no_duplicate_versions(project_1: Project):
    # given
    version_number = "2.3.5"
    create_version(version_number, project_1.id)

    # then
    with pytest.raises(VersionDuplicateError):
        # when
        create_version(version_number, project_1.id)

def test_it_raises_unknown_integrity_error(mocker: MockerFixture):
    # given
    mocker_error =  sqlite3.IntegrityError()
    mocker_error.sqlite_errorname = "UNKNOWN"
    mocker.patch.object(repository, "_query", side_effect =mocker_error)

    # then
    with pytest.raises(sqlite3.IntegrityError):
        # when
        repository.create_version("1.2.3", uuid4())
