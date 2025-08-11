from datetime import datetime
from pydantic import BaseModel
from src.common.eventsourcing import AggregateRoot
from multipledispatch import dispatch

from src.common.eventsourcing.exceptions import InvalidOperationError
from src.features.club.domain.events import ClubCreated, CollectiveCreated, PlayerAssignedToCollective, PlayerRegisteredToClub
from src.features.club.domain.models.collective import Collective
from src.features.club.domain.models.player import ClubPlayer
from src.features.club.domain.models.training_plan import TrainingPlan


class ClubPlayerInfo(BaseModel):
    license_id : str
    license_type : str
    season : str

class Club(AggregateRoot):
    __id : str
    registration_number : str
    name: str
    owner_id: str
    registered_at: datetime
    players : dict[str, ClubPlayer] = {}
    collectives : dict[str, Collective] = {}
    training_plans : dict[str, TrainingPlan] = {}
    @property
    def id(self) -> str:
        return self.__id
    
    @staticmethod
    def to_stream_id(id : str) -> str:
        return f"club-{id}"

    def __init__(self, registration_number : str | None = None, owner_id : str | None = None, name : str | None = None  ):
        super().__init__()
        if registration_number and owner_id and name:
            self._apply_change(ClubCreated(club_id=registration_number, registration_number=registration_number, owner_id=owner_id, name=name))

    def register_player(self, player_id : str, license_type : str, season : str) -> None:
        player_info = self.players.get(player_id)
        if player_info:
            if player_info.license_type == license_type and player_info.season == season:
                return
        self._apply_change(PlayerRegisteredToClub(club_id=self.__id, player_id=player_id, license_type=license_type, season=season))

    def create_collective(self, collective_id : str) -> None:
        self._apply_change(CollectiveCreated(club_id=self.__id, collective_id=collective_id))

    def assign_player_to_collective(self, player_id : str, collective_id : str) -> None:
        if player_id not in self.players:
            raise InvalidOperationError(f"Player {player_id} not found")
        if collective_id not in self.collectives:
            raise InvalidOperationError(f"Collective {collective_id} not found")
        self.collectives[collective_id].add_player(player_id)
        self._apply_change(PlayerAssignedToCollective(club_id=self.__id, player_id=player_id, collective_id=collective_id))


    @dispatch(ClubCreated)
    def _apply(self, e: ClubCreated) -> None:
        self.__id = e.club_id
        self.registration_number = e.registration_number
        self.owner_id = e.owner_id
        self.players = {}
        self.collectives = {}
        self.training_plans = {}
        self.name = e.name

    @dispatch(PlayerRegisteredToClub)
    def _apply(self, e: PlayerRegisteredToClub) -> None:
        self.players[e.player_id] = ClubPlayerInfo(license_id=e.player_id, license_type=e.license_type, season=e.season)

    @dispatch(CollectiveCreated)
    def _apply(self, e: CollectiveCreated) -> None:
        self.collectives[e.collective_id] = Collective(collective_id=e.collective_id)

    @dispatch(PlayerAssignedToCollective)
    def _apply(self, e: PlayerAssignedToCollective) -> None:
        pass