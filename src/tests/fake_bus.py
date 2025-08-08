from src.common.exceptions import GenericError
from src.eventsourcing.messages import Command, IMessageBroker, IntegrationEvent
from src.in_mem_bus import InMemBus

class FakeBus(IMessageBroker):
    def __init__(self) -> None:
        self.commands : list[Command] = []
        self.events : list[IntegrationEvent] = []

    async def send(self, command : "Command") -> None | GenericError:
        self.commands.append(command)

    async def publish(self, event : IntegrationEvent) -> None:
        self.events.append(event)