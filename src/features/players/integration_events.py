from src.eventsourcing.messages import IntegrationEvent, IMessageBroker, MessageHandler
from src.eventsourcing.repositories import IRepository
from src.features.players.aggregates import Player
from src.features.federation import integration_events as federation_integration_events
from multipledispatch import dispatch


class PlayerIntegrationEventHandler(MessageHandler):
    def __init__(self, player_repo : IRepository[Player], message_broker : IMessageBroker) -> None:
        super().__init__(message_broker)
        self.__player_repo = player_repo

    @dispatch(federation_integration_events.IEPlayerLicensed)
    async def _handle(self, event : federation_integration_events.IEPlayerLicensed) -> None:
        player = Player(license_id=event.license_id, first_name=event.first_name, last_name=event.last_name, date_of_birth=event.date_of_birth, email=event.email, phone=event.phone)
        await self.__player_repo.save(player, -1)