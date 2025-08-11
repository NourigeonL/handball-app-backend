

from dataclasses import dataclass
from src.common.eventsourcing import IEvent


@dataclass
class ClubCreated(IEvent):
    club_id : str
    registration_number : str
    owner_id : str
    name : str

@dataclass
class PlayerRegisteredToClub(IEvent):
    club_id : str
    player_id : str
    license_type : str
    season : str

@dataclass
class PlayerLicenseRenewed(IEvent):
    club_id : str
    player_id : str
    license_type : str
    season : str

@dataclass
class CollectiveCreated(IEvent):
    club_id : str
    collective_id : str

@dataclass
class PlayerAssignedToCollective(IEvent):
    club_id : str
    player_id : str
    collective_id : str

@dataclass
class TrainingPlanCreated(IEvent):
    club_id : str
    training_plan_id : str
    day_of_week : str
    start_time : str
    end_time : str
    skip_public_holidays : bool
    assigned_collectives : list[str]