import unittest
import pytest
from src.eventsourcing.exceptions import InvalidOperationError
from src.common.enums import StaffMemberRole
from src.features.club.domain.models.club import Club
from src.features.club.domain.events import ClubCreated, OwnerShipTransferred, PlayerRegisteredToClub, RoleAddedToStaffMember, RoleRemovedFromStaffMember, StaffMemberAdded, StaffMemberRemovedFromClub

class TestClubAggregate(unittest.IsolatedAsyncioTestCase):

    async def asyncSetUp(self) -> None:
        self.owner_id="1234567890"
        self.club = Club(registration_number="FFHB120", owner_id=self.owner_id)
        self.club.mark_changes_as_committed()

    async def test_club_should_be_created(self) -> None:
        club = Club(registration_number="FFHB120", owner_id="1234567890")
        events = club.get_uncommitted_changes()
        assert club is not None
        assert club.registration_number == "FFHB120"
        assert club.owner_id == "1234567890"
        assert len(events) == 1
        assert events[0].type == ClubCreated.type
        assert club.staff_members == {"1234567890" : [StaffMemberRole.OWNER, StaffMemberRole.STAFF]}

    async def test_player_should_be_registered(self) -> None:
        player_id="1234567890"
        license_type="A"
        season="2025"
        self.club.register_player(player_id=player_id, license_type=license_type, season=season)
        events = self.club.get_uncommitted_changes()
        assert len(events) == 1
        assert events[0].type == PlayerRegisteredToClub.type
        player = self.club.players.get(player_id)
        assert player is not None
        assert player.license_id == player_id
        assert player.license_type == license_type
        assert player.season == season


    async def test_cannot_register_player_with_same_license_type_and_season(self) -> None:
        player_id="1234567890"
        license_type="A"
        season="2025"
        self.club.loads_from_history([PlayerRegisteredToClub(player_id=player_id, license_type=license_type, season=season)])
        with pytest.raises(InvalidOperationError):
            self.club.register_player(player_id=player_id, license_type=license_type, season=season)

    async def test_staff_member_should_be_added(self) -> None:
        staff_member_id="new_staff_member"
        self.club.add_staff_member(staff_member_id=staff_member_id)
        events = self.club.get_uncommitted_changes()
        assert len(events) == 1
        assert events[0].type == StaffMemberAdded.type
        assert self.club.staff_members.get(staff_member_id) == [StaffMemberRole.STAFF]

    async def test_cannot_add_staff_member_twice(self) -> None:
        staff_member_id="new_staff_member"
        self.club.loads_from_history([StaffMemberAdded(staff_member_id=staff_member_id)])
        with pytest.raises(InvalidOperationError):
            self.club.add_staff_member(staff_member_id=staff_member_id)

    async def test_cannot_add_role_to_staff_member_that_does_not_exist(self) -> None:
        staff_member_id="new_staff_member"
        with pytest.raises(InvalidOperationError):
            self.club.add_role_to_staff_member(staff_member_id=staff_member_id, role=StaffMemberRole.COACH)

    async def test_cannot_remove_role_from_staff_member_that_does_not_exist(self) -> None:
        staff_member_id="new_staff_member"
        with pytest.raises(InvalidOperationError):
            self.club.remove_role_from_staff_member(staff_member_id=staff_member_id, role=StaffMemberRole.COACH)

    async def test_can_add_role_to_staff_member(self) -> None:
        staff_member_id="new_staff_member"
        self.club.loads_from_history([StaffMemberAdded(staff_member_id=staff_member_id)])
        self.club.add_role_to_staff_member(staff_member_id=staff_member_id, role=StaffMemberRole.COACH)
        events = self.club.get_uncommitted_changes()
        assert len(events) == 1
        assert events[0].type == RoleAddedToStaffMember.type
        assert StaffMemberRole.COACH in self.club.staff_members.get(staff_member_id)

    async def test_can_remove_role_from_staff_member(self) -> None:
        staff_member_id="new_staff_member"
        self.club.loads_from_history([StaffMemberAdded(staff_member_id=staff_member_id), RoleAddedToStaffMember(staff_member_id=staff_member_id, role=StaffMemberRole.COACH)])
        self.club.remove_role_from_staff_member(staff_member_id=staff_member_id, role=StaffMemberRole.COACH)
        events = self.club.get_uncommitted_changes()
        assert len(events) == 1
        assert events[0].type == RoleRemovedFromStaffMember.type

    async def test_cannot_remove_role_from_staff_member_that_does_not_have_it(self) -> None:
        staff_member_id="new_staff_member"
        self.club.loads_from_history([StaffMemberAdded(staff_member_id=staff_member_id)])
        with pytest.raises(InvalidOperationError):
            self.club.remove_role_from_staff_member(staff_member_id=staff_member_id, role=StaffMemberRole.COACH)

    async def test_cannot_remove_owner_role_from_staff_member(self) -> None:
        with pytest.raises(InvalidOperationError):
            self.club.remove_role_from_staff_member(staff_member_id=self.owner_id, role=StaffMemberRole.OWNER)

    async def test_cannot_add_role_to_staff_member_that_already_has_it(self) -> None:
        staff_member_id="new_staff_member"
        self.club.loads_from_history([StaffMemberAdded(staff_member_id=staff_member_id), RoleAddedToStaffMember(staff_member_id=staff_member_id, role=StaffMemberRole.COACH)])
        with pytest.raises(InvalidOperationError):
            self.club.add_role_to_staff_member(staff_member_id=staff_member_id, role=StaffMemberRole.COACH)

    async def test_cannot_add_owner_role_to_staff_member(self) -> None:
        staff_member_id="new_staff_member"
        self.club.loads_from_history([StaffMemberAdded(staff_member_id=staff_member_id)])
        with pytest.raises(InvalidOperationError):
            self.club.add_role_to_staff_member(staff_member_id=staff_member_id, role=StaffMemberRole.OWNER)

    async def test_cannot_transfer_ownership_to_the_same_owner(self) -> None:
        with pytest.raises(InvalidOperationError):
            self.club.transfer_ownership(new_owner_id=self.owner_id)

    async def test_cannot_transfer_ownership_to_a_staff_member_that_does_not_exist(self) -> None:
        with pytest.raises(InvalidOperationError):
            self.club.transfer_ownership(new_owner_id="new_owner")

    async def test_ownership_should_be_transferred(self) -> None:
        new_owner_id="new_owner"
        self.club.loads_from_history([StaffMemberAdded(staff_member_id=new_owner_id)])
        self.club.transfer_ownership(new_owner_id=new_owner_id)
        events = self.club.get_uncommitted_changes()
        assert len(events) == 1
        assert events[0].type == OwnerShipTransferred.type
        assert self.club.owner_id == new_owner_id
        assert StaffMemberRole.OWNER in self.club.staff_members.get(new_owner_id)
        assert StaffMemberRole.OWNER not in self.club.staff_members.get(self.owner_id)

    async def test_cannot_remove_owner_from_club(self) -> None:
        with pytest.raises(InvalidOperationError):
            self.club.remove_staff_member(staff_member_id=self.owner_id)

    async def test_can_remove_staff_member(self) -> None:
        staff_member_id="new_staff_member"
        self.club.loads_from_history([StaffMemberAdded(staff_member_id=staff_member_id)])
        self.club.remove_staff_member(staff_member_id=staff_member_id)
        events = self.club.get_uncommitted_changes()
        assert len(events) == 1
        assert events[0].type == StaffMemberRemovedFromClub.type
        assert staff_member_id not in self.club.staff_members
