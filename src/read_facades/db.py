from contextlib import contextmanager
import json
import os
from typing import Generator

from multipledispatch import dispatch

from src.common.dtos import ClubListDTO
from src.common.eventsourcing.event import IEvent
from src.common.eventsourcing.event_stores import get_event_class
from src.features.federation.aggregate import ClubRegistered

class InMemDB:

    club_list : list[ClubListDTO] = []
    def __init__(self, event_store_file_path: str):
        self.event_store_file_path = event_store_file_path
        self.last_modified = os.path.getmtime(event_store_file_path)
        self.load_data()

    def load_data(self):
        self.club_list = []
        if os.path.exists(self.event_store_file_path):
            with open(self.event_store_file_path, "r") as f:
                data : dict[str, list[dict]] = json.load(f)
                for aggregate_id, events in data.items():
                    for event in events:
                        event_class = get_event_class(event["event_type"])
                        event_data = event_class.from_dict(json.loads(event["event_data"]))
                        self._apply(event_data)
                        


    @dispatch(ClubRegistered)
    def _apply(self, e : ClubRegistered) -> None:
        self.club_list.append(ClubListDTO(registration_number=e.registration_number, name=e.name))
        

    @dispatch(IEvent)
    def _apply(self, e : IEvent) -> None:
        pass

    @contextmanager
    def get_db(self) -> Generator["InMemDB", None, None]:
        if os.path.getmtime(self.event_store_file_path) > self.last_modified:
            self.load_data()
            self.last_modified = os.path.getmtime(self.event_store_file_path)
        yield self

