


from src.common.dtos import ClubListDTO
from src.read_facades.db import InMemDB


class PublicReadFacade:
    
    def __init__(self, in_mem_db: InMemDB):
        self.in_mem_db = in_mem_db

    async def get_club_list(self) -> list[ClubListDTO]:
        with self.in_mem_db.get_db() as db:
            return db.club_list

