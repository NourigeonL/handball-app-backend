from multipledispatch import dispatch
from src.application.player.commands import RegisterPlayerCommand
from src.common.cqrs.messages import CommandHandler, IAuthService, IEventPublisher
from src.common.eventsourcing.exceptions import InvalidOperationError
from src.common.eventsourcing.repositories import IEventStoreRepository
from src.domains.club.model import Club
from src.domains.federation.model import Federation
from src.domains.player.model import Player, PlayerRegisterData

class PlayerService(CommandHandler):

    def __init__(self, auth_service: IAuthService, event_publisher: IEventPublisher, player_repo: IEventStoreRepository[Player], club_repo: IEventStoreRepository[Club], federation_repo: IEventStoreRepository[Federation]):
        super().__init__(auth_service, event_publisher)
        self._player_repo = player_repo
        self._club_repo = club_repo
        self._federation_repo = federation_repo

    @dispatch(RegisterPlayerCommand)
    async def _handle(self, command: RegisterPlayerCommand) -> None:
        await self._club_repo.get_by_id(command.club_id)
        federation = await self._federation_repo.get_singleton_aggregate()
        if command.license_number and federation.get_player_license(command.license_number):
            raise InvalidOperationError(f"License {command.license_number} already registered")
        player = Player(player_create_data=PlayerRegisterData(
            actor_id=command.actor_id,
            first_name=command.first_name, 
            last_name=command.last_name, 
            gender=command.gender, 
            date_of_birth=command.date_of_birth, 
            license_number=command.license_number))
        federation.register_player_license(player.id, command.license_number, command.license_type, command.actor_id)
        player.register_to_club(command.club_id, command.season, command.license_type, command.actor_id)
        await self._federation_repo.save(federation, -1)
        await self._player_repo.save(player, -1)
