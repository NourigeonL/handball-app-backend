from dataclasses import dataclass

from src.common.eventsourcing.event import IEvent

@dataclass
class CollectiveCreated(IEvent):
    collective_id: str
    club_id: str
    name: str
    description: str | None = None

@dataclass
class PlayerAddedToCollective(IEvent):
    collective_id: str
    player_id: str

@dataclass
class PlayerRemovedFromCollective(IEvent):
    collective_id: str
    player_id: str