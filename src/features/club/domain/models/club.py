

from dataclasses import dataclass
from datetime import datetime
from pydantic import BaseModel
from src.common.enums import StaffMemberRole
from src.eventsourcing.event import IEvent
from src.eventsourcing.exceptions import InvalidOperationError
from src.eventsourcing.aggregates import AggregateRoot
from multipledispatch import dispatch

from src.features.club.domain.events import ClubCreated, OwnerShipTransferred, PlayerRegisteredToClub, RoleAddedToStaffMember, RoleRemovedFromStaffMember, StaffMemberAdded, StaffMemberRemovedFromClub


class ClubPlayerInfo(BaseModel):
    license_id : str
    license_type : str
    season : str

class Club(AggregateRoot):
    __id : str
    registration_number : str
    name: str
    owner_id: str
    registered_at: datetime
    players : dict[str, ClubPlayerInfo] = {}
    staff_members : dict[str, list[str]] = {}

    @property
    def id(self) -> str:
        return self.__id
    
    @staticmethod
    def to_stream_id(id : str) -> str:
        return f"club-{id}"

    def __init__(self, registration_number : str | None = None, owner_id : str | None = None):
        super().__init__()
        if registration_number and owner_id:
            self._apply_change(ClubCreated(registration_number=registration_number, owner_id=owner_id))

    def register_player(self, player_id : str, license_type : str, season : str) -> None:
        player_info = self.players.get(player_id)
        if player_info:
            if player_info.license_type == license_type and player_info.season == season:
                raise InvalidOperationError(f"Player {player_id} is already registered to club {self.id} with same license type and season")
        else:
            self._apply_change(PlayerRegisteredToClub(player_id=player_id, license_type=license_type, season=season))

    def add_staff_member(self, staff_member_id : str) -> None:
        if staff_member_id in self.staff_members:
            raise InvalidOperationError(f"Staff member {staff_member_id} already added to club {self.id}")
        self.staff_members[staff_member_id] = []
        self._apply_change(StaffMemberAdded(staff_member_id=staff_member_id))

    def add_role_to_staff_member(self, staff_member_id : str, role : StaffMemberRole) -> None:
        if role == StaffMemberRole.OWNER:
            raise InvalidOperationError(f"Cannot add owner role to staff member {staff_member_id}")
        if staff_member_id not in self.staff_members:
            raise InvalidOperationError(f"Staff member {staff_member_id} not found in club {self.id}")
        if role not in self.staff_members[staff_member_id]:
            self.staff_members[staff_member_id].append(role)
            self._apply_change(RoleAddedToStaffMember(staff_member_id=staff_member_id, role=role))
        else:
            raise InvalidOperationError(f"Role {role} already added to staff member {staff_member_id}")

    def remove_role_from_staff_member(self, staff_member_id : str, role : StaffMemberRole) -> None:
        if role == StaffMemberRole.OWNER:
            raise InvalidOperationError(f"Cannot remove owner role from staff member {staff_member_id}")
        if staff_member_id not in self.staff_members:
            raise InvalidOperationError(f"Staff member {staff_member_id} not found in club {self.id}")
        if role not in self.staff_members[staff_member_id]:
            raise InvalidOperationError(f"Role {role} not found in staff member {staff_member_id}")
        self._apply_change(RoleRemovedFromStaffMember(staff_member_id=staff_member_id, role=role))

    def transfer_ownership(self, new_owner_id : str) -> None:
        if new_owner_id == self.owner_id:
            raise InvalidOperationError(f"New owner {new_owner_id} is the same as the current owner {self.owner_id}")
        if new_owner_id not in self.staff_members:
            raise InvalidOperationError(f"New owner {new_owner_id} not found in club {self.id}")
        self._apply_change(OwnerShipTransferred(new_owner_id=new_owner_id))

    def remove_staff_member(self, staff_member_id : str) -> None:
        if staff_member_id not in self.staff_members:
            raise InvalidOperationError(f"Staff member {staff_member_id} not found in club {self.id}")
        if staff_member_id == self.owner_id:
            raise InvalidOperationError(f"Cannot remove owner from club")
        self._apply_change(StaffMemberRemovedFromClub(staff_member_id=staff_member_id))

    @dispatch(ClubCreated)
    def _apply(self, e: ClubCreated) -> None:
        self.__id = e.registration_number
        self.registration_number = e.registration_number
        self.owner_id = e.owner_id
        self.players = {}
        self.staff_members = {e.owner_id : [StaffMemberRole.OWNER, StaffMemberRole.STAFF]}

    @dispatch(PlayerRegisteredToClub)
    def _apply(self, e: PlayerRegisteredToClub) -> None:
        self.players[e.player_id] = ClubPlayerInfo(license_id=e.player_id, license_type=e.license_type, season=e.season)

    @dispatch(StaffMemberAdded)
    def _apply(self, e: StaffMemberAdded) -> None:
        self.staff_members[e.staff_member_id] = [StaffMemberRole.STAFF]

    @dispatch(RoleAddedToStaffMember)
    def _apply(self, e: RoleAddedToStaffMember) -> None:
        self.staff_members[e.staff_member_id].append(e.role)

    @dispatch(RoleRemovedFromStaffMember)
    def _apply(self, e: RoleRemovedFromStaffMember) -> None:
        self.staff_members[e.staff_member_id].remove(e.role)

    @dispatch(OwnerShipTransferred)
    def _apply(self, e: OwnerShipTransferred) -> None:
        self.staff_members[self.owner_id].remove(StaffMemberRole.OWNER)
        self.owner_id = e.new_owner_id
        self.staff_members[e.new_owner_id].append(StaffMemberRole.OWNER)

    @dispatch(StaffMemberRemovedFromClub)
    def _apply(self, e: StaffMemberRemovedFromClub) -> None:
        self.staff_members.pop(e.staff_member_id)