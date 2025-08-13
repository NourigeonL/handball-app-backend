from multipledispatch import dispatch
from src.application.club.commands import CreateClubCommand
from src.common.cqrs.messages import CommandHandler, IAuthService, IEventPublisher
from src.common.eventsourcing.event_stores import IEventStore
from src.common.eventsourcing.repositories import IRepository
from src.domains.club.model import Club, ClubCreateData

class ClubService(CommandHandler):

    def __init__(self, auth_service: IAuthService, event_publisher: IEventPublisher, club_repo: IRepository[Club]):
        super().__init__(auth_service, event_publisher)
        self._club_repo = club_repo

    @dispatch(CreateClubCommand)
    async def _handle(self, command: CreateClubCommand) -> None:
        club = Club(club_create_data=ClubCreateData(actor_id=command.actor_id, 
        name=command.name, 
        registration_number=command.registration_number))
        await self._club_repo.save(club, -1)
        