import abc

from src.common.guid import guid
from src.common.exceptions import GenericError
from src.common.cqrs.exceptions import UnauthorizedError
from multipledispatch import dispatch
from dataclasses import dataclass, field
from datetime import datetime, timezone
class Message(abc.ABC):
    pass

@dataclass
class IntegrationEvent(Message, metaclass=abc.ABCMeta):
    __type : str = field(init=False)
    
    def __post_init__(self):
        self.event_id = guid()
        self.triggered_at = datetime.now(timezone.utc).isoformat()
        self.__type = self.__class__.__name__
    
    @property
    def type(self) -> str:
        return self.__type

@dataclass
class Command(Message, metaclass=abc.ABCMeta):
    actor_id : str

    def __post_init__(self) -> None:
        self.command_id = guid()
        self.date = datetime.now(timezone.utc).isoformat()

class IAuthService(abc.ABC):
    async def authorize_command(self, command: Command) -> None:
        if not await self._condition_are_met(command):
            raise UnauthorizedError("Condition are not met")

    async def _condition_are_met(self, command: Command) -> bool:
        """
        Abstract method to check if the condition are met.
        """

class IEventPublisher(abc.ABC):
    @abc.abstractmethod
    async def publish(self, event : "IntegrationEvent") -> None | GenericError:...

class ICommandSender(abc.ABC):
    @abc.abstractmethod
    async def send(self, command : "Command") -> None | GenericError:...

class IMessageBroker(IEventPublisher, ICommandSender):
    pass

class CommandHandler(abc.ABC):
    def __init__(self, auth_service : "IAuthService", message_broker : "IEventPublisher") -> None:
        self._auth_service = auth_service
        self._message_broker = message_broker

    @dispatch(Command)
    async def _handle(self, command : "Command")-> None:
        raise NotImplementedError

    async def handle(self, command : "Command")  -> None:
        await self._auth_service.authorize_command(command)
        await self._handle(command)


class IntegrationEventHandler(abc.ABC):
    def __init__(self, event_publisher : "IEventPublisher") -> None:
        self._event_publisher = event_publisher

    @dispatch(IntegrationEvent)
    async def _handle(self, event : "IntegrationEvent")-> None:
        return

    async def handle(self, event : "IntegrationEvent")  -> None | GenericError:
        try:
            await self._handle(event)
        except GenericError as e:
            return e