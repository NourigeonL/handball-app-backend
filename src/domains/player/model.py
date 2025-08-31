from datetime import date
from multipledispatch import dispatch
from pydantic import BaseModel
from src.common.eventsourcing.event import IEvent
from src.common.eventsourcing.exceptions import InvalidOperationError
from src.common.guid import guid
from src.common.enums import Gender, LicenseType, Season
from src.common.eventsourcing.aggregates import AggregateRoot
from src.domains.player.events import PlayerRegistered, PlayerRegisteredToClub, PlayerUnregisteredFromClub


class PlayerRegisterData(BaseModel):
    actor_id: str
    first_name: str
    last_name: str
    gender: Gender
    date_of_birth: date
    license_number: str | None = None
    player_id: str = guid()

class Player(AggregateRoot):

    @property
    def id(self) -> str:
        return self.__id

    @staticmethod
    def to_stream_id(id: str) -> str:
        return f"player-{id}"

    def __init__(self, player_create_data: PlayerRegisterData | None = None):
        super().__init__()
        self.club_id = None
        self.season = None
        self.license_type = None
        if player_create_data:
            self._apply_change(PlayerRegistered(
                actor_id=player_create_data.actor_id,
                player_id=player_create_data.player_id, 
                first_name=player_create_data.first_name, 
                last_name=player_create_data.last_name, 
                gender=player_create_data.gender, 
                date_of_birth=player_create_data.date_of_birth.isoformat(), 
                license_number=player_create_data.license_number))
        

    def register_to_club(self, club_id: str, season: Season, license_type: LicenseType, actor_id: str):
        if self.club_id and self.club_id != club_id:
            self.unregister_from_club(self.club_id, actor_id)
        self._apply_change(PlayerRegisteredToClub(
            actor_id=actor_id,
            player_id=self.id,
            club_id=club_id,
            season=season,
            license_type=license_type))

    def unregister_from_club(self, club_id: str, actor_id: str):
        if self.club_id != club_id:
            raise InvalidOperationError(f"Player {self.id} not registered to club {club_id}")
        self._apply_change(PlayerUnregisteredFromClub(
            actor_id=actor_id,
            player_id=self.id,
            club_id=club_id))

    @dispatch(PlayerRegistered)
    def _apply(self, event: PlayerRegistered):
        self.__id = event.player_id
        self.first_name = event.first_name
        self.last_name = event.last_name
        self.gender = event.gender
        self.date_of_birth = event.date_of_birth
        self.license_number = event.license_number

    @dispatch(PlayerRegisteredToClub)
    def _apply(self, event: PlayerRegisteredToClub):
        self.club_id = event.club_id
        self.season = event.season
        self.license_type = event.license_type

    @dispatch(PlayerUnregisteredFromClub)
    def _apply(self, event: PlayerUnregisteredFromClub):
        self.club_id = None