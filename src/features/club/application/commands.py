from dataclasses import dataclass
from src.common.enums import LicenseType
from src.common.eventsourcing.messages import Command

@dataclass
class RegisterPlayerToClub(Command):
    club_id: str
    player_id : str
    license_type : LicenseType
    season : str