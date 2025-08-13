# from contextlib import contextmanager
# import json
# import os
# from typing import Generator

# from multipledispatch import dispatch

# from src.common.dtos import ClubListDTO
# from src.common.eventsourcing.event import IEvent
# from src.common.eventsourcing.event_stores import get_event_class
# from src.features.club.domain.events import ClubCreated, CollectiveCreated, PlayerLicenseRenewed, PlayerRegisteredToClub, PlayerAssignedToCollective
# from src.features.club.domain.models.club import Club
# from src.features.club.domain.models.collective import Collective

# class InMemDB:

#     club_list : dict[str, Club] = {}
#     def __init__(self, event_store_file_path: str):
#         self.event_store_file_path = event_store_file_path
#         self.last_modified = os.path.getmtime(event_store_file_path)
#         self.load_data()

#     def load_data(self):
#         self.club_list = []
#         if os.path.exists(self.event_store_file_path):
#             with open(self.event_store_file_path, "r") as f:
#                 data : dict[str, list[dict]] = json.load(f)
#                 for aggregate_id, events in data.items():
#                     for event in events:
#                         event_class = get_event_class(event["event_type"])
#                         event_data = event_class.from_dict(json.loads(event["event_data"]))
#                         self._apply(event_data)
                        
        
#     @dispatch(ClubCreated)
#     def _apply(self, e : ClubCreated) -> None:
#         self.club_list[e.registration_number] = Club(registration_number=e.registration_number, owner_id=e.owner_id, name=e.name)

#     @dispatch(CollectiveCreated)
#     def _apply(self, e : CollectiveCreated) -> None:
#         self.club_list[e.club_id].collectives[e.collective_id] = Collective(collective_id=e.collective_id)


#     @dispatch(IEvent)
#     def _apply(self, e : IEvent) -> None:
#         pass

#     @contextmanager
#     def get_db(self) -> Generator["InMemDB", None, None]:
#         if os.path.getmtime(self.event_store_file_path) > self.last_modified:
#             self.load_data()
#             self.last_modified = os.path.getmtime(self.event_store_file_path)
#         yield self

