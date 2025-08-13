from multipledispatch import dispatch
from src.common.eventsourcing.event import IEvent
from src.domains.club.events import ClubCreated
from src.domains.player.events import PlayerCreated
from src.read_facades.dtos import ClubDTO, ClubListDTO
from src.read_facades.interface import IReadFacade


class PublicReadFacade(IReadFacade):
    
    def __init__(self):
        self.club_list : dict[str, ClubListDTO] = {}
        self.club_dict : dict[str, ClubDTO] = {}

    @dispatch(ClubCreated)
    def _apply(self, event: ClubCreated) -> None:
        self.club_list[event.club_id] = ClubListDTO(club_id=event.club_id, name=event.name, registration_number=event.registration_number)

    @dispatch(PlayerCreated)
    def _apply(self, event: PlayerCreated) -> None:
        self.club_list[event.club_id].nb_players += 1

    @dispatch(IEvent)
    def _apply(self, event: "IEvent") -> None:
        print(f"Event {event.type} not handled")


    def get_club_list(self) -> list[ClubListDTO]:
        return list(self.club_list.values())

    def get_club(self, club_id: str) -> ClubDTO | None:
        return self.club_dict.get(club_id)
