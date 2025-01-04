from datetime import date
from re import fullmatch
from uuid import UUID

from . import repository
from .error import VersionNumberInvalidError, VersionReleasedAtError
from .model import Version


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
