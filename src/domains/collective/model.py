

from multipledispatch import dispatch
from pydantic import BaseModel
from src.common.guid import guid
from src.common.eventsourcing.aggregates import AggregateRoot
from src.domains.collective.events import CollectiveCreated, PlayerAddedToCollective, PlayerRemovedFromCollective
from src.common.eventsourcing.exceptions import InvalidOperationError


class CollectiveCreateData(BaseModel):
    actor_id: str
    club_id: str
    name: str
    description: str | None = None

class Collective(AggregateRoot):

    @property
    def id(self) -> str:
        return self.__id

    @staticmethod
    def to_stream_id(id: str) -> str:
        return f"collective-{id}"

    def __init__(self, collective_create_data: CollectiveCreateData | None = None):
        super().__init__()
        self.players : list[str] = []
        if collective_create_data:
            collective_id = guid()
            self._apply_change(CollectiveCreated(
                actor_id=collective_create_data.actor_id,
                collective_id=collective_id,
                club_id=collective_create_data.club_id,
                name=collective_create_data.name,
                description=collective_create_data.description))

    def add_player(self, player_id: str, actor_id: str):
        if player_id in self.players:
            raise InvalidOperationError(f"Player {player_id} already in collective {self.id}")
        self._apply_change(PlayerAddedToCollective(
            actor_id=actor_id,
            collective_id=self.id,
            player_id=player_id))

    def remove_player(self, player_id: str, actor_id: str):
        if player_id not in self.players:
            raise InvalidOperationError(f"Player {player_id} not in collective {self.id}")
        self._apply_change(PlayerRemovedFromCollective(
            actor_id=actor_id,
            collective_id=self.id,
            player_id=player_id))

    @dispatch(CollectiveCreated)
    def _apply(self, event: CollectiveCreated):
        self.__id = event.collective_id
        self.club_id = event.club_id
        self.name = event.name
        self.description = event.description


    @dispatch(PlayerAddedToCollective)
    def _apply(self, event: PlayerAddedToCollective):
        self.players.append(event.player_id)

    @dispatch(PlayerRemovedFromCollective)
    def _apply(self, event: PlayerRemovedFromCollective):
        self.players.remove(event.player_id)