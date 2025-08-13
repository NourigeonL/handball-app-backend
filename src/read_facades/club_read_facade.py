from multipledispatch import dispatch
from pydantic import BaseModel
from src.common.eventsourcing.event import IEvent
from src.domains.club.events import ClubCreated
from src.domains.collective.events import CollectiveCreated, PlayerAddedToCollective, PlayerRemovedFromCollective
from src.domains.player.events import PlayerCreated
from src.read_facades.dtos import ClubDTO, ClubPlayerDTO, CollectiveDTO, CollectiveListDTO, UserClubAccessDTO
from src.read_facades.interface import IReadFacade


class DBCollectiveDTO(BaseModel):
    collective_id: str
    name: str
    description: str | None = None

class ClubReadFacade(IReadFacade):

    def __init__(self):
        self.club_dict : dict[str, ClubDTO] = {}
        self.club_collective_list_dict : dict[str, list[str]] = {}
        self.collective_player_list_dict : dict[str, list[str]] = {}
        self.club_player_dict : dict[str, list[str]] = {}
        self.player_dict : dict[str, ClubPlayerDTO] = {}
        self.collective_dict : dict[str, DBCollectiveDTO] = {}
        # Store club ownership and access information
        self.club_owners : dict[str, str] = {}  # club_id -> owner_id
        self.club_coaches : dict[str, list[str]] = {}  # club_id -> list of coach user_ids

    @dispatch(ClubCreated)
    def _apply(self, event: ClubCreated) -> None:
        self.club_dict[event.club_id] = ClubDTO(
            club_id=event.club_id, 
            name=event.name, 
            registration_number=event.registration_number,
            owner_id=event.owner_id
        )
        self.club_player_dict[event.club_id] = []
        self.club_collective_list_dict[event.club_id] = []
        # Store ownership information
        self.club_owners[event.club_id] = event.owner_id
        self.club_coaches[event.club_id] = []

    @dispatch(PlayerCreated)
    def _apply(self, event: PlayerCreated) -> None:
        self.club_player_dict[event.club_id].append(event.player_id)
        self.player_dict[event.player_id] = ClubPlayerDTO(player_id=event.player_id, first_name=event.first_name, last_name=event.last_name, gender=event.gender, date_of_birth=event.date_of_birth, license_number=event.license_number, license_type=event.license_type)

    @dispatch(CollectiveCreated)
    def _apply(self, event: CollectiveCreated) -> None:
        self.club_collective_list_dict[event.club_id].append(event.collective_id)
        self.collective_dict[event.collective_id] = DBCollectiveDTO(collective_id=event.collective_id, name=event.name, description=event.description)
        self.collective_player_list_dict[event.collective_id] = []

    @dispatch(PlayerAddedToCollective)
    def _apply(self, event: PlayerAddedToCollective) -> None:
        self.collective_player_list_dict[event.collective_id].append(event.player_id)

    @dispatch(PlayerRemovedFromCollective)
    def _apply(self, event: PlayerRemovedFromCollective) -> None:
        self.collective_player_list_dict[event.collective_id].remove(event.player_id)

    @dispatch(IEvent)
    def _apply(self, event: "IEvent") -> None:
        print(f"Event {event.type} not handled")

    def get_club_players(self, club_id: str) -> list[ClubPlayerDTO]:
        res = []
        for player_id in self.club_player_dict.get(club_id, []):
            res.append(self.player_dict[player_id])
        return res

    def get_club_collectives(self, club_id: str) -> list[CollectiveListDTO]:
        res = []
        for collective_id in self.club_collective_list_dict.get(club_id, []):
            collective = self.collective_dict[collective_id]
            res.append(CollectiveListDTO(
                collective_id=collective.collective_id,
                name=collective.name,
                nb_players=len(self.collective_player_list_dict[collective_id])
            ))
        return res

    def get_collective(self, club_id: str, collective_id: str) -> CollectiveDTO:
        if collective_id not in self.club_collective_list_dict.get(club_id, []):
            return []
        db_collective = self.collective_dict[collective_id]
        collective = CollectiveDTO(
            collective_id=db_collective.collective_id,
            name=db_collective.name,
            description=db_collective.description,
            players=[],
            nb_players = len(self.collective_player_list_dict[collective_id])
        )
        for player_id in self.collective_player_list_dict[collective_id]:
            collective.players.append(self.player_dict[player_id])
        return collective

    def get_club(self, club_id: str) -> ClubDTO | None:
        """Get club information including ownership"""
        return self.club_dict.get(club_id)

    def get_user_club_access(self, user_id: str, club_id: str) -> UserClubAccessDTO | None:
        """Get user's access level to a specific club"""
        club = self.club_dict.get(club_id)
        if not club:
            return None
        
        # Check if user is owner
        if self.club_owners.get(club_id) == user_id:
            return UserClubAccessDTO(
                club_id=club_id,
                name=club.name,
                access_level="owner",
                can_manage=True
            )
        
        # Check if user is coach
        if user_id in self.club_coaches.get(club_id, []):
            return UserClubAccessDTO(
                club_id=club_id,
                name=club.name,
                access_level="coach",
                can_manage=False
            )
        
        # User has no access
        return None

    def can_user_access_club(self, user_id: str, club_id: str) -> bool:
        """Check if user can access a club"""
        return self.get_user_club_access(user_id, club_id) is not None

    def can_user_manage_club(self, user_id: str, club_id: str) -> bool:
        """Check if user can manage a club"""
        access = self.get_user_club_access(user_id, club_id)
        return access is not None and access.can_manage