import abc
import os
import sys
import json

from src.read_facades.interface import IReadFacade
from .event import IEvent
from .exceptions import ConcurrencyError


class IEventStore(abc.ABC):
    @abc.abstractmethod
    async def save_events(self, aggregate_id : str, events : list[IEvent], expected_version : int) -> None:...

    @abc.abstractmethod
    async def get_events_for_aggregate(self, aggregate_id : str) -> list[IEvent]:...
    

def get_event_class(class_name) -> type[IEvent]:
    for module in list(sys.modules.values()):
        if hasattr(module, class_name):
            cls = getattr(module, class_name)
            if not issubclass(cls, IEvent):
                raise TypeError(f"{class_name} is not an Event")
            return cls
    raise ValueError(f"Class '{class_name}' not found.")

class EventDescriptor:
    def __init__(self, id : str, event_type: str, event_data : str, version : int) -> None:
        self.event_type = event_type
        self.__event_data = event_data
        self.__version = version
        self.__id = id

    @property
    def event_data(self) -> IEvent:
        return self.__event_data

    @property
    def version(self) -> int:
        return self.__version

    @property
    def id(self) -> str:
        return self.__id
    
    def __repr__(self) -> str:
        return f"(event:{self.event_type} - version:{self.version})"
    
    def to_dict(self) -> dict:
        return {
            "id": self.__id,
            "event_type": self.event_type,
            "event_data": self.event_data,
            "version": self.version
        }
    
    @classmethod
    def from_dict(cls, dict_values : dict) -> "EventDescriptor":
        return cls(dict_values["id"], dict_values["event_type"], dict_values["event_data"], dict_values["version"])

class InMemEventStore(IEventStore):

    def __init__(self) -> None:
        self.current : dict[str, list[EventDescriptor]] = {}

    async def save_events(self, aggregate_id: str, events: list[IEvent], expected_version: int) -> None:
        event_descriptors = self.current.get(aggregate_id)
        if not event_descriptors:
            if expected_version != -1:
                raise ConcurrencyError()
            event_descriptors = []
            self.current[aggregate_id] = event_descriptors

        elif event_descriptors[len(event_descriptors)-1].version != expected_version:
            raise ConcurrencyError()

        i = expected_version

        for event in events:
            i += 1
            event_descriptors.append(EventDescriptor(aggregate_id, event.type,json.dumps(event.to_dict()), i))

    async def get_events_for_aggregate(self, aggregate_id: str) -> list[IEvent]:
        event_descriptors = self.current.get(aggregate_id)
        if event_descriptors is None:
            return []
        return [get_event_class(desc.event_type).from_dict(json.loads(desc.event_data)) for desc in event_descriptors]

class JsonFileEventStore(IEventStore):
    def __init__(self, file_path : str, read_facade_list : list[IReadFacade]) -> None:
        self.file_path = file_path
        self.current : dict[str, list[dict]] = {}
        self.read_facade_list = read_facade_list
        if not os.path.exists(self.file_path):
            with open(self.file_path, "w") as f:
                json.dump({}, f)
        self.load()
    def load(self) -> None:
        if os.path.exists(self.file_path):
            with open(self.file_path, "r") as f:
                self.current = json.load(f)
        for event_descriptor in self.current.values():
            for event_descriptor in event_descriptor:
                for read_facade in self.read_facade_list:
                    event_data = json.loads(event_descriptor["event_data"])
                    read_facade.update_read_model(get_event_class(event_descriptor["event_type"]).from_dict(event_data))

    async def save_events(self, aggregate_id: str, events: list[IEvent], expected_version: int) -> None:
        event_descriptors = self.current.get(aggregate_id)
        if not event_descriptors:
            if expected_version != -1:
                raise ConcurrencyError()
            event_descriptors = []
            self.current[aggregate_id] = event_descriptors

        elif EventDescriptor.from_dict(event_descriptors[len(event_descriptors)-1]).version != expected_version:
            raise ConcurrencyError()

        i = expected_version

        for event in events:
            i += 1
            event_descriptor = EventDescriptor(aggregate_id, event.type,json.dumps(event.to_dict()), i).to_dict()
            event_descriptors.append(event_descriptor)
            for read_facade in self.read_facade_list:
                read_facade.update_read_model(event)

        with open(self.file_path, "w") as f:
            json.dump(self.current, f)

    async def get_events_for_aggregate(self, aggregate_id: str) -> list[IEvent]:
        return [get_event_class(desc["event_type"]).from_dict(json.loads(desc["event_data"])) for desc in self.current.get(aggregate_id, [])]

