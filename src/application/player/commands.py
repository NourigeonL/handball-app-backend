from dataclasses import dataclass
from datetime import date
from src.common.cqrs.messages import Command
from src.common.enums import LicenseType
from src.domains.player.model import Gender

@dataclass
class RegisterPlayerCommand(Command):
    club_id: str
    first_name: str
    last_name: str
    gender: Gender
    date_of_birth: date
    season: str
    license_number: str | None = None
    license_type: LicenseType | None = None