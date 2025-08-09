import unittest
import pytest
from src.eventsourcing.exceptions import InvalidOperationError
from src.features.club.domain.models.club import Club
from src.features.club.domain.events import ClubCreated, PlayerRegisteredToClub

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
