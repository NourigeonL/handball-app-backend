from datetime import datetime
from unittest.mock import patch
import pytest
import unittest
from src.common.enums import Gender, LicenseType, PlayerPosition, TeamCategory
from src.common.eventsourcing.exceptions import InvalidOperationError
from src.domains.team.events import PlayerAdded, PlayerRemoved
from src.domains.team.model import Team, TeamInit, TeamPlayer

class TestTeamAggregate(unittest.TestCase):

    def setUp(self) -> None:
        super().setUp()
        self.actor_id = "1"
    
    def test_player_cannot_join_team_if_gender_is_not_the_same_as_the_team(self) -> None:
        
        team_m = Team(TeamInit(team_id="1", category=TeamCategory.U11, club_id="1", name="Team 1", gender=Gender.M, season=2025), actor_id=self.actor_id)
        team_f = Team(TeamInit(team_id="1", category=TeamCategory.U11, club_id="1", name="Team 1", gender=Gender.F, season=2025), actor_id=self.actor_id)
        player_f = TeamPlayer(license_id="1", date_of_birth=datetime(2015, 1, 1), gender=Gender.F, position=PlayerPosition.GOAL_KEEPER, license_type=LicenseType.A)
        player_m = TeamPlayer(license_id="2", date_of_birth=datetime(2015, 1, 1), gender=Gender.M, position=PlayerPosition.GOAL_KEEPER, license_type=LicenseType.A)

        with pytest.raises(InvalidOperationError):
            team_f.add_player(player_m, self.actor_id)
        
        with pytest.raises(InvalidOperationError):
            team_m.add_player(player_f, self.actor_id)

    def test_player_cannot_join_team_if_category_is_not_authorized(self) -> None:

        with patch("src.common.utils.get_authorized_categories") as mock_get_authorized_categories:
            mock_get_authorized_categories.return_value = {TeamCategory.U11}

            team = Team(TeamInit(team_id="1", category=TeamCategory.U15, club_id="1", name="Team 1", gender=Gender.M, season=2025), actor_id=self.actor_id)
            player = TeamPlayer(license_id="1", date_of_birth=datetime(2015, 1, 1), gender=Gender.M, position=PlayerPosition.GOAL_KEEPER, license_type=LicenseType.A)

            with pytest.raises(InvalidOperationError):
                team.add_player(player, self.actor_id)

    def test_cannot_add_player_if_already_exists(self) -> None:
        license_id = "1"
        team = Team(TeamInit(team_id="1", category=TeamCategory.U11, club_id="1", name="Team 1", gender=Gender.M, season=2025), actor_id=self.actor_id)
        team.loads_from_history([PlayerAdded(team_id="1",actor_id=self.actor_id, player=TeamPlayer(license_id=license_id, date_of_birth=datetime(2015, 1, 1), gender=Gender.M, position=PlayerPosition.GOAL_KEEPER, license_type=LicenseType.A))])
        
        with pytest.raises(InvalidOperationError):
            team.add_player(actor_id=self.actor_id, player=TeamPlayer(license_id=license_id, date_of_birth=datetime(2015, 1, 1), gender=Gender.M, position=PlayerPosition.GOAL_KEEPER, license_type=LicenseType.A))

    def test_player_should_be_added_to_team(self) -> None:
        team = Team(TeamInit(team_id="1", category=TeamCategory.U11, club_id="1", name="Team 1", gender=Gender.M, season=2025), actor_id=self.actor_id)
        player = TeamPlayer(license_id="1", date_of_birth=datetime(2015, 1, 1), gender=Gender.M, position=PlayerPosition.GOAL_KEEPER, license_type=LicenseType.A)
        team.mark_changes_as_committed()
        team.add_player(player, self.actor_id)
        assert team.players == {player.license_id: player}
        events = team.get_uncommitted_changes()
        assert len(events) == 1
        assert events[0] == PlayerAdded(team_id="1", player=player, actor_id=self.actor_id)

    def test_cannot_remove_player_if_not_exists(self) -> None:
        team = Team(TeamInit(team_id="1", category=TeamCategory.U11, club_id="1", name="Team 1", gender=Gender.M, season=2025), actor_id=self.actor_id)
        with pytest.raises(InvalidOperationError):
            team.remove_player("1", self.actor_id)

    def test_player_should_be_removed_from_team(self) -> None:
        team = Team(TeamInit(team_id="1", category=TeamCategory.U11, club_id="1", name="Team 1", gender=Gender.M, season=2025), actor_id=self.actor_id)
        player = TeamPlayer(license_id="1", date_of_birth=datetime(2015, 1, 1), gender=Gender.M, position=PlayerPosition.GOAL_KEEPER, license_type=LicenseType.A)
        team.loads_from_history([PlayerAdded(team_id="1", player=player, actor_id=self.actor_id)])
        team.remove_player(player.license_id, self.actor_id)
        assert team.players == {}
        events = team.get_uncommitted_changes()
        assert len(events) == 1
        assert events[0] == PlayerRemoved(team_id="1", player_id=player.license_id, actor_id=self.actor_id)

    def test_team_should_be_invalid_if_it_has_more_than_12_players(self) -> None:
        team = Team(TeamInit(team_id="1", category=TeamCategory.U11, club_id="1", name="Team 1", gender=Gender.M, season=2025), actor_id=self.actor_id)
        team.loads_from_history([PlayerAdded(team_id="1", actor_id=self.actor_id, player=TeamPlayer(license_id="1", date_of_birth=datetime(2015, 1, 1), gender=Gender.M, position=PlayerPosition.GOAL_KEEPER, license_type=LicenseType.A)),
        PlayerAdded(team_id="1", actor_id=self.actor_id, player=TeamPlayer(license_id="2", date_of_birth=datetime(2015, 1, 1), gender=Gender.M, position=PlayerPosition.CENTER_BACK, license_type=LicenseType.A)),
        PlayerAdded(team_id="1", actor_id=self.actor_id, player=TeamPlayer(license_id="3", date_of_birth=datetime(2015, 1, 1), gender=Gender.M, position=PlayerPosition.LEFT_BACK, license_type=LicenseType.A)),
        PlayerAdded(team_id="1", actor_id=self.actor_id, player=TeamPlayer(license_id="4", date_of_birth=datetime(2015, 1, 1), gender=Gender.M, position=PlayerPosition.RIGHT_BACK, license_type=LicenseType.A)),
        PlayerAdded(team_id="1", actor_id=self.actor_id, player=TeamPlayer(license_id="5", date_of_birth=datetime(2015, 1, 1), gender=Gender.M, position=PlayerPosition.PIVOT, license_type=LicenseType.A)),
        PlayerAdded(team_id="1", actor_id=self.actor_id, player=TeamPlayer(license_id="6", date_of_birth=datetime(2015, 1, 1), gender=Gender.M, position=PlayerPosition.LEFT_WINGER, license_type=LicenseType.A)),
        PlayerAdded(team_id="1", actor_id=self.actor_id, player=TeamPlayer(license_id="7", date_of_birth=datetime(2015, 1, 1), gender=Gender.M, position=PlayerPosition.RIGHT_WINGER, license_type=LicenseType.A)),
        PlayerAdded(team_id="1", actor_id=self.actor_id, player=TeamPlayer(license_id="8", date_of_birth=datetime(2015, 1, 1), gender=Gender.M, position=PlayerPosition.GOAL_KEEPER, license_type=LicenseType.A)),
        PlayerAdded(team_id="1", actor_id=self.actor_id, player=TeamPlayer(license_id="9", date_of_birth=datetime(2015, 1, 1), gender=Gender.M, position=PlayerPosition.GOAL_KEEPER, license_type=LicenseType.A)),
        PlayerAdded(team_id="1", actor_id=self.actor_id, player=TeamPlayer(license_id="10", date_of_birth=datetime(2015, 1, 1), gender=Gender.M, position=PlayerPosition.GOAL_KEEPER, license_type=LicenseType.A)),
        PlayerAdded(team_id="1", actor_id=self.actor_id, player=TeamPlayer(license_id="11", date_of_birth=datetime(2015, 1, 1), gender=Gender.M, position=PlayerPosition.GOAL_KEEPER, license_type=LicenseType.A)),
        PlayerAdded(team_id="1", actor_id=self.actor_id, player=TeamPlayer(license_id="12", date_of_birth=datetime(2015, 1, 1), gender=Gender.M, position=PlayerPosition.GOAL_KEEPER, license_type=LicenseType.A)),
        PlayerAdded(team_id="1", actor_id=self.actor_id, player=TeamPlayer(license_id="13", date_of_birth=datetime(2015, 1, 1), gender=Gender.M, position=PlayerPosition.GOAL_KEEPER, license_type=LicenseType.A))])
        is_valid, errors = team.validate_team()
        assert not is_valid

    def test_team_should_be_invalid_if_right_winger_is_missing(self) -> None:
        team = Team(TeamInit(team_id="1", category=TeamCategory.U11, club_id="1", name="Team 1", gender=Gender.M, season=2025), actor_id=self.actor_id)
        team.loads_from_history([PlayerAdded(team_id="1", actor_id=self.actor_id, player=TeamPlayer(license_id="1", date_of_birth=datetime(2015, 1, 1), gender=Gender.M, position=PlayerPosition.GOAL_KEEPER, license_type=LicenseType.A)),
        PlayerAdded(team_id="1", actor_id=self.actor_id, player=TeamPlayer(license_id="2", date_of_birth=datetime(2015, 1, 1), gender=Gender.M, position=PlayerPosition.CENTER_BACK, license_type=LicenseType.A)),
        PlayerAdded(team_id="1", actor_id=self.actor_id, player=TeamPlayer(license_id="3", date_of_birth=datetime(2015, 1, 1), gender=Gender.M, position=PlayerPosition.LEFT_BACK, license_type=LicenseType.A)),
        PlayerAdded(team_id="1", actor_id=self.actor_id, player=TeamPlayer(license_id="4", date_of_birth=datetime(2015, 1, 1), gender=Gender.M, position=PlayerPosition.RIGHT_BACK, license_type=LicenseType.A)),
        PlayerAdded(team_id="1", actor_id=self.actor_id, player=TeamPlayer(license_id="5", date_of_birth=datetime(2015, 1, 1), gender=Gender.M, position=PlayerPosition.PIVOT, license_type=LicenseType.A)),
        PlayerAdded(team_id="1", actor_id=self.actor_id, player=TeamPlayer(license_id="6", date_of_birth=datetime(2015, 1, 1), gender=Gender.M, position=PlayerPosition.LEFT_WINGER, license_type=LicenseType.A)),
        PlayerAdded(team_id="1", actor_id=self.actor_id, player=TeamPlayer(license_id="7", date_of_birth=datetime(2015, 1, 1), gender=Gender.M, position=PlayerPosition.LEFT_WINGER, license_type=LicenseType.A))])
        is_valid, errors = team.validate_team()
        assert not is_valid

    def test_team_should_be_invalid_if_left_winger_is_missing(self) -> None:
        team = Team(TeamInit(team_id="1", category=TeamCategory.U11, club_id="1", name="Team 1", gender=Gender.M, season=2025), actor_id=self.actor_id)
        team.loads_from_history([PlayerAdded(team_id="1", actor_id=self.actor_id, player=TeamPlayer(license_id="1", date_of_birth=datetime(2015, 1, 1), gender=Gender.M, position=PlayerPosition.GOAL_KEEPER, license_type=LicenseType.A)),
        PlayerAdded(team_id="1", actor_id=self.actor_id, player=TeamPlayer(license_id="2", date_of_birth=datetime(2015, 1, 1), gender=Gender.M, position=PlayerPosition.CENTER_BACK, license_type=LicenseType.A)),
        PlayerAdded(team_id="1", actor_id=self.actor_id, player=TeamPlayer(license_id="3", date_of_birth=datetime(2015, 1, 1), gender=Gender.M, position=PlayerPosition.LEFT_BACK, license_type=LicenseType.A)),
        PlayerAdded(team_id="1", actor_id=self.actor_id, player=TeamPlayer(license_id="4", date_of_birth=datetime(2015, 1, 1), gender=Gender.M, position=PlayerPosition.RIGHT_BACK, license_type=LicenseType.A)),
        PlayerAdded(team_id="1", actor_id=self.actor_id, player=TeamPlayer(license_id="5", date_of_birth=datetime(2015, 1, 1), gender=Gender.M, position=PlayerPosition.PIVOT, license_type=LicenseType.A)),
        PlayerAdded(team_id="1", actor_id=self.actor_id, player=TeamPlayer(license_id="6", date_of_birth=datetime(2015, 1, 1), gender=Gender.M, position=PlayerPosition.RIGHT_WINGER, license_type=LicenseType.A)),
        PlayerAdded(team_id="1", actor_id=self.actor_id, player=TeamPlayer(license_id="7", date_of_birth=datetime(2015, 1, 1), gender=Gender.M, position=PlayerPosition.RIGHT_WINGER, license_type=LicenseType.A))])
        is_valid, errors = team.validate_team()
        assert not is_valid