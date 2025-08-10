from dataclasses import dataclass
from src.common.enums import Gender, TeamCategory
from src.common.cqrs.messages import Command

@dataclass
class CreateTeamCommand(Command):
    team_id: str
    category: TeamCategory
    club_id: str
    name: str
    gender: Gender
    season: int | None = None