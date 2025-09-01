from dataclasses import dataclass
from src.common.enums import TrainingSessionPlayerStatus
from src.common.eventsourcing.event import IEvent

@dataclass
class TrainingSessionCreated(IEvent):
    training_session_id: str
    club_id: str
    start_time: str
    end_time: str

@dataclass
class PlayerTrainingSessionStatusChanged(IEvent):
    training_session_id: str
    player_id: str
    status: TrainingSessionPlayerStatus

@dataclass
class PlayerTrainingSessionStatusChangedToPresent(IEvent):
    training_session_id: str
    player_id: str

@dataclass
class PlayerTrainingSessionStatusChangedToAbsent(IEvent):
    training_session_id: str
    player_id: str
    with_reason: bool = False
    reason: str | None = None

@dataclass
class PlayerTrainingSessionStatusChangedToLate(IEvent):
    training_session_id: str
    player_id: str
    arrival_time: str
    with_reason: bool = False
    reason: str | None = None
