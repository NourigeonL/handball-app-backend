import unittest
from src.eventsourcing.event_stores import InMemEventStore
from src.eventsourcing.repositories import EventStoreRepository
from src.features.club.aggregates import Club
from src.features.club.integration_events import ClubIntegrationEventHandler
from src.features.federation.aggregates import Federation
from src.tests.fake_bus import FakeBus
from src.features.federation import integration_events as federation_integration_events

class TestClubIntegrationEventHandler(unittest.IsolatedAsyncioTestCase):

    async def asyncSetUp(self) -> None:
        self.event_store = InMemEventStore()
        self.message_broker = FakeBus()
        self.federation_repo = EventStoreRepository(self.event_store, Federation)
        await self.federation_repo.save(Federation(), -1)
        self.club_repo = EventStoreRepository(self.event_store, Club)
        self.club_integration_event_handler = ClubIntegrationEventHandler(self.club_repo, self.message_broker)

    async def test_club_should_be_created_when_club_registered_event_is_received(self) -> None:
        await self.club_integration_event_handler.handle(federation_integration_events.IEClubRegistered(registration_number="FFHB120", owner_id="1234567890"))
        club = await self.club_repo.get_by_id("FFHB120")
        assert club is not None
        assert club.version == 0
        assert club.registration_number == "FFHB120"
        assert club.owner_id == "1234567890"
