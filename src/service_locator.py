

from src.common.cqrs.messages import IEventPublisher
from src.read_facades.public_read_facade import PublicReadFacade

class ServiceLocator:
    __global = {}

    @property
    def public_read_facade(self) -> PublicReadFacade:
        return self.__global["public_read_facade"]
    
    @public_read_facade.setter
    def public_read_facade(self, public_read_facade : PublicReadFacade) -> None:
        self.__global["public_read_facade"] = public_read_facade

    @property
    def event_publisher(self) -> IEventPublisher:
        return self.__global["event_publisher"]
    
    @event_publisher.setter
    def event_publisher(self, event_publisher : IEventPublisher) -> None:
        self.__global["event_publisher"] = event_publisher

service_locator = ServiceLocator()