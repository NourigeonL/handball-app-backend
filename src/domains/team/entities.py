from datetime import datetime
from pydantic import BaseModel
from src.common.enums import Gender, LicenseType, PlayerPosition

class TeamPlayer(BaseModel):
    license_id : str
    date_of_birth : datetime
    gender : Gender
    license_type : LicenseType
    position : PlayerPosition