import os
import sqlite3
from datetime import UTC, datetime
from functools import partial
from uuid import UUID, uuid4

from realerikrani.sopenqlite import query

from .db import CREATE_TABLES
from .error import VersionNotFoundError
from .model import Version

_query = partial(
    query,
    CREATE_TABLES,
    os.environ["PROJECT_DATABASE_PATH"],
    [],
)


def to_version(row: sqlite3.Row | None) -> Version:
    if row is None:
        raise VersionNotFoundError
    number = f'{row["major"]}.{row["minor"]}.{row["patch"]}'
    return Version(
        id=UUID(row["id"]),
        number=number,
        project_id=UUID(row["project_id"]),
        created_at=datetime.fromtimestamp(row["created_at"], UTC).date(),
        released_at=(
            datetime.fromtimestamp(row["released_at"], UTC).date()
            if row["released_at"] is not None
            else None
        ),
    )


def create_version(version: str, project_id: UUID) -> Version:
    q = """INSERT INTO version(project_id, major, minor, patch, id, created_at)
    VALUES (?,?,?,?,?,?) RETURNING *"""
    time = (
        datetime.now(UTC).replace(hour=0, minute=0, second=0, microsecond=0).timestamp()
    )
    args = str(project_id), *map(int, version.split(".")), str(uuid4()), time

    return to_version(_query(lambda c: c.execute(q, args).fetchone()))
