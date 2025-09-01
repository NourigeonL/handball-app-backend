from multipledispatch import dispatch
from pydantic import BaseModel
from sqlalchemy import or_, select
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from sqlalchemy.orm import joinedload
from src.common.eventsourcing.event import IEvent
from src.common.exceptions import NotFoundError
from src.domains.club.events import ClubCreated
from src.domains.collective.events import CollectiveCreated, PlayerAddedToCollective, PlayerRemovedFromCollective
from src.domains.player.events import PlayerRegistered
from src.infrastructure.storages.sql_model import Club, Collective, CollectivePlayer, Player, TrainingSession, TrainingSessionPlayer
from src.read_facades.dtos import ClubDTO, ClubPlayerDTO, CollectiveDTO, CollectiveListDTO, CollectivePlayerDTO, TrainingSessionDTO, TrainingSessionPlayerDTO, UserClubAccessDTO
from src.read_facades.interface import IReadFacade
from src.read_facades.pagination import PaginatedDTO, paginate


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

    async def club_players(self, club_id: str, page: int = 0, per_page: int = 10) -> PaginatedDTO[ClubPlayerDTO]:
        async with self.async_session_maker() as session:
            result = await paginate(select(Player).where(Player.club_id == club_id), page, per_page, session)
            players_dict = {player.id : ClubPlayerDTO(player_id=player.id, first_name=player.first_name, last_name=player.last_name, gender=player.gender, date_of_birth=player.date_of_birth, license_number=player.license_number, license_type=player.license_type, collectives=[]) for player in result.items}
            collectives = await session.execute(select(CollectivePlayer).options(joinedload(CollectivePlayer.collective)).where(CollectivePlayer.player_id.in_(players_dict.keys())))
            for collective_player in collectives.scalars().all():
                players_dict[collective_player.player_id].collectives.append(CollectiveListDTO(collective_id=collective_player.collective_id, name=collective_player.collective.name, nb_players=collective_player.collective.number_of_players, description=collective_player.collective.description))
            return PaginatedDTO(total_count=result.total_items, total_page=result.total_pages, count=len(players_dict), page=page, results=list(players_dict.values()))
    
    async def get_collective(self, club_id: str, collective_id: str) -> CollectiveDTO:
        async with self.async_session_maker() as session:
            result = await session.execute(select(Collective).where(Collective.id == collective_id, Collective.club_id == club_id))
            collective = result.scalars().first()
            if collective:
                return CollectiveDTO(collective_id=collective.id, name=collective.name, description=collective.description, nb_players=collective.number_of_players)
            return None


    async def get_collective_players(self, club_id: str, collective_id: str, page: int = 0, per_page: int = 10) -> PaginatedDTO[CollectivePlayerDTO]:
        async with self.async_session_maker() as session:
            stmt = select(Player).join(CollectivePlayer).where(CollectivePlayer.collective_id == collective_id, Player.club_id == club_id)
            result = await paginate(stmt, page, per_page, session)
            results=[CollectivePlayerDTO(player_id=player.id, first_name=player.first_name, last_name=player.last_name, gender=player.gender, date_of_birth=player.date_of_birth, license_number=player.license_number, license_type=player.license_type) for player in result.items]
            return PaginatedDTO(total_count=result.total_items, total_page=result.total_pages, count=len(results), page=page, results=results)

    async def get_user_club_access(self, user_id: str, club_id: str) -> UserClubAccessDTO:
        async with self.async_session_maker() as session:
            result = await session.execute(select(Club).where(Club.id == club_id, Club.owner_id == user_id))
            club = result.scalars().first()
            if club:
                return UserClubAccessDTO(club_id=club.id, name=club.name, access_level="owner", can_manage=True)
            return None

    async def search_players(self, club_id: str, search_query: str) -> CollectivePlayerDTO:
        async with self.async_session_maker() as session:
            result = await session.execute(select(Player).where(Player.club_id == club_id, or_(Player.first_name.ilike(f"%{search_query}%"), Player.last_name.ilike(f"%{search_query}%"), Player.license_number.ilike(f"%{search_query}%"))).order_by(Player.last_name, Player.first_name))
            return [CollectivePlayerDTO(player_id=player.id, first_name=player.first_name, last_name=player.last_name, gender=player.gender, date_of_birth=player.date_of_birth, license_number=player.license_number, license_type=player.license_type) for player in result.scalars().all()]

    async def search_unassigned_players_in_collective(self, club_id: str, collective_id: str, search_query: str) -> list[CollectivePlayerDTO]:
        async with self.async_session_maker() as session:
            result = await session.execute(select(Player).where(Player.club_id == club_id, Player.id.notin_(select(CollectivePlayer.player_id).where(CollectivePlayer.collective_id == collective_id)), or_(Player.first_name.ilike(f"%{search_query}%"), Player.last_name.ilike(f"%{search_query}%"), Player.license_number.ilike(f"%{search_query}%"))).order_by(Player.last_name, Player.first_name))
            return [CollectivePlayerDTO(player_id=player.id, first_name=player.first_name, last_name=player.last_name, gender=player.gender, date_of_birth=player.date_of_birth, license_number=player.license_number, license_type=player.license_type) for player in result.scalars().all()]

    async def get_training_session(self, club_id: str, training_session_id: str) -> TrainingSessionDTO | None:
        async with self.async_session_maker() as session:
            result = await session.execute(select(TrainingSession).where(TrainingSession.id == training_session_id, TrainingSession.club_id == club_id))
            training_session = result.scalar_one_or_none()
            if training_session:
                return TrainingSessionDTO(training_session_id=training_session.id, start_time=training_session.start_time, end_time=training_session.end_time, number_of_players_present=training_session.number_of_players_present, number_of_players_absent=training_session.number_of_players_absent, number_of_players_late=training_session.number_of_players_late )
            raise NotFoundError(f"Training session {training_session_id} not found")

    async def get_training_session_list(self, club_id: str, page: int = 0, per_page: int = 10) -> PaginatedDTO[TrainingSessionDTO]:
        async with self.async_session_maker() as session:
            result = await paginate(select(TrainingSession).where(TrainingSession.club_id == club_id).order_by(TrainingSession.start_time.desc()), page, per_page, session)
            return PaginatedDTO(total_count=result.total_items, total_page=result.total_pages, count=len(result.items), page=page, results=[TrainingSessionDTO(training_session_id=training_session.id, start_time=training_session.start_time, end_time=training_session.end_time, number_of_players_present=training_session.number_of_players_present, number_of_players_absent=training_session.number_of_players_absent, number_of_players_late=training_session.number_of_players_late) for training_session in result.items])

    async def get_training_session_players(self, club_id: str, training_session_id: str, page: int = 0, per_page: int = 10) -> PaginatedDTO[TrainingSessionPlayerDTO]:
        async with self.async_session_maker() as session:
            result = await paginate(select(TrainingSessionPlayer).options(joinedload(TrainingSessionPlayer.player), joinedload(TrainingSessionPlayer.training_session)).where(TrainingSessionPlayer.training_session_id == training_session_id, TrainingSession.club_id == club_id), page, per_page, session)
            return PaginatedDTO(total_count=result.total_items, total_page=result.total_pages, count=len(result.items), page=page, results=[TrainingSessionPlayerDTO(training_session_id=training_session_player.training_session_id, player=ClubPlayerDTO(player_id=training_session_player.player.id, first_name=training_session_player.player.first_name, last_name=training_session_player.player.last_name, gender=training_session_player.player.gender, date_of_birth=training_session_player.player.date_of_birth, license_number=training_session_player.player.license_number, license_type=training_session_player.player.license_type), status=training_session_player.status) for training_session_player in result.items])

    async def search_players_not_in_training_session(self, club_id: str, training_session_id: str, collective_id: str | None = None, search_query: str = "") -> list[ClubPlayerDTO]:
        async with self.async_session_maker() as session:
            stmt = select(Player).where(Player.club_id == club_id, Player.id.notin_(select(TrainingSessionPlayer.player_id).where(TrainingSessionPlayer.training_session_id == training_session_id)))
            if collective_id:
                stmt = stmt.where(Player.id.in_(select(CollectivePlayer.player_id).where(CollectivePlayer.collective_id == collective_id)))
            if search_query:
                stmt = stmt.where(or_(Player.first_name.ilike(f"%{search_query}%"), Player.last_name.ilike(f"%{search_query}%"), Player.license_number.ilike(f"%{search_query}%")))
            result = await session.execute(stmt)
            players_dict = {player.id : ClubPlayerDTO(player_id=player.id, first_name=player.first_name, last_name=player.last_name, gender=player.gender, date_of_birth=player.date_of_birth, license_number=player.license_number, license_type=player.license_type, collectives=[]) for player in result.scalars().all()}
            collectives = await session.execute(select(CollectivePlayer).options(joinedload(CollectivePlayer.collective)).where(CollectivePlayer.player_id.in_(players_dict.keys())))
            for collective_player in collectives.scalars().all():
                players_dict[collective_player.player_id].collectives.append(CollectiveListDTO(collective_id=collective_player.collective_id, name=collective_player.collective.name, nb_players=collective_player.collective.number_of_players, description=collective_player.collective.description))
            return list(players_dict.values())  