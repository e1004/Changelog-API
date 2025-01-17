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
class ChangeNotFoundError(Exception):
    message: str = "change missing"
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
class VersionReleasedError(Exception):
    message: str = "version is released"
    code: str = "RESOURCE_PERMANENT"


@dataclass(slots=True)
class VersionCannotBeDeletedError(VersionReleasedError): ...


@dataclass(slots=True)
class VersionCannotBeReleasedError(VersionReleasedError): ...


@dataclass(slots=True)
class VersionReleasedAtError(Exception):
    message: str = "invalid released at"
    code: str = "VALUE_INVALID"


@dataclass(slots=True)
class VersionsReadingTokenInvalidError(Exception):
    message: str = "versions reading token invalid"
    code: str = "VALUE_INVALID"


@dataclass(slots=True)
class ChangeKindInvalidError(Exception):
    message: str = (
        "invalid kind: must be one of "
        '"added","changed","deprecated","removed","fixed","security"'
    )
    code: str = "VALUE_INVALID"


@dataclass(slots=True)
class ChangeBodyInvalidError(Exception):
    message: str = "change body is longer that 1000 characters"
    code: str = "VALUE_INVALID"
