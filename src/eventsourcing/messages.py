import abc

from src.common.guid import guid
from .exceptions import GenericError
from multipledispatch import dispatch
from dataclasses import asdict, dataclass, field
from typing import Optional, Coroutine, Any
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
    user_id : str

    def __post_init__(self) -> None:
        self.command_id = guid()
        self.date = datetime.now(timezone.utc).isoformat()

class IEventPublisher(abc.ABC):
    @abc.abstractmethod
    async def publish(self, event : "IntegrationEvent") -> None | GenericError:...

class ICommandSender(abc.ABC):
    @abc.abstractmethod
    async def send(self, command : "Command") -> None | GenericError:...

class IMessageBroker(IEventPublisher, ICommandSender):
    pass

class MessageHandler(abc.ABC):
    def __init__(self, message_broker : "IMessageBroker") -> None:
        self._message_broker = message_broker

    @dispatch(Message)
    async def _handle(self, message : "Message")-> None:
        return

    async def handle(self, message : "Message")  -> None | GenericError:
        try:
            await self._handle(message)
        except GenericError as e:
            return e