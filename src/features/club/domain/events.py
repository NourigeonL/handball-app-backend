

from dataclasses import dataclass
from src.eventsourcing.event import IEvent


@dataclass
class ClubCreated(IEvent):
    registration_number : str
    owner_id : str

@dataclass
class PlayerRegisteredToClub(IEvent):
    player_id : str
    license_type : str
    season : str