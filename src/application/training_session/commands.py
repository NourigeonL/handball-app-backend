from dataclasses import dataclass
from src.common.cqrs.messages import Command
from src.common.enums import TrainingSessionPlayerStatus
from datetime import datetime

@dataclass
class CreateTrainingSessionCommand(Command):
    club_id: str
    start_time: datetime
    end_time: datetime

@dataclass
class ChangePlayerTrainingSessionStatusCommand(Command):
    club_id: str
    training_session_id: str
    player_id: str
    status: TrainingSessionPlayerStatus
    reason: str | None = None
    arrival_time: datetime | None = None
    with_reason: bool = False