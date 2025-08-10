from collections.abc import Callable
import logging
from typing import Coroutine, Any

from src.common.exceptions import GenericError
from src.common.eventsourcing.exceptions import InvalidOperationError
from src.common.eventsourcing.messages import Command, IMessageBroker, IntegrationEvent, Message, MessageHandler
from src.common.loggers import app_logger

class InMemBus(IMessageBroker):
    #__routes : dict[type["IMessage"], list[Callable[["IMessage", IMessageHandlerContext], None]]] = {}

    def __init__(self) -> None:
        self.__routes : dict[type[Message], list[MessageHandler]] = {}

    # def register_handler(self, typename : type["Message|IntegrationEvent"], handler : Callable[[Message, IMessageBroker], Coroutine[Any, Any,None | GenericError]]) -> None:
    def register_handler(self, typename : type["Message|IntegrationEvent"], handler : MessageHandler) -> None:
        handlers = self.__routes.setdefault(typename, [])

        handlers.append(handler)

    async def send(self, command : "Command") -> None | GenericError:
        app_logger.debug(f"Fakebus : Sending {command}")
        handlers = self.__routes.get(type(command))
        if handlers:
            if len(handlers) != 1:
                raise InvalidOperationError("cannot send to more than one handler")
            return await handlers[0].handle(command)
        else:
            raise InvalidOperationError(f"no handler registered for {type(command)}")

    async def publish(self, event : IntegrationEvent) -> None:
        app_logger.debug(f"Fakebus : Publishing {event}")
        handlers = self.__routes.get(type(event))
        if not handlers:
            return
        for handler in handlers:
            await handler(event, self)
