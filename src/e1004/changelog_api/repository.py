import os
import sqlite3
from datetime import UTC, date, datetime
from functools import partial
from uuid import UUID, uuid4

from realerikrani.sopenqlite import query

from .db import CREATE_TABLES
from .error import (
    ProjectNotFoundError,
    VersionCannotBeDeletedError,
    VersionCannotBeReleasedError,
    VersionDuplicateError,
    VersionNotFoundError,
)
from .model import Version

_query = partial(
    query,
    CREATE_TABLES,
    os.environ["PROJECT_DATABASE_PATH"],
    ["PRAGMA foreign_keys = 1"],
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


def create_version(version_number: str, project_id: UUID) -> Version:
    q = """INSERT INTO version(project_id, major, minor, patch, id, created_at)
    VALUES (?,?,?,?,?,?) RETURNING *"""
    time = (
        datetime.now(UTC).replace(hour=0, minute=0, second=0, microsecond=0).timestamp()
    )
    args = str(project_id), *map(int, version_number.split(".")), str(uuid4()), time

    try:
        return to_version(_query(lambda c: c.execute(q, args).fetchone()))
    except sqlite3.IntegrityError as integrity:
        if integrity.sqlite_errorname == "SQLITE_CONSTRAINT_UNIQUE":
            raise VersionDuplicateError from None
        if integrity.sqlite_errorname == "SQLITE_CONSTRAINT_FOREIGNKEY":
            raise ProjectNotFoundError from None
        raise


def delete_version(version_number: str, project_id: UUID) -> Version:
    check_query = """SELECT * FROM version WHERE project_id = ?
    AND major = ? AND minor = ? AND patch = ? AND released_at IS NOT NULL"""
    check_args = (str(project_id), *map(int, version_number.split(".")))

    if _query(lambda c: c.execute(check_query, check_args).fetchone()) is not None:
        raise VersionCannotBeDeletedError from None

    delete_query = """DELETE FROM version WHERE project_id = ?
    AND major = ? AND minor = ? AND patch = ? AND released_at IS NULL RETURNING *"""

    return to_version(_query(lambda c: c.execute(delete_query, check_args).fetchone()))


def release_version(
    version_number: str, project_id: UUID, released_at: date
) -> Version:
    check_query = """SELECT * FROM version WHERE project_id = ?
    AND major = ? AND minor = ? AND patch = ? AND released_at IS NOT NULL"""
    check_args = (str(project_id), *map(int, version_number.split(".")))

    if _query(lambda c: c.execute(check_query, check_args).fetchone()) is not None:
        raise VersionCannotBeReleasedError from None

    update_query = """UPDATE version SET released_at = ? WHERE project_id = ?
    AND major = ? AND minor = ? AND patch = ? AND released_at IS NULL RETURNING *"""
    released_timestamp = datetime.combine(
        released_at, datetime.min.time(), UTC
    ).timestamp()
    return to_version(
        _query(
            lambda c: c.execute(
                update_query, (released_timestamp, *check_args)
            ).fetchone()
        )
    )


def read_versions(project_id: UUID, page_size: int) -> list[Version]:
    q = """SELECT * FROM version WHERE project_id = ?
    ORDER BY major DESC, minor DESC, patch DESC LIMIT ?"""
    args = str(project_id), page_size
    return [to_version(v) for v in _query(lambda c: c.execute(q, args).fetchall())]


def read_prev_versions(
    project_id: UUID, page_size: int, last_version: str
) -> list[Version]:
    q = """SELECT * FROM version WHERE project_id = :project_id AND(
    (major=:major AND minor=:minor AND patch>:patch) OR
    (major=:major AND minor>:minor) OR
    (major>:major)
    )
    ORDER BY major ASC, minor ASC, patch ASC LIMIT :limit"""
    major, minor, patch = map(int, last_version.split("."))
    params = {
        "project_id": str(project_id),
        "major": major,
        "minor": minor,
        "patch": patch,
        "limit": page_size,
    }
    return [to_version(v) for v in _query(lambda c: c.execute(q, params).fetchall())][
        ::-1
    ]


def read_next_versions(
    project_id: UUID, page_size: int, last_version: str
) -> list[Version]:
    q = """SELECT * FROM version WHERE project_id = :project_id AND(
    (major=:major AND minor=:minor AND patch<:patch) OR
    (major=:major AND minor<:minor) OR
    (major<:major)
    )
    ORDER BY major DESC, minor DESC, patch DESC LIMIT :limit"""
    major, minor, patch = map(int, last_version.split("."))
    params = {
        "project_id": str(project_id),
        "major": major,
        "minor": minor,
        "patch": patch,
        "limit": page_size,
    }
    return [to_version(v) for v in _query(lambda c: c.execute(q, params).fetchall())]
