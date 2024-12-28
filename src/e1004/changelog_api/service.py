from re import fullmatch

from .error import VersionNumberInvalidError


def validate_version_number(number: str) -> str:
    if fullmatch(r"^\d+\.\d+\.\d+$", number) is not None:
        return str(number)
    raise VersionNumberInvalidError
