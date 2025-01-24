from uuid import uuid4

import pytest
from realerikrani.project import Project, project_repo

from e1004.changelog_api.error import VersionNotFoundError
from e1004.changelog_api.repository import (
    create_change,
    create_version,
    read_changes_for_version,
    read_next_versions,
    read_prev_versions,
    read_versions,
)


@pytest.fixture
def project_1():
    p, _ = project_repo.create_project_with_key("name", "a")
    yield p
    project_repo.delete_project(p.id)


def test_it_reads_versions(project_1: Project):
    # given
    create_version("2.3.5", project_1.id)
    create_version("2.3.6", project_1.id)
    create_version("2.4.6", project_1.id)
    create_version("1.0.0", project_1.id)
    create_version("2.0.0", project_1.id)

    # when
    result = read_versions(project_1.id, 4)

    # then
    assert [r.number for r in result] == ["2.4.6", "2.3.6", "2.3.5", "2.0.0"]


def test_it_reads_previous_versions(project_1: Project):
    # given
    create_version("2.3.5", project_1.id)
    create_version("2.3.6", project_1.id)
    create_version("2.4.6", project_1.id)
    create_version("1.0.0", project_1.id)
    create_version("2.0.0", project_1.id)

    # when
    result = read_prev_versions(project_1.id, 2, "2.0.0")

    # then
    assert [r.number for r in result] == ["2.3.6", "2.3.5"]


def test_it_reads_next_versions(project_1: Project):
    # given
    create_version("2.3.5", project_1.id)
    create_version("2.3.6", project_1.id)
    create_version("2.4.6", project_1.id)
    create_version("1.0.0", project_1.id)
    create_version("2.0.0", project_1.id)

    # when
    result = read_next_versions(project_1.id, 3, "2.4.6")

    # then
    assert [r.number for r in result] == ["2.3.6", "2.3.5", "2.0.0"]


def test_it_reads_changes_for_version(project_1: Project):
    # given
    version = create_version("1.0.1", project_1.id)
    version_2 = create_version("1.2.1", project_1.id)
    create_change(version.number, project_1.id, "added", "boody")
    create_change(version.number, project_1.id, "fixed", "body")
    create_change(version.number, project_1.id, "changed", "text")
    create_change(version.number, project_1.id, "security", "body")
    create_change(version_2.number, project_1.id, "deprecated", "body")

    # when
    result = read_changes_for_version(version.number, project_1.id)

    # then
    assert [r.kind for r in result] == ["added", "changed", "fixed", "security"]
    assert [r.body for r in result] == ["boody", "text", "body", "body"]


def test_read_changes_for_version_raises_error_for_missing_version():
    # then
    with pytest.raises(VersionNotFoundError):
        # when
        read_changes_for_version("1.2.3", uuid4())
