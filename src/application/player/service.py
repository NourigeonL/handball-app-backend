from multipledispatch import dispatch
from src.application.player.commands import RegisterPlayerCommand
from src.common.cqrs.messages import CommandHandler, IAuthService, IEventPublisher
from src.common.eventsourcing.repositories import IRepository
from src.domains.club.model import Club
from src.domains.player.model import Player, PlayerCreateData

class PlayerService(CommandHandler):

    def __init__(self, auth_service: IAuthService, event_publisher: IEventPublisher, player_repo: IRepository[Player], club_repo: IRepository[Club]):
        super().__init__(auth_service, event_publisher)
        self._player_repo = player_repo
        self._club_repo = club_repo

    @dispatch(RegisterPlayerCommand)
    async def _handle(self, command: RegisterPlayerCommand) -> None:
        await self._club_repo.get_by_id(command.club_id)
        player = Player(player_create_data=PlayerCreateData(
            actor_id=command.actor_id,
            club_id=command.club_id, 
            first_name=command.first_name, 
            last_name=command.last_name, 
            gender=command.gender, 
            date_of_birth=command.date_of_birth, 
            license_number=command.license_number, 
            license_type=command.license_type))
        await self._player_repo.save(player, -1)
