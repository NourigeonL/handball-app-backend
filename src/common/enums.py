from enum import Enum
from datetime import datetime, date
from typing import Optional

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

class TrainingSessionPlayerStatus(str,Enum):
    PRESENT = "PRESENT"
    ABSENT = "ABSENT"
    LATE = "LATE"
    ABSENT_WITHOUT_REASON = "ABSENT_WITHOUT_REASON"

class Season(str, Enum):
    SEASON_2024_2025 = "2024/2025"
    SEASON_2025_2026 = "2025/2026"
    SEASON_2026_2027 = "2026/2027"
    SEASON_2027_2028 = "2027/2028"
    SEASON_2028_2029 = "2028/2029"
    SEASON_2029_2030 = "2029/2030"
    SEASON_2030_2031 = "2030/2031"
    
    def __lt__(self, other):
        """Enable comparison between seasons"""
        if not isinstance(other, Season):
            return NotImplemented
        return self.start_year < other.start_year
    
    def __le__(self, other):
        """Enable <= comparison between seasons"""
        if not isinstance(other, Season):
            return NotImplemented
        return self.start_year <= other.start_year
    
    def __gt__(self, other):
        """Enable > comparison between seasons"""
        if not isinstance(other, Season):
            return NotImplemented
        return self.start_year > other.start_year
    
    def __ge__(self, other):
        """Enable >= comparison between seasons"""
        if not isinstance(other, Season):
            return NotImplemented
        return self.start_year >= other.start_year
    
    def __eq__(self, other):
        """Enable == comparison between seasons"""
        if not isinstance(other, Season):
            return NotImplemented
        return self.start_year == other.start_year
    
    def __ne__(self, other):
        """Enable != comparison between seasons"""
        if not isinstance(other, Season):
            return NotImplemented
        return self.start_year != other.start_year
    
    @property
    def start_year(self) -> int:
        """Get the start year of the season"""
        return int(self.value.split('/')[0])
    
    @property
    def end_year(self) -> int:
        """Get the end year of the season"""
        return int(self.value.split('/')[1])
    
    @property
    def display_name(self) -> str:
        """Get a display-friendly name for the season"""
        return f"Season {self.value}"
    
    @classmethod
    def from_year(cls, year: int) -> Optional['Season']:
        """Get season from a specific year (returns the season that contains that year)"""
        for season in cls:
            if season.start_year <= year <= season.end_year:
                return season
        return None
    
    @classmethod
    def current_season(cls) -> 'Season':
        """Get the current season based on current date"""
        current_year = datetime.now().year
        current_month = datetime.now().month
        
        # Handball seasons typically start in August/September
        # If we're in the first half of the year, we're still in the previous season
        if current_month < 8:
            current_year -= 1
        print(f"current_year: {current_year}")
        season = cls.from_year(current_year)
        if season is None:
            # Fallback to the most recent season
            return max(cls)
        return season
    
    @classmethod
    def next_season(cls, current: 'Season') -> Optional['Season']:
        """Get the next season after the current one"""
        seasons = list(cls)
        try:
            current_index = seasons.index(current)
            if current_index < len(seasons) - 1:
                return seasons[current_index + 1]
        except ValueError:
            pass
        return None
    
    @classmethod
    def previous_season(cls, current: 'Season') -> Optional['Season']:
        """Get the previous season before the current one"""
        seasons = list(cls)
        try:
            current_index = seasons.index(current)
            if current_index > 0:
                return seasons[current_index - 1]
        except ValueError:
            pass
        return None
    
    def is_current(self) -> bool:
        """Check if this is the current season"""
        return self == self.current_season()
    
    def is_future(self) -> bool:
        """Check if this is a future season"""
        return self > self.current_season()
    
    def is_past(self) -> bool:
        """Check if this is a past season"""
        return self < self.current_season()