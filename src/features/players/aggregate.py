

from dataclasses import dataclass
from datetime import datetime
from src.common.eventsourcing import AggregateRoot
from src.common.eventsourcing import IEvent
from multipledispatch import dispatch

@dataclass
class PlayerCreated(IEvent):
    license_id : str
    first_name : str
    last_name : str
    date_of_birth : str
    email : str | None = None
    phone : str | None = None

@dataclass
class PlayerClubMembershipStarted(IEvent):
    club_id : str
    season : str


class Player(AggregateRoot):
    __id : str
    license_id : str
    licence_type : str
    club_id : str | None = None
    club_registration_date : str | None = None
    first_name : str
    last_name : str
    date_of_birth : str
    email: str | None = None
    phone: str | None = None
    registered_at: datetime

    @property
    def id(self) -> str:
        return self.__id
    
    @staticmethod
    def to_stream_id(id : str) -> str:
        return f"player-{id}"

    def __init__(self, license_id: str | None = None, first_name: str | None = None, last_name: str | None = None, date_of_birth: str | None = None, email: str | None = None, phone: str | None = None):
        super().__init__()
        if license_id:
            self._apply_change(PlayerCreated(license_id=license_id, first_name=first_name, last_name=last_name, date_of_birth=date_of_birth, email=email, phone=phone))


    @dispatch(PlayerCreated)
    def _apply(self, e: PlayerCreated) -> None:
        self.__id = e.license_id
        self.license_id = e.license_id
        self.first_name = e.first_name
        self.last_name = e.last_name
        self.date_of_birth = e.date_of_birth
        self.email = e.email
        self.phone = e.phone
        self.registered_at = e.triggered_at