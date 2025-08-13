
from dataclasses import dataclass

from src.common.enums import Gender, LicenseType
from src.common.eventsourcing.event import IEvent


@dataclass
class PlayerCreated(IEvent):
    player_id: str
    club_id: str
    first_name: str
    last_name: str
    gender: Gender
    date_of_birth: str
    license_number: str | None = None
    license_type: LicenseType | None = None