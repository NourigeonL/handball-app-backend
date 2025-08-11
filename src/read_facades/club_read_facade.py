from src.read_facades.db import InMemDB


class ClubReadFacade:

    def __init__(self, in_mem_db: InMemDB, club_id: str):
        self.in_mem_db = in_mem_db
        self.club_id = club_id