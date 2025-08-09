

from dataclasses import dataclass
from src.eventsourcing.event import IEvent


@dataclass
class ClubCreated(IEvent):
    registration_number : str
    owner_id : str

@dataclass
class CoachAdded(IEvent):
    coach_id : str


@dataclass
class PlayerRegisteredToClub(IEvent):
    player_id : str
    license_type : str
    season : str

@dataclass
class StaffMemberAdded(IEvent):
    staff_member_id : str

@dataclass
class StaffMemberRemoved(IEvent):
    staff_member_id : str

@dataclass
class RoleAddedToStaffMember(IEvent):
    staff_member_id : str
    role : str

@dataclass
class RoleRemovedFromStaffMember(IEvent):
    staff_member_id : str
    role : str

@dataclass
class OwnerShipTransferred(IEvent):
    new_owner_id : str

@dataclass
class StaffMemberRemovedFromClub(IEvent):
    staff_member_id : str