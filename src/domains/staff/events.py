from dataclasses import dataclass

from src.common.enums import StaffMemberRole
from src.common.eventsourcing.event import IEvent


@dataclass
class StaffCreated(IEvent):
    staff_id: str
    club_id: str
    email: str
    first_name: str | None = None
    last_name: str | None = None
    role: StaffMemberRole