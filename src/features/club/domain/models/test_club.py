import unittest
from src.features.club.domain.models.club import Club
from src.features.club.domain.events import ClubCreated, CollectiveCreated, PlayerAssignedToCollective, PlayerRegisteredToClub, PlayerUnassignedFromCollective

class TestClubAggregate(unittest.IsolatedAsyncioTestCase):

    async def asyncSetUp(self) -> None:
        self.owner_id="1234567890"
        self.user_id="1234567890"
        self.club = Club(registration_number="FFHB120", owner_id=self.owner_id, name="Club1", user_id=self.user_id)
        self.club.mark_changes_as_committed()

    async def test_club_should_be_created(self) -> None:
        club = Club(registration_number="FFHB120", owner_id="1234567890", name="Club1", user_id=self.user_id)
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
        self.club.register_player(player_id=player_id, license_type=license_type, season=season, user_id=self.user_id)
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
        self.club.loads_from_history([PlayerRegisteredToClub(club_id=self.club.id, player_id=player_id, license_type=license_type, season=season, user_id=self.user_id)])
        self.club.register_player(player_id=player_id, license_type=license_type, season=season, user_id=self.user_id)
        events = self.club.get_uncommitted_changes()
        assert len(events) == 0

    async def test_collective_should_be_created(self) -> None:
        collective_id="1234567890"
        collective_name="Collective 1"
        self.club.create_collective(collective_id=collective_id, collective_name=collective_name, user_id=self.user_id)
        events = self.club.get_uncommitted_changes()
        assert len(events) == 1
        assert events[0].type == CollectiveCreated.type
        assert self.club.collectives[collective_id].collective_name == collective_name
    
    async def test_player_should_be_assigned_to_collective(self) -> None:
        collective_id="1234567890"
        player_id="1234567890"
        self.club.loads_from_history([CollectiveCreated(club_id=self.club.id, collective_id=collective_id, collective_name="Collective 1", user_id=self.user_id), PlayerRegisteredToClub(club_id=self.club.id, player_id=player_id, license_type="A", season="2025", user_id=self.user_id)])
        self.club.assign_player_to_collective(player_id=player_id, collective_id=collective_id, user_id=self.user_id)
        events = self.club.get_uncommitted_changes()
        assert len(events) == 1
        assert events[0].type == PlayerAssignedToCollective.type
        assert self.club.collectives[collective_id].players == [player_id]

    async def test_player_should_be_unassigned_from_collective(self) -> None:
        collective_id="1234567890"
        player_id="1234567890"
        self.club.loads_from_history([CollectiveCreated(club_id=self.club.id, collective_id=collective_id, collective_name="Collective 1", user_id=self.user_id), PlayerRegisteredToClub(club_id=self.club.id, player_id=player_id, license_type="A", season="2025", user_id=self.user_id), PlayerAssignedToCollective(club_id=self.club.id, player_id=player_id, collective_id=collective_id, user_id=self.user_id)])
        self.club.remove_player_from_collective(player_id=player_id, collective_id=collective_id, user_id=self.user_id)
        events = self.club.get_uncommitted_changes()
        assert len(events) == 1
        assert events[0].type == PlayerUnassignedFromCollective.type
        assert self.club.collectives[collective_id].players == []