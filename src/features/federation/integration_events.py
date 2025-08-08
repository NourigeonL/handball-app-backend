
from dataclasses import dataclass
from src.eventsourcing.messages import IntegrationEvent

@dataclass
class IEClubRegistered(IntegrationEvent):
    registration_number : str
    owner_id : str

@dataclass
class IEPlayerLicensed(IntegrationEvent):
    license_id : str
    first_name : str
    last_name : str
    date_of_birth : str
    email : str | None = None
    phone : str | None = None