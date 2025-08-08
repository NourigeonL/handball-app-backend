
from uuid import UUID

from pydantic import BaseModel


class ClubListDTO(BaseModel):
    registration_number: str
    name: str