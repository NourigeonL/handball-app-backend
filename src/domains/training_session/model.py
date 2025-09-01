
from multipledispatch import dispatch
from pydantic import BaseModel
from src.common.enums import TrainingSessionPlayerStatus
from src.common.eventsourcing.aggregates import AggregateRoot
from datetime import datetime
from src.common.eventsourcing.exceptions import InvalidOperationError
from src.common.guid import guid
from src.domains.training_session.events import PlayerRemovedFromTrainingSession, PlayerTrainingSessionStatusChangedToAbsent, PlayerTrainingSessionStatusChangedToLate, PlayerTrainingSessionStatusChangedToPresent, TrainingSessionCanceled, TrainingSessionCreated

class TrainingSessionCreate(BaseModel):
    actor_id: str
    club_id: str
    start_time: datetime
    end_time: datetime


class TrainingSession(AggregateRoot):

    @property
    def id(self) -> str:
        return self.__id
    
    @staticmethod
    def to_stream_id(id: str) -> str:
        return f"training_session-{id}"

    def __init__(self, create: TrainingSessionCreate | None = None):
        super().__init__()
        self.players = {}
        self.cancelled = False
        if create:
            self._apply_change(TrainingSessionCreated(
                training_session_id=guid(),
                club_id=create.club_id,
                start_time=create.start_time.isoformat(),
                end_time=create.end_time.isoformat(),
                actor_id=create.actor_id,
            ))

    def remove_player(self, actor_id: str, player_id: str):
        if self.cancelled:
            raise InvalidOperationError("Training session is cancelled")
        if player_id not in self.players:
            raise InvalidOperationError(f"Player {player_id} not in training session {self.id}")
        self._apply_change(PlayerRemovedFromTrainingSession(
            training_session_id=self.id,
            player_id=player_id,
            club_id=self.club_id,
            actor_id=actor_id))

    def change_player_status(self, actor_id: str, player_id: str, status: TrainingSessionPlayerStatus, reason: str | None = None, arrival_time: datetime | None = None, with_reason: bool = False):
        if self.cancelled:
            raise InvalidOperationError("Training session is cancelled")
        match status:
            case TrainingSessionPlayerStatus.PRESENT:
                self._apply_change(PlayerTrainingSessionStatusChangedToPresent(
                    training_session_id=self.id,
                    player_id=player_id,
                    actor_id=actor_id,
                ))
            case TrainingSessionPlayerStatus.ABSENT:
                self._apply_change(PlayerTrainingSessionStatusChangedToAbsent(
                    training_session_id=self.id,
                    player_id=player_id,
                    reason=reason,
                    with_reason=with_reason,
                    actor_id=actor_id,
                ))
            case TrainingSessionPlayerStatus.LATE:
                if not arrival_time:
                    raise InvalidOperationError("Arrival time is required")
                if arrival_time > self.end_time or arrival_time < self.start_time:
                    raise InvalidOperationError("Arrival time is not in the training session time")
                self._apply_change(PlayerTrainingSessionStatusChangedToLate(
                    training_session_id=self.id,
                    player_id=player_id,
                    arrival_time=arrival_time.isoformat(),
                    actor_id=actor_id,
                    with_reason=with_reason,
                    reason=reason,
                ))
    
    @dispatch(TrainingSessionCreated)
    def _apply(self, event: TrainingSessionCreated):
        self.__id = event.training_session_id
        self.club_id = event.club_id
        self.start_time = datetime.fromisoformat(event.start_time)
        self.end_time = datetime.fromisoformat(event.end_time)

    @dispatch(PlayerTrainingSessionStatusChangedToPresent)
    def _apply(self, event: PlayerTrainingSessionStatusChangedToPresent):
        self.players[event.player_id] = TrainingSessionPlayerStatus.PRESENT

    @dispatch(PlayerTrainingSessionStatusChangedToAbsent)
    def _apply(self, event: PlayerTrainingSessionStatusChangedToAbsent):
        self.players[event.player_id] = TrainingSessionPlayerStatus.ABSENT

    @dispatch(PlayerTrainingSessionStatusChangedToLate)
    def _apply(self, event: PlayerTrainingSessionStatusChangedToLate):
        self.players[event.player_id] = TrainingSessionPlayerStatus.LATE

    @dispatch(TrainingSessionCanceled)
    def _apply(self, event: TrainingSessionCanceled):
        self.players = {}
        self.cancelled = True

    @dispatch(PlayerRemovedFromTrainingSession)
    def _apply(self, event: PlayerRemovedFromTrainingSession):
        self.players.pop(event.player_id)