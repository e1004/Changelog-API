from dataclasses import dataclass


@dataclass(slots=True)
class VersionNumberInvalidError(Exception):
    message: str = "Version number must use integers in 'major.minor.patch'"
    code: str = "VALUE_INVALID"
