from dataclasses import dataclass
from src.common.eventsourcing.event import IEvent

@dataclass
class UserSignedUp(IEvent):
    user_id: str
    name: str | None = None
    first_name: str | None = None
    last_name: str | None = None
    email: str | None = None

@dataclass
class UserNameUpdated(IEvent):
    user_id: str
    first_name: str
    last_name: str
    name: str

@dataclass
class UserEmailUpdated(IEvent):
    user_id: str
    email: str