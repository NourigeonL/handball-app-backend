from dataclasses import dataclass
from src.common.cqrs.messages import Command

@dataclass
class CreateClubCommand(Command):
    name: str
    owner_id: str
    registration_number: str | None = None

@dataclass
class ChangeClubOwnerCommand(Command):
    club_id: str
    new_owner_id: str