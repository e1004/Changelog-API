from dataclasses import dataclass
from datetime import datetime
from uuid import UUID


@dataclass(slots=True)
class Version:
    created_at: datetime
    project_id: UUID
    number: str
    id: UUID
    released_at: datetime | None
