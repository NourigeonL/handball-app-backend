

from dataclasses import dataclass
from src.common.eventsourcing.event import IEvent


@dataclass
class ClubCreated(IEvent):
    club_id: str
    name: str
    registration_number: str | None = None
    owner_id: str | None = None

@dataclass
class ClubOwnerChanged(IEvent):
    club_id: str
    new_owner_id: str

@dataclass
class CoachAdded(IEvent):
    club_id: str
    user_id: str
