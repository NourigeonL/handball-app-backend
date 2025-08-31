from multipledispatch import dispatch
from sqlalchemy import select
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from sqlalchemy.orm import joinedload
from src.common.eventsourcing.event import IEvent
from src.domains.club.events import ClubCreated, CoachAdded
from src.domains.player.events import PlayerRegistered
from src.domains.user.events import UserSignedUp
from src.infrastructure.storages.sql_model import Club, Player
from src.read_facades.dtos import ClubDTO, PublicClubDTO, PublicPlayerDTO
from src.read_facades.interface import IReadFacade


class PublicReadFacade(IReadFacade):
    
    def __init__(self, url: str):
        self.url = url
        self.async_engine = create_async_engine(url, 
                                                echo=False, 
                                                pool_size=10,
                                                max_overflow=20,
                                                pool_pre_ping=True,
                                                pool_recycle=3600)
        self.async_session_maker = async_sessionmaker(self.async_engine, expire_on_commit=False)

    async def get_club_list(self) -> list[PublicClubDTO]:
        async with self.async_session_maker() as session:
            result = await session.execute(select(Club).order_by(Club.name))
            return [PublicClubDTO(club_id=club.id, name=club.name, registration_number=club.registration_number, nb_players=club.number_of_players) for club in result.scalars().all()]

    async def get_club(self, club_id: str) -> ClubDTO | None:
        async with self.async_session_maker() as session:
            result = await session.execute(select(Club).where(Club.id == club_id))
            club = result.scalars().first()
            if club:
                return ClubDTO(club_id=club.id, name=club.name, registration_number=club.registration_number, nb_players=club.number_of_players)
            return None

    async def get_user_clubs(self, user_id: str) -> list[PublicClubDTO]:
        res = []
        async with self.async_session_maker() as session:
            result = await session.execute(select(Club).where(Club.owner_id == user_id))
            for club in result.scalars().all():
                res.append(PublicClubDTO(club_id=club.id, name=club.name, registration_number=club.registration_number, nb_players=club.number_of_players))
        return res

    async def get_player_list(self) -> list[PublicPlayerDTO]:
        async with self.async_session_maker() as session:
            result = await session.execute(select(Player).options(joinedload(Player.club)))
            return [PublicPlayerDTO(player_id=player.id, first_name=player.first_name, last_name=player.last_name, club=PublicClubDTO(club_id=player.club_id, name=player.club.name, registration_number=player.club.registration_number, nb_players=player.club.number_of_players), gender=player.gender, date_of_birth=player.date_of_birth, license_number=player.license_number, license_type=player.license_type) for player in result.scalars().all()]