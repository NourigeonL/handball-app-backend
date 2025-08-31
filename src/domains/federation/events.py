

from dataclasses import dataclass
from src.common.enums import LicenseType
from src.common.eventsourcing.event import IEvent

@dataclass
class PlayerLicenseRegistered(IEvent):
    player_id: str
    license_number: str
    license_type: LicenseType