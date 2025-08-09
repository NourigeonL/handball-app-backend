
from dataclasses import dataclass
from datetime import datetime

from src.common.enums import Gender, LicenseType, PlayerPosition

@dataclass
class Player:
    license_id : str
    date_of_birth : datetime
    gender : Gender
    license_type : LicenseType
    position : PlayerPosition