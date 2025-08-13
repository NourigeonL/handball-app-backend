

from multipledispatch import dispatch
from pydantic import BaseModel
from src.common.guid import guid
from src.common.eventsourcing.aggregates import AggregateRoot
from src.domains.club.events import ClubCreated, ClubOwnerChanged, CoachAdded


class ClubCreateData(BaseModel):
    actor_id: str
    name: str
    registration_number: str | None = None
    owner_id: str


class Club(AggregateRoot):

    @property
    def id(self) -> str:
        return self.__id

    @staticmethod
    def to_stream_id(id: str) -> str:
        return f"club-{id}"

    def __init__(self, club_create_data: ClubCreateData | None = None):
        super().__init__()
        self.coaches : list[str] = []
        if club_create_data:
            self._apply_change(ClubCreated(
                club_id=guid(), 
                name=club_create_data.name, 
                registration_number=club_create_data.registration_number,
                owner_id=club_create_data.owner_id,
                actor_id=club_create_data.actor_id,
            ))


    def change_owner(self, new_owner_id: str, actor_id: str):
        self._apply_change(ClubOwnerChanged(
            club_id=self.id,
            new_owner_id=new_owner_id,
            actor_id=actor_id,
        ))

    def add_coach(self, user_id: str, actor_id: str):
        self._apply_change(CoachAdded(club_id=self.id, user_id=user_id, actor_id=actor_id))

    @dispatch(ClubCreated)
    def _apply(self, event: ClubCreated):
        self.__id = event.club_id
        self.name = event.name
        self.registration_number = event.registration_number
        self.owner_id = event.owner_id

    @dispatch(ClubOwnerChanged)
    def _apply(self, event: ClubOwnerChanged):
        self.owner_id = event.new_owner_id

    @dispatch(CoachAdded)
    def _apply(self, event: CoachAdded):
        self.coaches.append(event.user_id)