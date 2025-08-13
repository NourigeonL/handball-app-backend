

from dataclasses import dataclass
from src.common.eventsourcing.event import IEvent


@dataclass
class ClubCreated(IEvent):
    club_id: str
    name: str
    registration_number: str | None = None