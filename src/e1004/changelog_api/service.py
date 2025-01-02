from re import fullmatch
from uuid import UUID

from . import repository
from .error import VersionNumberInvalidError
from .model import Version


def validate_version_number(number: str) -> str:
    if fullmatch(r"^\d+\.\d+\.\d+$", number) is not None:
        return number
    raise VersionNumberInvalidError


def create_version(number: str, project_id: UUID) -> Version:
    valid_number = validate_version_number(number)
    return repository.create_version(valid_number, project_id)


def delete_version(version_number: str, project_id: UUID) -> Version:
    valid_number = validate_version_number(version_number)
    return repository.delete_version(valid_number, project_id)
