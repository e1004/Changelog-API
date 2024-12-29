from datetime import UTC, datetime
from re import fullmatch
from uuid import uuid4

from .error import VersionNumberInvalidError
from .model import Version


def validate_version_number(number: str) -> str:
    if fullmatch(r"^\d+\.\d+\.\d+$", number) is not None:
        return str(number)
    raise VersionNumberInvalidError


def create_version(number: str) -> Version:
    valid_number = validate_version_number(number)
    return Version(datetime.now(tz=UTC), uuid4(), valid_number, uuid4(), None)
