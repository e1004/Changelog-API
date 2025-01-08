import pytest
from realerikrani.project import Project, project_repo

from e1004.changelog_api.repository import (
    create_version,
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
