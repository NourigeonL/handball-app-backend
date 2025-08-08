

from src.eventsourcing.messages import IMessageBroker
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
    def message_broker(self) -> IMessageBroker:
        return self.__global["message_broker"]
    
    @message_broker.setter
    def message_broker(self, message_broker : IMessageBroker) -> None:
        self.__global["message_broker"] = message_broker

service_locator = ServiceLocator()