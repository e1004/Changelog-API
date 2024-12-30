from dataclasses import dataclass


@dataclass(slots=True)
class VersionNumberInvalidError(Exception):
    message: str = "version number must use integers in 'major.minor.patch'"
    code: str = "VALUE_INVALID"


@dataclass(slots=True)
class VersionNotFoundError(Exception):
    message: str = "version missing'"
    code: str = "RESOURCE_MISSING"
