from unittest import IsolatedAsyncioTestCase

import pytest
from src.eventsourcing.exceptions import InvalidOperationError
from src.eventsourcing.event_stores import InMemEventStore
from src.tests.fake_bus import FakeBus
from src.features.federation.aggregates import Federation
from src.features.federation.commands import FederationCommandHandler, RegisterClub, RegisterPlayer
from src.features.federation.events import ClubRegistered, FederationCreated, PlayerRegistered
from src.eventsourcing.repositories import EventStoreRepository
from src.features.federation import integration_events

class TestFederationCommandHandler(IsolatedAsyncioTestCase):

    pass
        