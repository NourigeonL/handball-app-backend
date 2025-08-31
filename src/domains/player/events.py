
from dataclasses import dataclass

from src.common.enums import Gender, LicenseType, Season
from src.common.eventsourcing.event import IEvent


@dataclass
class PlayerRegistered(IEvent):
    player_id: str
    first_name: str
    last_name: str
    gender: Gender
    date_of_birth: str
    license_number: str | None = None

@dataclass
class PlayerRegisteredToClub(IEvent):
    player_id: str
    club_id: str
    season: Season
    license_type: LicenseType

@dataclass
class PlayerUnregisteredFromClub(IEvent):
    player_id: str
    club_id: str