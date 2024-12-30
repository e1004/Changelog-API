from dataclasses import dataclass
from datetime import date
from uuid import UUID


@dataclass(slots=True)
class Version:
    created_at: date
    project_id: UUID
    number: str
    id: UUID
    released_at: date | None
