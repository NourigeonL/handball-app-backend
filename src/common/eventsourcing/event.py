import abc
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone

from src.common.guid import guid
from .encryption import Data

class EventMeta(abc.ABCMeta):
    @property
    def type(cls) -> str:
        return cls.__name__

@dataclass
class IEvent(Data, metaclass=EventMeta):
    def __post_init__(self):
        self.event_id = guid()
        self.triggered_at = datetime.now(timezone.utc).isoformat()
    
    @property
    def type(self) -> str:
        return self.__class__.__name__