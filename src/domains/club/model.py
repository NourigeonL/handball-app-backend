

from multipledispatch import dispatch
from pydantic import BaseModel
from src.common.guid import guid
from src.common.eventsourcing.aggregates import AggregateRoot
from src.domains.club.events import ClubCreated


class ClubCreateData(BaseModel):
    actor_id: str
    name: str
    registration_number: str | None = None


class Club(AggregateRoot):

    @property
    def id(self) -> str:
        return self.__id

    @staticmethod
    def to_stream_id(id: str) -> str:
        return f"club-{id}"

    def __init__(self, club_create_data: ClubCreateData | None = None):
        super().__init__()
        if club_create_data:
            self._apply_change(ClubCreated(
                club_id=guid(), 
                name=club_create_data.name, 
                registration_number=club_create_data.registration_number,
                actor_id=club_create_data.actor_id))

    @dispatch(ClubCreated)
    def _apply(self, event: ClubCreated):
        self.__id = event.club_id
        self.name = event.name
        self.registration_number = event.registration_number
