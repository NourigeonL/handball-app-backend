from collections.abc import Callable
import logging
from typing import Coroutine, Any

from src.common.exceptions import GenericError
from src.common.eventsourcing.exceptions import InvalidOperationError
from src.common.cqrs.messages import Command, IEventPublisher, IMessageBroker, IntegrationEvent, Message, IntegrationEventHandler
from src.common.loggers import app_logger

class InMemBus(IEventPublisher):
    #__routes : dict[type["IMessage"], list[Callable[["IMessage", IMessageHandlerContext], None]]] = {}

    def __init__(self) -> None:
        self.__routes : dict[type[Message], list[IntegrationEventHandler]] = {}

    # def register_handler(self, typename : type["Message|IntegrationEvent"], handler : Callable[[Message, IMessageBroker], Coroutine[Any, Any,None | GenericError]]) -> None:
    def register_handler(self, typename : type["IntegrationEvent"], handler : IntegrationEventHandler) -> None:
        handlers = self.__routes.setdefault(typename, [])

        handlers.append(handler)

    async def publish(self, event : IntegrationEvent) -> None:
        app_logger.debug(f"Fakebus : Publishing {event}")
        handlers = self.__routes.get(type(event))
        if not handlers:
            return
        for handler in handlers:
            await handler(event, self)
