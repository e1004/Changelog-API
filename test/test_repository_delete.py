from uuid import uuid4

import pytest
from realerikrani.project import Project, project_repo

from e1004.changelog_api.error import VersionNotFoundError
from e1004.changelog_api.repository import create_version, delete_version


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
