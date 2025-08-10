from src.common.eventsourcing import IRepository
from src.common.cqrs import IMessageBroker, IntegrationEventHandler
from src.features.players.aggregate import Player
from src.features.federation import application as federation_integration_events
from multipledispatch import dispatch


class PlayerIntegrationEventHandler(IntegrationEventHandler):
    def __init__(self, player_repo : IRepository[Player], message_broker : IMessageBroker) -> None:
        super().__init__(message_broker)
        self.__player_repo = player_repo

    @dispatch(federation_integration_events.IEFederationApprovedPlayerRegistration)
    async def _handle(self, event : federation_integration_events.IEFederationApprovedPlayerRegistration) -> None:
        player = Player(license_id=event.license_id, first_name=event.first_name, last_name=event.last_name, date_of_birth=event.date_of_birth, email=event.email, phone=event.phone)
        await self.__player_repo.save(player, -1)