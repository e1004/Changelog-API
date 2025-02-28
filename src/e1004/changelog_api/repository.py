import os
import sqlite3
from datetime import UTC, date, datetime
from functools import partial
from uuid import UUID, uuid4

from realerikrani.sopenqlite import query

from .db import CREATE_TABLES
from .error import (
    ChangeNotFoundError,
    ProjectNotFoundError,
    VersionCannotBeDeletedError,
    VersionCannotBeReleasedError,
    VersionDuplicateError,
    VersionNotFoundError,
    VersionReleasedError,
)
from .model import Change, Version

_query = partial(
    query,
    CREATE_TABLES,
    os.environ["PROJECT_DATABASE_PATH"],
    ["PRAGMA foreign_keys = 1"],
)


def to_version(row: sqlite3.Row | None) -> Version:
    if row is None:
        raise VersionNotFoundError
    number = f"{row['major']}.{row['minor']}.{row['patch']}"
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


def to_change(row: sqlite3.Row | None) -> Change:
    if row is None:
        raise ChangeNotFoundError
    return Change(
        id=UUID(row["id"]),
        version_id=UUID(row["version_id"]),
        kind=row["kind"],
        body=row["body"],
        author=row["author"],
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


def create_change(
    version_number: str, project_id: UUID, kind: str, body: str, author: str
) -> Change:
    q = """INSERT INTO change(id, version_id, body, kind, author)
    SELECT :change_id, id, :body, :kind, :author FROM version
    WHERE project_id=:project_id AND major=:major AND minor=:minor AND patch=:patch
    RETURNING *"""
    major, minor, patch = map(int, version_number.split("."))
    args = {
        "change_id": str(uuid4()),
        "body": body,
        "kind": kind,
        "project_id": str(project_id),
        "author": author,
        "major": major,
        "minor": minor,
        "patch": patch,
    }

    try:
        return to_change(_query(lambda c: c.execute(q, args).fetchone()))
    except ChangeNotFoundError:
        raise VersionNotFoundError from None


def delete_change(version_number: str, id: UUID, project_id: UUID) -> Change:
    qv = "SELECT * FROM version WHERE project_id=? AND major=? AND minor=? AND patch=?"
    qc = """DELETE FROM change
    WHERE id=? AND version_id=(
    SELECT id FROM version
    WHERE project_id=? AND major=? AND minor=? AND patch=? AND released_at is NULL
    ) RETURNING *"""
    args_v = str(project_id), *map(int, version_number.split("."))
    args_c = str(id), str(project_id), *map(int, version_number.split("."))
    _qv = lambda c: c.execute(qv, args_v).fetchone()
    _qc = lambda c: c.execute(qc, args_c).fetchone()
    version, change = _query(lambda c: (_qv(c), _qc(c)))
    v = to_version(version)
    if v.released_at:
        raise VersionReleasedError
    return to_change(change)


def read_changes_for_version(version_number: str, project_id: UUID) -> list[Change]:
    version_query = """SELECT id FROM version WHERE project_id = ?
                       AND major = ? AND minor = ? AND patch = ?"""
    version_args = (str(project_id), *map(int, version_number.split(".")))
    version_id_row = _query(lambda c: c.execute(version_query, version_args).fetchone())
    if version_id_row is None:
        raise VersionNotFoundError
    version_id = version_id_row[0]
    change_query = """SELECT * FROM change WHERE version_id=? ORDER BY kind ASC"""
    change_args = (version_id,)
    return [
        to_change(h)
        for h in _query(lambda c: c.execute(change_query, change_args).fetchall())
    ]


def move_change_to_other_version(
    from_version_number: str, to_version_number: str, project_id: UUID, change_id: UUID
) -> Change:
    qv = "SELECT * FROM version WHERE project_id=? AND major=? AND minor=? AND patch=?"
    qc = """UPDATE change SET version_id=(
    SELECT id FROM version WHERE project_id=:project_id AND
    major=:to_major AND minor=:to_minor AND patch=:to_patch
    AND released_at is NULL)
    WHERE id=:change_id AND version_id=(
    SELECT id FROM version
    WHERE project_id=:project_id AND major=:from_major AND
    minor=:from_minor AND patch=:from_patch AND released_at is NULL
    ) RETURNING *"""
    args_v1 = str(project_id), *map(int, from_version_number.split("."))
    args_v2 = str(project_id), *map(int, to_version_number.split("."))
    args_c = {
        "project_id": str(project_id),
        "change_id": str(change_id),
        "to_major": args_v2[1],
        "to_minor": args_v2[2],
        "to_patch": args_v2[3],
        "from_major": args_v1[1],
        "from_minor": args_v1[2],
        "from_patch": args_v1[3],
    }
    _qv1 = lambda c: c.execute(qv, args_v1).fetchone()
    _qc = lambda c: c.execute(qc, args_c).fetchone()

    try:
        from_version, change = _query(lambda c: (_qv1(c), _qc(c)))
    except sqlite3.IntegrityError as e:
        raise VersionReleasedError from e
    fv = to_version(from_version)
    if fv.released_at:
        raise VersionReleasedError
    return to_change(change)
