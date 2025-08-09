import unittest
from src.common.enums import LicenseType
from src.eventsourcing.event_stores import InMemEventStore
from src.eventsourcing.repositories import EventStoreRepository
from src.features.federation.aggregate import Federation
from src.features.players.aggregate import Player
from src.features.players.application import PlayerIntegrationEventHandler
from src.tests.fake_bus import FakeBus
from src.features.federation import application as federation_integration_events

class TestPlayer(unittest.IsolatedAsyncioTestCase):

    async def asyncSetUp(self) -> None:
        self.event_store = InMemEventStore()
        self.message_broker = FakeBus()
        self.federation_repo = EventStoreRepository(self.event_store, Federation)
        await self.federation_repo.save(Federation(), -1)
        self.player_repo = EventStoreRepository(self.event_store, Player)
        self.player_integration_event_handler = PlayerIntegrationEventHandler(self.player_repo, self.message_broker)

    async def test_player_should_be_created_when_player_registered_event_is_received(self) -> None:
        await self.player_integration_event_handler.handle(federation_integration_events.IEFederationApprovedPlayerRegistration(license_id="1234567890", first_name="John", last_name="Doe", date_of_birth="1990-01-01", club_id="1234567890", season="2025", license_type=LicenseType.A, email="john.doe@example.com", phone="1234567890"))
        player = await self.player_repo.get_by_id("1234567890")
        assert player is not None
        assert player.version == 0
        assert player.license_id == "1234567890"
        assert player.first_name == "John"
        assert player.last_name == "Doe"
        assert player.date_of_birth == "1990-01-01"
        assert player.email == "john.doe@example.com"
        assert player.phone == "1234567890"
    
