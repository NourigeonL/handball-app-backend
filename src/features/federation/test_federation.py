from unittest import IsolatedAsyncioTestCase
import pytest
from src.common.eventsourcing.exceptions import InvalidOperationError
from src.features.federation.aggregate import Federation, ClubRegistered, PlayerRegistered


class TestFederationAggregate(IsolatedAsyncioTestCase):

    async def asyncSetUp(self) -> None:
        self.federation = Federation(first_creation=True)
        self.federation.mark_changes_as_committed()

    async def test_register_club(self) -> None:
        registration_number="FFHB-1234567890"
        owner_id="1234567890"
        self.federation.register_club(registration_number=registration_number, name="Test Club", owner_id=owner_id)
        events = self.federation.get_uncommitted_changes()
        assert len(events) == 1
        assert events[0].type == ClubRegistered.type
        club_registered : ClubRegistered = events[0]
        assert club_registered.registration_number == registration_number
        assert club_registered.name == "Test Club"
        assert club_registered.owner_id == owner_id
        assert len(self.federation.clubs) == 1
        assert self.federation.clubs[0] == registration_number

    async def test_cannot_register_club_with_same_registration_number(self) -> None:
        registration_number="FFHB-1234567890"
        self.federation.loads_from_history([ClubRegistered(registration_number=registration_number, name="Test Club", owner_id="1234567890")])
        with pytest.raises(InvalidOperationError):
            self.federation.register_club(registration_number=registration_number, name="Test Club 2", owner_id="1234567890")

    async def test_register_player(self) -> None:
        license_id="1234567890"
        self.federation.register_player(license_id=license_id)
        events = self.federation.get_uncommitted_changes()
        assert len(events) == 1
        assert events[0].type == PlayerRegistered.type
        player_registered : PlayerRegistered = events[0]
        assert player_registered.license_id == license_id

    async def test_cannot_register_player_with_same_license_id(self) -> None:
        license_id="1234567890"
        self.federation.loads_from_history([PlayerRegistered(license_id=license_id)])
        with pytest.raises(InvalidOperationError):
            self.federation.register_player(license_id=license_id)
        
