from src.eventsourcing.messages import IMessageBroker, MessageHandler
from src.features.club.aggregates import Club
from src.eventsourcing.repositories import IRepository
from src.features.federation import integration_events as federation_integration_events
from multipledispatch import dispatch

class ClubIntegrationEventHandler(MessageHandler):
    def __init__(self, club_repo : IRepository[Club], message_broker : IMessageBroker) -> None:
        super().__init__(message_broker)
        self.__club_repo = club_repo

    @dispatch(federation_integration_events.IEClubRegistered)
    async def _handle(self, event : federation_integration_events.IEClubRegistered) -> None:
        club = Club(registration_number=event.registration_number, owner_id=event.owner_id)
        await self.__club_repo.save(club, -1)
        