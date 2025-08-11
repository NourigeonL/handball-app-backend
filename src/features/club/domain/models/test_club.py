import unittest
from src.features.club.domain.models.club import Club
from src.features.club.domain.events import ClubCreated, PlayerRegisteredToClub

class TestClubAggregate(unittest.IsolatedAsyncioTestCase):

    async def asyncSetUp(self) -> None:
        self.owner_id="1234567890"
        self.club = Club(registration_number="FFHB120", owner_id=self.owner_id, name="Club1")
        self.club.mark_changes_as_committed()

    async def test_club_should_be_created(self) -> None:
        club = Club(registration_number="FFHB120", owner_id="1234567890", name="Club1")
        events = club.get_uncommitted_changes()
        assert club is not None
        assert club.registration_number == "FFHB120"
        assert club.owner_id == "1234567890"
        assert club.name == "Club1"
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


    async def test_adding_player_should_be_idempotent(self) -> None:
        player_id="1234567890"
        license_type="A"
        season="2025"
        self.club.loads_from_history([PlayerRegisteredToClub(club_id=self.club.id, player_id=player_id, license_type=license_type, season=season)])
        self.club.register_player(player_id=player_id, license_type=license_type, season=season)
        events = self.club.get_uncommitted_changes()
        assert len(events) == 0
