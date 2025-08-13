from dataclasses import dataclass
from src.common.cqrs.messages import Command

@dataclass
class CreateClubCommand(Command):
    name: str
    registration_number: str | None = None
