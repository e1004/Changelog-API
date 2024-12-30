import os
import sqlite3
from contextlib import closing
from datetime import UTC, datetime
from uuid import UUID

import pytest
from realerikrani.project import Project, project_repo

from e1004.changelog_api.repository import create_version


@pytest.fixture
def project_1():
    p, _ = project_repo.create_project_with_key("name", "a")
    yield p
    project_repo.delete_project(p.id)


@pytest.fixture
def clean_db():
    with closing(
        sqlite3.connect(os.environ["PROJECT_DATABASE_PATH"], uri=True, autocommit=True)
    ):
        yield


@pytest.mark.usefixtures("clean_db")
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
