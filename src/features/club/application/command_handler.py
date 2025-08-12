from src.common.cqrs import CommandHandler
from src.common.cqrs.messages import IAuthService, IMessageBroker
from multipledispatch import dispatch
from src.features.club.application.commands import AssignPlayerToCollective, CreateCollective, RegisterPlayerToClub, UnassignPlayerFromCollective
from src.features.club.domain.models.club import Club
from src.common.eventsourcing import IRepository

class ClubCommandHandler(CommandHandler):
    def __init__(self, auth_service: IAuthService, message_broker: IMessageBroker, club_repository: IRepository[Club]):
        super().__init__(auth_service, message_broker)
        self.club_repository = club_repository

    @dispatch(CreateCollective)
    async def _handle(self, command: CreateCollective) -> None:
        club = await self.club_repository.get_by_id(command.club_id)
        club.create_collective(command.collective_id, command.collective_name, command.user_id)
        await self.club_repository.save(club)

    @dispatch(RegisterPlayerToClub)
    async def _handle(self, command: RegisterPlayerToClub) -> None:
        club = await self.club_repository.get_by_id(command.club_id)
        club.register_player(command.player_id, command.license_type, command.season, command.user_id)
        await self.club_repository.save(club)

    @dispatch(AssignPlayerToCollective)
    async def _handle(self, command: AssignPlayerToCollective) -> None:
        club = await self.club_repository.get_by_id(command.club_id)
        club.assign_player_to_collective(command.player_id, command.collective_id, command.user_id)
        await self.club_repository.save(club)

    @dispatch(UnassignPlayerFromCollective)
    async def _handle(self, command: UnassignPlayerFromCollective) -> None:
        club = await self.club_repository.get_by_id(command.club_id)
        club.remove_player_from_collective(command.player_id, command.collective_id, command.user_id)
        await self.club_repository.save(club)