from dataclasses import dataclass
from src.common.cqrs.messages import Command

@dataclass
class CreateCollectiveCommand(Command):
    club_id: str
    name: str
    description: str | None = None

@dataclass
class AddPlayerToCollectiveCommand(Command):
    collective_id: str
    player_id: str

@dataclass
class RemovePlayerFromCollectiveCommand(Command):
    collective_id: str
    player_id: str
