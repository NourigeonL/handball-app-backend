from datetime import datetime
from multipledispatch import dispatch
from pydantic import BaseModel
from src.common.enums import Gender, PlayerPosition, TeamCategory
from src.common.utils import get_authorized_categories, get_current_season
from src.common.eventsourcing import AggregateRoot
from src.common.eventsourcing.exceptions import InvalidOperationError
from src.features.team.domain.models.entities import Player
from src.features.team.domain.events import PlayerAdded, PlayerRemoved, TeamCreated

class TeamInit(BaseModel):
    team_id : str
    category : TeamCategory
    club_id : str
    name : str
    gender : Gender
    season : int | None = None

class Team(AggregateRoot):
    __id : str


    @property
    def id(self) -> str:
        return self.__id

    @staticmethod 
    def to_stream_id(id: str) -> str:
        return f"team-{id}"

    def __init__(self, init: TeamInit | None = None):
        super().__init__()
        self.players : dict[str, Player] = {}
        self.nb_players_by_position : dict[PlayerPosition, int] = {}
        if init:
            self._apply_change(TeamCreated(team_id=init.team_id, category=init.category, club_id=init.club_id, name=init.name, gender=init.gender, season=init.season or get_current_season()))

    def validate_team(self) -> tuple[bool, list[str]]:
        errors = []
        if len(self.players) > 12:
            errors.append("Team can only have 12 players")
        for position in PlayerPosition:
            if self.nb_players_by_position.get(position, 0) < 1:
                errors.append(f"Team must have at least 1 player for position {position}")
        return len(errors) == 0, errors

    def add_player(self, player: Player) -> None:
        if self.category not in get_authorized_categories(self.season, player.date_of_birth):
            raise InvalidOperationError(f"Player {player.license_id} is not allowed to play in this category")
        if self.players.get(player.license_id):
            raise InvalidOperationError(f"Player with license id {player.license_id} already exists")
        if player.gender != self.gender:
            raise InvalidOperationError(f"Player {player.license_id} is not of the same gender as the team")
        
        self._apply_change(PlayerAdded(player=player))

    def remove_player(self, license_id: str) -> None:
        if not self.players.get(license_id):
            raise InvalidOperationError(f"Player with license id {license_id} does not exist")
        self._apply_change(PlayerRemoved(license_id=license_id))


    @dispatch(TeamCreated)
    def _apply(self, e: TeamCreated) -> None:
        self.__id = e.team_id
        self.category = e.category
        self.club_id = e.club_id
        self.name = e.name
        self.gender = e.gender
        self.season = e.season

    @dispatch(PlayerAdded)
    def _apply(self, e: PlayerAdded) -> None:
        self.players[e.player.license_id] = e.player
        self.nb_players_by_position[e.player.position] = self.nb_players_by_position.get(e.player.position, 0) + 1

    @dispatch(PlayerRemoved)
    def _apply(self, e: PlayerRemoved) -> None:
        removed_player = self.players.pop(e.license_id)
        self.nb_players_by_position[removed_player.position] -= 1





    