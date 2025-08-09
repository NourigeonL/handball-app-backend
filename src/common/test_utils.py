from datetime import datetime
import unittest
from unittest.mock import patch

from src.common.enums import TeamCategory
from src.common.utils import get_authorized_categories, get_current_season

@patch("src.common.utils.datetime")
def test_current_season_should_return_next_year_if_month_is_after_june(mock_datetime) -> None:
        mock_datetime.now.return_value = datetime(2025, 7, 1)
        assert get_current_season() == 2026

@patch("src.common.utils.datetime")
def test_current_season_should_return_current_year_if_month_is_before_june(mock_datetime) -> None:
        mock_datetime.now.return_value = datetime(2025, 6, 30)
        assert get_current_season() == 2025
        
def test_get_authorized_categories_should_return_correct_categories() -> None:
        values = {
            (2025, datetime(2020, 1, 1)) : {TeamCategory.U7, TeamCategory.U9},
            (2025, datetime(2019, 1, 1)) : {TeamCategory.U7, TeamCategory.U9},
            (2025, datetime(2018, 1, 1)) : {TeamCategory.U9, TeamCategory.U11},
            (2025, datetime(2017, 1, 1)) : {TeamCategory.U9, TeamCategory.U11},
            (2025, datetime(2016, 1, 1)) : {TeamCategory.U11, TeamCategory.U13},
            (2025, datetime(2015, 1, 1)) : {TeamCategory.U11, TeamCategory.U13},
            (2025, datetime(2014, 1, 1)) : {TeamCategory.U13, TeamCategory.U15},
            (2025, datetime(2013, 1, 1)) : {TeamCategory.U13, TeamCategory.U15},
            (2025, datetime(2012, 1, 1)) : {TeamCategory.U15, TeamCategory.U18},
            (2025, datetime(2011, 1, 1)) : {TeamCategory.U15, TeamCategory.U18},
            (2025, datetime(2010, 1, 1)) : {TeamCategory.U18},
            (2025, datetime(2009, 1, 1)) : {TeamCategory.U18, TeamCategory.SENIOR},
            (2025, datetime(2008, 1, 1)) : {TeamCategory.U18, TeamCategory.SENIOR},
            (2025, datetime(2007, 1, 1)) : {TeamCategory.SENIOR},
            (2025, datetime(2006, 1, 1)) : {TeamCategory.SENIOR},
            (2025, datetime(2005, 1, 1)) : {TeamCategory.SENIOR},
        }
        for (season, date_of_birth), expected_categories in values.items():
            print(season, date_of_birth)
            assert get_authorized_categories(season, date_of_birth) == expected_categories