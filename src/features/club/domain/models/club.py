from datetime import datetime
from pydantic import BaseModel
from src.eventsourcing.exceptions import InvalidOperationError
from src.eventsourcing.aggregates import AggregateRoot
from multipledispatch import dispatch

from src.features.club.domain.events import ClubCreated, PlayerRegisteredToClub


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
    players : dict[str, ClubPlayerInfo] = {}

    @property
    def id(self) -> str:
        return self.__id
    
    @staticmethod
    def to_stream_id(id : str) -> str:
        return f"club-{id}"

    def __init__(self, registration_number : str | None = None, owner_id : str | None = None):
        super().__init__()
        if registration_number and owner_id:
            self._apply_change(ClubCreated(registration_number=registration_number, owner_id=owner_id))

    def register_player(self, player_id : str, license_type : str, season : str) -> None:
        player_info = self.players.get(player_id)
        if player_info:
            if player_info.license_type == license_type and player_info.season == season:
                raise InvalidOperationError(f"Player {player_id} is already registered to club {self.id} with same license type and season")
        else:
            self._apply_change(PlayerRegisteredToClub(player_id=player_id, license_type=license_type, season=season))


    @dispatch(ClubCreated)
    def _apply(self, e: ClubCreated) -> None:
        self.__id = e.registration_number
        self.registration_number = e.registration_number
        self.owner_id = e.owner_id
        self.players = {}

    @dispatch(PlayerRegisteredToClub)
    def _apply(self, e: PlayerRegisteredToClub) -> None:
        self.players[e.player_id] = ClubPlayerInfo(license_id=e.player_id, license_type=e.license_type, season=e.season)