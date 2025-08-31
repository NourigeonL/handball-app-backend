from dataclasses import dataclass
from src.common.cqrs.messages import Command
from src.common.enums import TrainingSessionPlayerStatus
from datetime import date, datetime

@dataclass
class CreateTrainingSessionCommand(Command):
    club_id: str
    date: date
    start_time: datetime | None = None
    end_time: datetime | None = None

@dataclass
class ChangePlayerTrainingSessionStatusCommand(Command):
    club_id: str
    training_session_id: str
    player_id: str
    status: TrainingSessionPlayerStatus