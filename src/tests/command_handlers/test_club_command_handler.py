import unittest
import pytest
from unittest.mock import AsyncMock, Mock
from src.common.enums import LicenseType
from src.eventsourcing.exceptions import UnauthorizedError
from src.eventsourcing.repositories import EventStoreRepository
from src.features.club.aggregates import Club
from src.features.club.commands import ClubCommandHandler, RegisterPlayerToClub
from src.tests.fake_bus import FakeBus

class TestClubCommandHandler(unittest.IsolatedAsyncioTestCase):

    async def asyncSetUp(self) -> None:
        self.message_broker = FakeBus()
        self.repo = AsyncMock()
        self.handler = ClubCommandHandler(repo=self.repo, message_broker=self.message_broker)

    async def test_cannot_register_player_to_club_if_user_is_not_a_staff_member(self) -> None:
        club = Club(registration_number="1234567890", owner_id="owner_id")
        self.repo.get_by_id = AsyncMock(return_value=club)
        club.register_player = Mock()
        command = RegisterPlayerToClub(club_id="1234567890", player_id="player_id", license_type=LicenseType.A, season="2024/2025", user_id="user_id")
        e = await self.handler.handle(command)
        assert type(e) == UnauthorizedError

    async def test_aggregate_should_be_called(self) -> None:
        club = Club(registration_number="1234567890", owner_id="owner_id")
        self.repo.get_by_id = AsyncMock(return_value=club)
        club.register_player = Mock()
        command = RegisterPlayerToClub(club_id="1234567890", player_id="player_id", license_type=LicenseType.A, season="2024/2025", user_id="owner_id")
        await self.handler.handle(command)
        self.repo.get_by_id.assert_called_once_with("1234567890")
        club.register_player.assert_called_once_with(player_id="player_id", license_type=LicenseType.A, season="2024/2025")
