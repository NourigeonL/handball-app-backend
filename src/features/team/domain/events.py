
from dataclasses import dataclass

from src.common.enums import Gender, TeamCategory
from src.common.eventsourcing import IEvent
from src.features.team.domain.models.entities import TeamPlayer


@dataclass
class TeamCreated(IEvent):
    user_id: str
    team_id: str
    category: TeamCategory
    club_id: str
    name: str
    gender: Gender
    season: int

@dataclass
class PlayerAdded(IEvent):
    user_id: str
    team_id: str
    player: TeamPlayer

@dataclass
class PlayerRemoved(IEvent):
    user_id: str
    team_id: str
    player_id: str
