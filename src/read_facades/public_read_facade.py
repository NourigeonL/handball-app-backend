from multipledispatch import dispatch
from src.common.eventsourcing.event import IEvent
from src.domains.club.events import ClubCreated, CoachAdded
from src.domains.player.events import PlayerCreated
from src.domains.user.events import UserSignedUp
from src.read_facades.dtos import ClubDTO, ClubListDTO
from src.read_facades.interface import IReadFacade


class PublicReadFacade(IReadFacade):
    
    def __init__(self):
        self.club_list : dict[str, ClubListDTO] = {}
        self.club_dict : dict[str, ClubDTO] = {}
        self.user_clubs : dict[str, set[str]] = {}

    @dispatch(ClubCreated)
    def _apply(self, event: ClubCreated) -> None:
        self.club_list[event.club_id] = ClubListDTO(club_id=event.club_id, name=event.name, registration_number=event.registration_number)
        self.user_clubs[event.owner_id].add(event.club_id)
        self.club_dict[event.club_id] = ClubDTO(club_id=event.club_id, name=event.name, registration_number=event.registration_number, owner_id=event.owner_id)

    @dispatch(PlayerCreated)
    def _apply(self, event: PlayerCreated) -> None:
        self.club_list[event.club_id].nb_players += 1

    @dispatch(UserSignedUp)
    def _apply(self, event: UserSignedUp) -> None:
        self.user_clubs[event.user_id] = set()

    @dispatch(CoachAdded)
    def _apply(self, event: CoachAdded) -> None:
        self.user_clubs[event.user_id].add(event.club_id)


    @dispatch(IEvent)
    def _apply(self, event: "IEvent") -> None:
        print(f"Event {event.type} not handled")


    async def get_club_list(self) -> list[ClubListDTO]:
        return list(self.club_list.values())

    async def get_club(self, club_id: str) -> ClubDTO | None:
        return self.club_dict.get(club_id)

    async def get_user_clubs(self, user_id: str) -> list[ClubListDTO]:
        res = []
        for club_id in self.user_clubs.get(user_id, []):
            res.append(self.club_list[club_id])
        return res