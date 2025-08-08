from enum import Enum

class LicenseType(Enum):
    A = "A"
    B = "B"
    C = "C"

class StaffMemberRole(str,Enum):
    COACH = "COACH"
    MANAGER = "MANAGER"
    ADMIN = "ADMIN"
    OWNER = "OWNER"
    STAFF = "STAFF"