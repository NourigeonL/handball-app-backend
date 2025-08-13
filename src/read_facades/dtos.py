from datetime import date
from pydantic import BaseModel
from typing import List

from src.common.enums import Gender, LicenseType


class ClubListDTO(BaseModel):
    club_id: str
    name: str
    registration_number: str | None = None
    nb_players: int = 0

class ClubDTO(BaseModel):
    club_id: str
    name: str
    registration_number: str | None = None
    owner_id: str | None = None  # Added for authorization
    staff: list[str] = []

class PublicPlayerDTO(BaseModel):
    player_id: str
    first_name: str
    last_name: str
    club_name: str
    gender: Gender
    date_of_birth: date
    license_number: str | None = None
    license_type: LicenseType | None = None

class PlayerDTO(BaseModel):
    player_id: str
    first_name: str
    last_name: str
    club_name: str
    gender: Gender
    date_of_birth: date
    license_number: str | None = None
    license_type: LicenseType | None = None

class ClubPlayerDTO(BaseModel):
    player_id: str
    first_name: str
    last_name: str
    gender: Gender
    date_of_birth: date
    license_number: str | None = None
    license_type: LicenseType | None = None

class CollectiveDTO(BaseModel):
    collective_id: str
    name: str
    description: str | None = None
    players: List[ClubPlayerDTO]
    nb_players: int

class CollectiveListDTO(BaseModel):
    collective_id: str
    name: str
    nb_players: int


class UserClubAccessDTO(BaseModel):
    """DTO for user's club access information"""
    club_id: str
    name: str
    access_level: str  # "owner", "coach", "member", etc.
    can_manage: bool