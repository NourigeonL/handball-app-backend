from datetime import date
from multipledispatch import dispatch
from pydantic import BaseModel
from src.common.eventsourcing.event import IEvent
from src.common.guid import guid
from src.common.enums import Gender, LicenseType
from src.common.eventsourcing.aggregates import AggregateRoot
from src.domains.player.events import PlayerCreated


class PlayerCreateData(BaseModel):
    actor_id: str
    club_id: str
    first_name: str
    last_name: str
    gender: Gender
    date_of_birth: date
    license_number: str | None = None
    license_type: LicenseType | None = None

class Player(AggregateRoot):

    @property
    def id(self) -> str:
        return self.__id

    @staticmethod
    def to_stream_id(id: str) -> str:
        return f"player-{id}"

    def __init__(self, player_create_data: PlayerCreateData | None = None):
        super().__init__()
        if player_create_data:
            player_id = guid()
            self._apply_change(PlayerCreated(
                actor_id=player_create_data.actor_id,
                player_id=player_id, 
                club_id=player_create_data.club_id, 
                first_name=player_create_data.first_name, 
                last_name=player_create_data.last_name, 
                gender=player_create_data.gender, 
                date_of_birth=player_create_data.date_of_birth.isoformat(), 
                license_number=player_create_data.license_number, 
                license_type=player_create_data.license_type))
        

    @dispatch(PlayerCreated)
    def _apply(self, event: PlayerCreated):
        self.__id = event.player_id
        self.club_id = event.club_id
        self.first_name = event.first_name
        self.last_name = event.last_name
        self.gender = event.gender
        self.date_of_birth = event.date_of_birth
        self.license_number = event.license_number
        self.license_type = event.license_type