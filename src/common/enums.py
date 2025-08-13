from enum import Enum

class LicenseType(str, Enum):
    A = "A"
    B = "B"
    C = "C"

class StaffMemberRole(str,Enum):
    COACH = "COACH"
    MANAGER = "MANAGER"
    ADMIN = "ADMIN"
    OWNER = "OWNER"
    STAFF = "STAFF"

class TeamCategory(str,Enum):
    U7 = "U7"
    U9 = "U9"
    U11 = "U11"
    U13 = "U13"
    U15 = "U15"
    U18 = "U18"
    SENIOR = "SENIOR"

class Gender(str,Enum):
    M = "M"
    F = "F"

class PlayerPosition(str,Enum):
    GOAL_KEEPER = "GK"
    LEFT_WINGER = "LW"
    RIGHT_WINGER = "RW"
    LEFT_BACK = "LB"
    CENTER_BACK = "CB"
    RIGHT_BACK = "RB"
    PIVOT = "P"

class TrainingOccurencePlayerStatus(str,Enum):
    PRESENT = "PRESENT"
    ABSENT = "ABSENT"
    LATE = "LATE"
    ABSENT_WITHOUT_REASON = "ABSENT_WITHOUT_REASON"