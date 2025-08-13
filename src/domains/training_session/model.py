
from multipledispatch import dispatch
from pydantic import BaseModel
from src.common.eventsourcing.aggregates import AggregateRoot
from datetime import date, datetime
from src.common.guid import guid
from src.domains.training_session.events import PlayersAddedToTrainingSession, TrainingSessionCreated

class TrainingSessionCreate(BaseModel):
    actor_id: str
    club_id: str
    date: date
    start_time: datetime | None = None
    end_time: datetime | None = None


class TrainingSession(AggregateRoot):

    @property
    def id(self) -> str:
        return self.__id
    
    @staticmethod
    def to_stream_id(id: str) -> str:
        return f"training_session-{id}"

    def __init__(self, create: TrainingSessionCreate | None = None):
        super().__init__()
        self.players = []
        if create:
            self._apply_change(TrainingSessionCreated(
                training_session_id=guid(),
                club_id=create.club_id,
                date=create.date.isoformat(),
                start_time=create.start_time.isoformat() if create.start_time else None,
                end_time=create.end_time.isoformat() if create.end_time else None,
                actor_id=create.actor_id,
            ))

    
    @dispatch(TrainingSessionCreated)
    def _apply(self, event: TrainingSessionCreated):
        self.__id = event.training_session_id
        self.club_id = event.club_id
        self.date = event.date
        self.start_time = event.start_time
        self.end_time = event.end_time
        self.actor_id = event.actor_id

    @dispatch(PlayersAddedToTrainingSession)
    def _apply(self, event: PlayersAddedToTrainingSession):
        self.players.extend(event.player_ids)