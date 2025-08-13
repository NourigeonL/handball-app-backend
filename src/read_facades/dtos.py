from datetime import date
from pydantic import BaseModel

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
    nb_players: int
    players: list[ClubPlayerDTO]

class CollectiveListDTO(BaseModel):
    collective_id: str
    name: str
    nb_players: int