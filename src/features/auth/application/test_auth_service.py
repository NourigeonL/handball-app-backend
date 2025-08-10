import unittest
import pytest
from unittest.mock import AsyncMock
from src.common.enums import Gender, TeamCategory
from src.common.eventsourcing.exceptions import UnauthorizedError
from src.common.eventsourcing.messages import Command
from src.features.auth.application.service import AuthService
from src.features.auth.domain.models.club_managment import ClubManagment
from src.features.team.application.commands import CreateTeamCommand


class BaseAuthServiceTest(unittest.IsolatedAsyncioTestCase):

    async def asyncSetUp(self) -> None:
        self.club_managment_repository=AsyncMock()
        self.auth_service = AuthService(club_managment_repository=self.club_managment_repository)

class TestDefaultAuth(BaseAuthServiceTest):
    async def test_should_return_true_by_default(self) -> None:
        class TestCommand(Command):
            pass
        command = TestCommand(user_id="1")
        await self.auth_service.authorize_command(command)


class TestCreateTeamCommandAuth(BaseAuthServiceTest):

    async def test_should_raise_unauthorized_error_if_club_managment_not_found(self) -> None:
        command = CreateTeamCommand(team_id="1", club_id="1", user_id="1", name="Test Team", gender=Gender.M, category=TeamCategory.U11)
        with pytest.raises(UnauthorizedError):
            await self.auth_service.authorize_command(command)

    async def test_should_raise_unauthorized_error_if_user_is_not_in_club_managment(self) -> None:
        self.club_managment_repository.get_by_id.return_value = ClubManagment(registration_number="1", owner_id="1")
        command = CreateTeamCommand(team_id="1", club_id="1", user_id="2", name="Test Team", gender=Gender.M, category=TeamCategory.U11)
        with pytest.raises(UnauthorizedError):
            await self.auth_service.authorize_command(command)

