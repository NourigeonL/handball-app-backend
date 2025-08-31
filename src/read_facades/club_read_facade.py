from multipledispatch import dispatch
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from sqlalchemy.orm import joinedload
from src.common.eventsourcing.event import IEvent
from src.domains.club.events import ClubCreated
from src.domains.collective.events import CollectiveCreated, PlayerAddedToCollective, PlayerRemovedFromCollective
from src.domains.player.events import PlayerRegistered
from src.infrastructure.storages.sql_model import Collective, CollectivePlayer, Player
from src.read_facades.dtos import ClubDTO, ClubPlayerDTO, CollectiveDTO, CollectiveListDTO, UserClubAccessDTO
from src.read_facades.interface import IReadFacade


class DBCollectiveDTO(BaseModel):
    collective_id: str
    name: str
    description: str | None = None

class ClubReadFacade(IReadFacade):

    def __init__(self, url: str):
        self.url = url
        self.async_engine = create_async_engine(url, 
                                                echo=False, 
                                                pool_size=10,
                                                max_overflow=20,
                                                pool_pre_ping=True,
                                                pool_recycle=3600)
        self.async_session_maker = async_sessionmaker(self.async_engine, expire_on_commit=False)

    async def get_collective_list(self, club_id: str) -> list[CollectiveListDTO]:
        async with self.async_session_maker() as session:
            result = await session.execute(select(Collective).where(Collective.club_id == club_id).order_by(Collective.name))
            return [CollectiveListDTO(collective_id=collective.id, name=collective.name, nb_players=collective.number_of_players, description=collective.description) for collective in result.scalars().all()]

    async def club_players(self, club_id: str) -> list[ClubPlayerDTO]:
        async with self.async_session_maker() as session:
            result = await session.execute(select(Player).where(Player.club_id == club_id))
            players_dict = {player.id : ClubPlayerDTO(player_id=player.id, first_name=player.first_name, last_name=player.last_name, gender=player.gender, date_of_birth=player.date_of_birth, license_number=player.license_number, license_type=player.license_type, collectives=[]) for player in result.scalars().all()}
            result = await session.execute(select(CollectivePlayer).options(joinedload(CollectivePlayer.collective)).where(CollectivePlayer.player_id.in_(players_dict.keys())))
            for collective_player in result.scalars().all():
                players_dict[collective_player.player_id].collectives.append(CollectiveListDTO(collective_id=collective_player.collective_id, name=collective_player.collective.name, nb_players=collective_player.collective.number_of_players, description=collective_player.collective.description))
            return list(players_dict.values())
