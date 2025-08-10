from src.common.cqrs.messages import IEventPublisher, IntegrationEvent


class FakeBus(IEventPublisher):
    def __init__(self) -> None:

        self.events : list[IntegrationEvent] = []

    async def publish(self, event : IntegrationEvent) -> None:
        self.events.append(event)