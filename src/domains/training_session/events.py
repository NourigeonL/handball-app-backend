from dataclasses import dataclass
from src.common.enums import TrainingSessionPlayerStatus
from src.common.eventsourcing.event import IEvent

@dataclass
class TrainingSessionCreated(IEvent):
    training_session_id: str
    club_id: str
    date: str
    start_time: str | None = None
    end_time: str | None = None

@dataclass
class PlayerTrainingSessionStatusChanged(IEvent):
    training_session_id: str
    player_id: str
    status: TrainingSessionPlayerStatus

