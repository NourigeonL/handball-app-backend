from multipledispatch import dispatch
from src.application.collective.commands import AddPlayerToCollectiveCommand, CreateCollectiveCommand, RemovePlayerFromCollectiveCommand
from src.common.cqrs.messages import CommandHandler, IAuthService, IEventPublisher
from src.common.eventsourcing.exceptions import InvalidOperationError
from src.common.eventsourcing.repositories import IEventStoreRepository
from src.domains.club.model import Club
from src.domains.collective.model import Collective, CollectiveCreateData

class CollectiveService(CommandHandler):

    def __init__(self, auth_service: IAuthService, event_publisher: IEventPublisher, collective_repo: IEventStoreRepository[Collective], club_repo: IEventStoreRepository[Club]):
        super().__init__(auth_service, event_publisher)
        self._collective_repo = collective_repo
        self._club_repo = club_repo

    @dispatch(CreateCollectiveCommand)
    async def _handle(self, command: CreateCollectiveCommand) -> None:
        club = await self._club_repo.get_by_id(command.club_id)
        if not club:
            raise InvalidOperationError(f"Club {command.club_id} not found")
        collective = Collective(collective_create_data=CollectiveCreateData(
            actor_id=command.actor_id, 
            club_id=command.club_id, 
            name=command.name, 
            description=command.description))
        await self._collective_repo.save(collective, -1)

    @dispatch(AddPlayerToCollectiveCommand)
    async def _handle(self, command: AddPlayerToCollectiveCommand) -> None:
        collective = await self._collective_repo.get_by_id(command.collective_id)
        collective.add_player(command.player_id, command.actor_id)
        await self._collective_repo.save(collective, -1)

    @dispatch(RemovePlayerFromCollectiveCommand)
    async def _handle(self, command: RemovePlayerFromCollectiveCommand) -> None:
        collective = await self._collective_repo.get_by_id(command.collective_id)
        collective.remove_player(command.player_id, command.actor_id)
        await self._collective_repo.save(collective, -1)
