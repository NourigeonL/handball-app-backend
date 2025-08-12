from dataclasses import dataclass
from src.common.enums import LicenseType
from src.common.cqrs import Command

@dataclass
class RegisterPlayerToClub(Command):
    club_id: str
    player_id : str
    license_type : LicenseType
    season : str

@dataclass
class CreateCollective(Command):
    club_id: str
    collective_id : str
    collective_name : str

@dataclass
class AssignPlayerToCollective(Command):
    club_id: str
    collective_id : str
    player_id : str

@dataclass
class UnassignPlayerFromCollective(Command):
    club_id: str
    collective_id : str
    player_id : str