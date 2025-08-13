from multipledispatch import dispatch
from pydantic import BaseModel
from src.common.guid import guid
from src.common.enums import StaffMemberRole
from src.common.eventsourcing.aggregates import AggregateRoot
from src.domains.staff.events import StaffCreated


class StaffCreateData(BaseModel):
    actor_id: str
    club_id: str
    email: str
    first_name: str | None = None
    last_name: str | None = None
    role: StaffMemberRole

class Staff(AggregateRoot):

    @property
    def id(self) -> str:
        return self.__id

    @staticmethod
    def to_stream_id(id: str) -> str:
        return f"staff-{id}"

    def __init__(self, staff_create_data: StaffCreateData | None = None):
        super().__init__()
        if staff_create_data:
            staff_id = guid()
            self._apply_change(StaffCreated(
                actor_id=staff_create_data.actor_id,
                staff_id=staff_id,
                club_id=staff_create_data.club_id,
                email=staff_create_data.email,
                first_name=staff_create_data.first_name,
                last_name=staff_create_data.last_name,
                role=staff_create_data.role))

    @dispatch(StaffCreated)
    def _apply(self, event: StaffCreated):
        self.__id = event.staff_id
        self.club_id = event.club_id
        self.email = event.email
        self.first_name = event.first_name
        self.last_name = event.last_name
        self.role = event.role

