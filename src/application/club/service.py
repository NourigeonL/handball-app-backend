from multipledispatch import dispatch
from src.application.club.commands import ChangeClubOwnerCommand, CreateClubCommand
from src.common.cqrs.messages import CommandHandler, IAuthService, IEventPublisher
from src.common.eventsourcing.event_stores import IEventStore
from src.common.eventsourcing.repositories import IEventStoreRepository
from src.domains.club.model import Club, ClubCreateData

class ClubService(CommandHandler):

    def __init__(self, auth_service: IAuthService, event_publisher: IEventPublisher, club_repo: IEventStoreRepository[Club]):
        super().__init__(auth_service, event_publisher)
        self._club_repo = club_repo

    @dispatch(CreateClubCommand)
    async def _handle(self, command: CreateClubCommand) -> None:
        club = Club(club_create_data=ClubCreateData(actor_id=command.actor_id, 
        name=command.name, 
        owner_id=command.owner_id,
        registration_number=command.registration_number))
        await self._club_repo.save(club, -1)
        
    @dispatch(ChangeClubOwnerCommand)
    async def _handle(self, command: ChangeClubOwnerCommand) -> None:
        club = await self._club_repo.get_by_id(Club.to_stream_id(command.club_id))
        club.change_owner(command.new_owner_id, command.actor_id)
        await self._club_repo.save(club, club.version)