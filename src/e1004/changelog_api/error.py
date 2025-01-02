from dataclasses import dataclass


@dataclass(slots=True)
class VersionNumberInvalidError(Exception):
    message: str = "version number must use integers in 'major.minor.patch'"
    code: str = "VALUE_INVALID"


@dataclass(slots=True)
class VersionNotFoundError(Exception):
    message: str = "version missing"
    code: str = "RESOURCE_MISSING"


@dataclass(slots=True)
class ProjectNotFoundError(Exception):
    message: str = "project missing"
    code: str = "RESOURCE_MISSING"


@dataclass(slots=True)
class VersionDuplicateError(Exception):
    message: str = "version duplicate"
    code: str = "RESOURCE_EXISTING"


@dataclass(slots=True)
class VersionCannotBeDeletedError(Exception):
    message: str = "version is released"
    code: str = "RESOURCE_PERMANENT"
