
from dataclasses import dataclass

from src.eventsourcing.event import IEvent


@dataclass
class FederationCreated(IEvent):
    pass

@dataclass
class ClubRegistered(IEvent):
    registration_number : str
    name : str
    owner_id : str

@dataclass
class PlayerRegistered(IEvent):
    license_id : str