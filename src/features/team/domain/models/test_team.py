from datetime import datetime
from unittest.mock import patch
import pytest
import unittest
from src.common.enums import Gender, LicenseType, PlayerPosition, TeamCategory
from src.eventsourcing.exceptions import InvalidOperationError
from src.features.team.domain.events import PlayerAdded, PlayerRemoved
from src.features.team.domain.models.entities import Player
from src.features.team.domain.models.team import Team, TeamInit

class TestTeamAggregate(unittest.TestCase):

    def setUp(self) -> None:
        super().setUp()
    
    def test_player_cannot_join_team_if_gender_is_not_the_same_as_the_team(self) -> None:
        
        team_m = Team(TeamInit(team_id="1", category=TeamCategory.U11, club_id="1", name="Team 1", gender=Gender.M, season=2025))
        team_f = Team(TeamInit(team_id="1", category=TeamCategory.U11, club_id="1", name="Team 1", gender=Gender.F, season=2025))
        player_f = Player(license_id="1", date_of_birth=datetime(2015, 1, 1), gender=Gender.F, position=PlayerPosition.GOAL_KEEPER, license_type=LicenseType.A)
        player_m = Player(license_id="2", date_of_birth=datetime(2015, 1, 1), gender=Gender.M, position=PlayerPosition.GOAL_KEEPER, license_type=LicenseType.A)

        with pytest.raises(InvalidOperationError):
            team_f.add_player(player_m)
        
        with pytest.raises(InvalidOperationError):
            team_m.add_player(player_f)

    def test_player_cannot_join_team_if_category_is_not_authorized(self) -> None:

        with patch("src.common.utils.get_authorized_categories") as mock_get_authorized_categories:
            mock_get_authorized_categories.return_value = {TeamCategory.U11}

            team = Team(TeamInit(team_id="1", category=TeamCategory.U15, club_id="1", name="Team 1", gender=Gender.M, season=2025))
            player = Player(license_id="1", date_of_birth=datetime(2015, 1, 1), gender=Gender.M, position=PlayerPosition.GOAL_KEEPER, license_type=LicenseType.A)

            with pytest.raises(InvalidOperationError):
                team.add_player(player)

    def test_cannot_add_player_if_already_exists(self) -> None:
        license_id = "1"
        team = Team(TeamInit(team_id="1", category=TeamCategory.U11, club_id="1", name="Team 1", gender=Gender.M, season=2025))
        team.loads_from_history([PlayerAdded(player=Player(license_id=license_id, date_of_birth=datetime(2015, 1, 1), gender=Gender.M, position=PlayerPosition.GOAL_KEEPER, license_type=LicenseType.A))])
        
        with pytest.raises(InvalidOperationError):
            team.add_player(Player(license_id=license_id, date_of_birth=datetime(2015, 1, 1), gender=Gender.M, position=PlayerPosition.GOAL_KEEPER, license_type=LicenseType.A))

    def test_player_should_be_added_to_team(self) -> None:
        team = Team(TeamInit(team_id="1", category=TeamCategory.U11, club_id="1", name="Team 1", gender=Gender.M, season=2025))
        player = Player(license_id="1", date_of_birth=datetime(2015, 1, 1), gender=Gender.M, position=PlayerPosition.GOAL_KEEPER, license_type=LicenseType.A)
        team.mark_changes_as_committed()
        team.add_player(player)
        assert team.players == {player.license_id: player}
        events = team.get_uncommitted_changes()
        assert len(events) == 1
        assert events[0] == PlayerAdded(player=player)

    def test_cannot_remove_player_if_not_exists(self) -> None:
        team = Team(TeamInit(team_id="1", category=TeamCategory.U11, club_id="1", name="Team 1", gender=Gender.M, season=2025))
        with pytest.raises(InvalidOperationError):
            team.remove_player("1")

    def test_player_should_be_removed_from_team(self) -> None:
        team = Team(TeamInit(team_id="1", category=TeamCategory.U11, club_id="1", name="Team 1", gender=Gender.M, season=2025))
        player = Player(license_id="1", date_of_birth=datetime(2015, 1, 1), gender=Gender.M, position=PlayerPosition.GOAL_KEEPER, license_type=LicenseType.A)
        team.loads_from_history([PlayerAdded(player=player)])
        team.remove_player(player.license_id)
        assert team.players == {}
        events = team.get_uncommitted_changes()
        assert len(events) == 1
        assert events[0] == PlayerRemoved(license_id=player.license_id)
