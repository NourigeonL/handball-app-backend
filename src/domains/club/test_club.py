
import unittest

from src.domains.club.events import ClubCreated
from src.domains.club.model import Club, ClubCreateData
from src.common.constants import SYSTEM_ACTOR_ID

class TestClubAggregate(unittest.TestCase):

    def test_create_club(self):
        club = Club(club_create_data=ClubCreateData(
            actor_id=SYSTEM_ACTOR_ID, 
            name="Test Club", 
            owner_id="123", 
            registration_number="1234567890"))
        
        assert club.id is not None
        assert club.name == "Test Club"
        assert club.owner_id == "123"
        assert club.registration_number == "1234567890"

        events = club.get_uncommitted_changes()
        assert len(events) == 1
        assert events[0].type == ClubCreated.type
