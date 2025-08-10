
from multipledispatch import dispatch
from src.common.eventsourcing import IRepository
from src.common.cqrs import IAuthService, Command
from src.features.auth.domain.models.club_managment import ClubManagment
from src.features.team.application.commands import CreateTeamCommand

class AuthService(IAuthService):
    def __init__(self, club_managment_repository: IRepository[ClubManagment]):
        self.club_managment_repository = club_managment_repository

    @dispatch(CreateTeamCommand)
    async def _condition_are_met(self, command: CreateTeamCommand) -> bool:
        club_managment = await self.club_managment_repository.get_by_id(command.club_id)
        if club_managment is None:
            return False
        if command.user_id not in club_managment.staff_members:
            return False
        return True
    
    @dispatch(Command)
    async def _condition_are_met(self, command: "Command") -> bool:
        return True