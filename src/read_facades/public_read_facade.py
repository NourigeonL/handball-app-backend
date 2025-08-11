
from src.read_facades.db import InMemDB
from src.read_facades.dtos import ClubListDTO


class PublicReadFacade:
    
    def __init__(self, in_mem_db: InMemDB):
        self.in_mem_db = in_mem_db

    async def get_club_list(self) -> list[ClubListDTO]:
        with self.in_mem_db.get_db() as db:
            return [ClubListDTO(registration_number=club.registration_number, name=club.name) for club in db.club_list.values()]

