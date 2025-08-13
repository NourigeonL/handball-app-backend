from abc import ABC, abstractmethod
from multipledispatch import dispatch
from src.common.eventsourcing.event import IEvent
from src.common.loggers import app_logger

class IReadFacade(ABC):

    @dispatch(IEvent)
    def _apply(self, event: "IEvent") -> None:
        pass

    
    def update_read_model(self, event: "IEvent") -> None:
        app_logger.info(f"Updating read model for {event.type}")
        self._apply(event)

