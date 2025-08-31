from enum import Enum
from datetime import datetime, date
from typing import Optional
from dataclasses import dataclass

class LicenseType(str, Enum):
    A = "A"
    B = "B"
    C = "C"
    D = "D"

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

class TrainingSessionPlayerStatus(str,Enum):
    PRESENT = "PRESENT"
    ABSENT = "ABSENT"
    LATE = "LATE"
    ABSENT_WITHOUT_REASON = "ABSENT_WITHOUT_REASON"

@dataclass(frozen=True)
class Season:
    start_year: int
    end_year: int
    
    @property
    def value(self) -> str:
        return f"{self.start_year}/{self.end_year}"
    
    @property
    def display_name(self) -> str:
        return f"Season {self.value}"
    
    @classmethod
    def current(cls) -> 'Season':
        """Get the current season based on current date"""
        now = datetime.now()
        # Handball seasons typically start in August/September
        # If we're in the first half of the year, we're still in the previous season
        if now.month < 8:
            start_year = now.year - 1
        else:
            start_year = now.year
        return cls(start_year, start_year + 1)
    
    @classmethod
    def from_year(cls, year: int) -> 'Season':
        """Get season from a specific year (returns the season that contains that year)"""
        return cls(year, year + 1)
    
    @classmethod
    def next_season(cls, current: 'Season') -> 'Season':
        """Get the next season after the current one"""
        return cls(current.start_year + 1, current.end_year + 1)
    
    @classmethod
    def previous_season(cls, current: 'Season') -> 'Season':
        """Get the previous season before the current one"""
        return cls(current.start_year - 1, current.end_year - 1)
    
    def is_current(self) -> bool:
        """Check if this is the current season"""
        return self == self.current()
    
    def is_future(self) -> bool:
        """Check if this is a future season"""
        return self.start_year > self.current().start_year
    
    def is_past(self) -> bool:
        """Check if this is a past season"""
        return self.start_year < self.current().start_year
    
    def __lt__(self, other: 'Season') -> bool:
        """Enable comparison between seasons"""
        if not isinstance(other, Season):
            return NotImplemented
        return self.start_year < other.start_year
    
    def __le__(self, other: 'Season') -> bool:
        """Enable <= comparison between seasons"""
        if not isinstance(other, Season):
            return NotImplemented
        return self.start_year <= other.start_year
    
    def __gt__(self, other: 'Season') -> bool:
        """Enable > comparison between seasons"""
        if not isinstance(other, Season):
            return NotImplemented
        return self.start_year > other.start_year
    
    def __ge__(self, other: 'Season') -> bool:
        """Enable >= comparison between seasons"""
        if not isinstance(other, Season):
            return NotImplemented
        return self.start_year >= other.start_year
    
    def __eq__(self, other: object) -> bool:
        """Enable == comparison between seasons"""
        if not isinstance(other, Season):
            return NotImplemented
        return self.start_year == other.start_year
    
    def __ne__(self, other: object) -> bool:
        """Enable != comparison between seasons"""
        if not isinstance(other, Season):
            return NotImplemented
        return self.start_year != other.start_year