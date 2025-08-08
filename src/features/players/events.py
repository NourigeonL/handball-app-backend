

from dataclasses import dataclass
from datetime import date, datetime
from time import timezone
from src.eventsourcing.event import IEvent


@dataclass
class LicenseRegistered(IEvent):
    license_id : str
    player_id : str
@dataclass
class PlayerCreated(IEvent):
    license_id : str
    first_name : str
    last_name : str
    date_of_birth : str
    email : str | None = None
    phone : str | None = None

@dataclass
class PlayerClubMembershipStarted(IEvent):
    club_id : str
    season : str
