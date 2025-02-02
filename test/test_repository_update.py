from datetime import date
from uuid import uuid4

import pytest
from realerikrani.project import Project, project_repo

from e1004.changelog_api.error import (
    VersionCannotBeReleasedError,
    VersionNotFoundError,
    VersionReleasedError,
)
from e1004.changelog_api.repository import (
    create_change,
    create_version,
    move_change_to_other_version,
    release_version,
)


@pytest.fixture
def project_1():
    p, _ = project_repo.create_project_with_key("name", "a")
    yield p
    project_repo.delete_project(p.id)


def test_it_releases_version(project_1: Project):
    # given
    version_number = "2.3.5"
    create_version(version_number, project_1.id)
    released_date = date.today()

    # when
    result = release_version(version_number, project_1.id, released_date)

    # then
    assert result.released_at == released_date


def test_it_raises_error_for_missing_version():
    # given
    version_number = "2.3.5"

    # then
    with pytest.raises(VersionNotFoundError):
        # when
        release_version(version_number, uuid4(), date.today())


def test_it_has_already_released_version(project_1: Project):
    # given
    version_number = "2.3.5"
    create_version(version_number, project_1.id)
    released_date = date.today()
    release_version(version_number, project_1.id, released_date)

    # then
    with pytest.raises(VersionCannotBeReleasedError):
        # when
        release_version(version_number, project_1.id, released_date)


def test_it_moves_change_to_other_version(project_1: Project):
    # given
    version_number_1 = "1.3.5"
    create_version(version_number_1, project_1.id)
    version_number_2 = "2.3.5"
    target_version = create_version(version_number_2, project_1.id)
    change = create_change(version_number_1, project_1.id, "added", "body", "Bob")

    # when
    result = move_change_to_other_version(
        version_number_1, version_number_2, project_1.id, change.id
    )

    # then
    assert result.version_id == target_version.id
    assert result.id == change.id


def test_it_moves_no_change_to_released_version(project_1: Project):
    # given
    version_number_1 = "1.3.5"
    create_version(version_number_1, project_1.id)
    version_number_2 = "2.3.5"
    create_version(version_number_2, project_1.id)
    release_version(version_number_2, project_1.id, date.today())
    change = create_change(version_number_1, project_1.id, "added", "body", "Bob")

    # then
    with pytest.raises(VersionReleasedError):
        # when
        move_change_to_other_version(
            version_number_1, version_number_2, project_1.id, change.id
        )


def test_it_moves_no_released_version_change_to_other_version(project_1: Project):
    # given
    version_number_1 = "1.3.5"
    create_version(version_number_1, project_1.id)
    version_number_2 = "2.3.5"
    create_version(version_number_2, project_1.id)
    release_version(version_number_1, project_1.id, date.today())
    change = create_change(version_number_1, project_1.id, "added", "body", "Bob")

    # then
    with pytest.raises(VersionReleasedError):
        # when
        move_change_to_other_version(
            version_number_1, version_number_2, project_1.id, change.id
        )
