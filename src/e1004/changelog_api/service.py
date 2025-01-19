import contextlib
from datetime import date
from re import fullmatch
from uuid import UUID

from realerikrani.base64token import decode, encode

from . import repository
from .error import (
    ChangeBodyInvalidError,
    ChangeKindInvalidError,
    VersionNumberInvalidError,
    VersionReleasedAtError,
    VersionsReadingTokenInvalidError,
)
from .model import Change, Version, VersionsPage


def validate_version_number(number: str) -> str:
    if fullmatch(r"^\d+\.\d+\.\d+$", number) is not None:
        return number
    raise VersionNumberInvalidError


def validate_released_at(released_at: str) -> date:
    try:
        return date.fromisoformat(released_at)
    except (TypeError, ValueError) as e:
        raise VersionReleasedAtError from e


def create_version(version_number: str, project_id: UUID) -> Version:
    valid_number = validate_version_number(version_number)
    return repository.create_version(valid_number, project_id)


def delete_version(version_number: str, project_id: UUID) -> Version:
    valid_number = validate_version_number(version_number)
    return repository.delete_version(valid_number, project_id)


def release_version(version_number: str, project_id: UUID, released_at: str) -> Version:
    valid_number = validate_version_number(version_number)
    valid_date = validate_released_at(released_at)
    return repository.release_version(valid_number, project_id, valid_date)


def read_versions(project_id: UUID, page_size: int, token: str | None) -> VersionsPage:
    direction = "next"
    if token is None:
        versions = repository.read_versions(project_id, page_size + 1)
    else:
        if (data := decode(token)) is None:
            raise VersionsReadingTokenInvalidError
        try:
            version_number = data["version_number"]
            direction = data["direction"]
        except KeyError as k:
            raise VersionsReadingTokenInvalidError from k
        if direction == "next":
            versions = repository.read_next_versions(
                project_id, page_size + 1, version_number
            )
        elif direction == "previous":
            versions = repository.read_prev_versions(
                project_id, page_size + 1, version_number
            )
        else:
            raise VersionsReadingTokenInvalidError from None

    next_token = None
    prev_token = None
    with contextlib.suppress(IndexError):
        if len(versions) == page_size + 1 and direction == "next":
            versions = versions[:-1]
            next_token = [
                ("version_number", versions[-1].number),
                ("direction", "next"),
            ]
        elif direction == "previous" and repository.read_next_versions(
            project_id, 1, versions[-1].number
        ):
            next_token = [
                ("version_number", versions[-1].number),
                ("direction", "next"),
            ]
        if len(versions) == page_size + 1 and direction == "previous":
            versions = versions[1:]
            prev_token = [
                ("version_number", versions[0].number),
                ("direction", "previous"),
            ]
        elif direction == "next" and repository.read_prev_versions(
            project_id, 1, versions[0].number
        ):
            prev_token = [
                ("version_number", versions[0].number),
                ("direction", "previous"),
            ]
    return VersionsPage(versions, encode(prev_token), encode(next_token))


def validate_kind(kind: str) -> str:
    if kind in ["added", "changed", "deprecated", "removed", "fixed", "security"]:
        return kind
    raise ChangeKindInvalidError


def validate_body(body: str) -> str:
    if 1 <= len(body) <= 1000:
        return body
    raise ChangeBodyInvalidError


def create_change(
    version_number: str, project_id: UUID, kind: str, body: str
) -> Change:
    valid_number = validate_version_number(version_number)
    valid_kind = validate_kind(kind)
    valid_body = validate_body(body)
    return repository.create_change(valid_number, project_id, valid_kind, valid_body)
