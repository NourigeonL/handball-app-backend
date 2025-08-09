from datetime import datetime

from src.common.enums import TeamCategory


def get_current_season() -> int:
        now = datetime.now()
        if now.month < 7:
            return now.year
        else:
            return now.year + 1

def get_authorized_categories(season : int, date_of_birth: datetime) -> set[TeamCategory]:
        age = season - date_of_birth.year
        if age < 7:
            return {TeamCategory.U7, TeamCategory.U9}
        elif age < 9:
            return {TeamCategory.U9, TeamCategory.U11}
        elif age < 11:
            return {TeamCategory.U11, TeamCategory.U13}
        elif age < 13:
            return {TeamCategory.U13, TeamCategory.U15}
        elif age < 15:
            return {TeamCategory.U15, TeamCategory.U18}
        elif age == 15:
            return {TeamCategory.U18}
        elif age >= 16 and age < 18:
            return {TeamCategory.U18, TeamCategory.SENIOR}
        else:
            return {TeamCategory.SENIOR}