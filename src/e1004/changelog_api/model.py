from dataclasses import dataclass
from datetime import date
from typing import Literal
from uuid import UUID


@dataclass(slots=True)
class Version:
    created_at: date
    project_id: UUID
    number: str
    id: UUID
    released_at: date | None


@dataclass(slots=True)
class VersionsPage:
    versions: list[Version]
    prev_token: str | None
    next_token: str | None


@dataclass(slots=True)
class Change:
    id: UUID
    version_id: UUID
    body: str
    kind: Literal["added", "changed", "deprecated", "removed", "fixed", "security"]
