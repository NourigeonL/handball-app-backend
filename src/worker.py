import os
import threading
import asyncio
from time import sleep

from multipledispatch import dispatch
from src.common.enums import TrainingSessionPlayerStatus
from src.common.eventsourcing.event import IEvent
from src.common.loggers import app_logger
from src.common.eventsourcing.event_stores import IEventStore
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy import select

from src.domains.club import events as club_events
from src.domains.player import events as player_events
from src.domains.user import events as user_events
from src.domains.collective import events as collective_events
from src.domains.training_session import events as training_session_events
from src.infrastructure.storages.sql_model import Club, Collective, CollectivePlayer, LastRecordedEventPosition, Base, Player, TrainingSession, TrainingSessionPlayer, User
from src.service_locator import service_locator

class Worker:
    def __init__(self, event_store: IEventStore, url: str):
        self.event_store = event_store
        self.url = url
        self.async_engine = create_async_engine(url, 
                                                echo=False, 
                                                pool_size=10,
                                                max_overflow=20,
                                                pool_pre_ping=True,
                                                pool_recycle=3600)
        self.async_session_maker = async_sessionmaker(self.async_engine, expire_on_commit=False)
        self.__stop = False
        self.__last_recorded_event_position = 0

    async def init_db(self) -> None:
        metadata = Base.metadata
        db_path = self.url.split(":///")[1]
        app_logger.info(f"DB path: {db_path}")
        if os.path.exists(db_path):
            os.remove(db_path)

        # 2. Recreate schema
        async with self.async_engine.begin() as conn:
            await conn.run_sync(metadata.create_all)

    async def callback(self) -> None:
        current_commit_position = await self.event_store.get_last_commit_position()
        if current_commit_position != self.__last_recorded_event_position:
            subscription = await self.event_store.get_all_events_from_position(self.__last_recorded_event_position)
            try:
                async with self.async_session_maker() as session:
                    if len(subscription) == 0:
                        return
                    for event in subscription:
                        app_logger.debug(f"Processing event {event.event_id} : {event.type}")
                        self.__last_recorded_event_position = self.__last_recorded_event_position+1
                        await self.handle(event, session)
                        await session.commit()
                        await self.save_last_recorded_event_position()
                        if current_commit_position == self.__last_recorded_event_position:
                            break
            except Exception as e:
                app_logger.error(e)

    async def get_last_recorded_event_position(self) -> None:
        async with self.async_session_maker() as session:
            result = await session.execute(select(LastRecordedEventPosition))
            last_recorded_event_position = result.scalar_one_or_none()
            if last_recorded_event_position:
                self.__last_recorded_event_position = last_recorded_event_position.position
            else:
                self.__last_recorded_event_position = 0

    async def save_last_recorded_event_position(self) -> None:
        async with self.async_session_maker() as session:
            await session.merge(LastRecordedEventPosition(id=1, position=self.__last_recorded_event_position))
            await session.commit()

    def stop(self) -> None:
        self.__stop = True

    async def start(self):
        app_logger.info("Worker starts running")
        await self.init_db()
        await self.get_last_recorded_event_position()
        while not self.__stop:
            await self.callback()
            await asyncio.sleep(1)
        app_logger.info("Worker stopped running")


    @dispatch(IEvent, AsyncSession)
    async def handle(self, event: "IEvent", session: AsyncSession) -> None:
        app_logger.error(f"Event {event.type} {event.event_id} not handled")

    @dispatch(club_events.ClubCreated, AsyncSession)
    async def handle(self, event: club_events.ClubCreated, session: AsyncSession) -> None:
        app_logger.info(f"ClubCreated: {event.club_id}")
        club = Club(id=event.club_id, name=event.name, registration_number=event.registration_number, owner_id=event.owner_id)
        session.add(club)
        await session.merge(club)

    @dispatch(club_events.ClubOwnerChanged, AsyncSession)
    async def handle(self, event: club_events.ClubOwnerChanged, session: AsyncSession) -> None:
        app_logger.info(f"ClubOwnerChanged: {event.club_id}")
        club = await session.get(Club, event.club_id)
        if club:
            club.owner_id = event.new_owner_id
            await session.merge(club)


    @dispatch(user_events.UserSignedUp, AsyncSession)
    async def handle(self, event: user_events.UserSignedUp, session: AsyncSession) -> None:
        app_logger.info(f"UserSignedUp: {event.user_id}")
        user = User(id=event.user_id, name=event.name, email=event.email, first_name=event.first_name, last_name=event.last_name)
        session.add(user)
        await session.merge(user)

    @dispatch(user_events.UserNameUpdated, AsyncSession)
    async def handle(self, event: user_events.UserNameUpdated, session: AsyncSession) -> None:
        app_logger.info(f"UserNameUpdated: {event.user_id}")
        user = await session.get(User, event.user_id)
        if user:
            user.name = event.name
            user.first_name = event.first_name
            user.last_name = event.last_name
            await session.merge(user)

    @dispatch(player_events.PlayerRegistered, AsyncSession)
    async def handle(self, event: player_events.PlayerRegistered, session: AsyncSession) -> None:
        app_logger.info(f"PlayerRegistered: {event.player_id}")
        player = Player(id=event.player_id, first_name=event.first_name, last_name=event.last_name, gender=event.gender, date_of_birth=event.date_of_birth, license_number=event.license_number)
        await session.merge(player)

    @dispatch(player_events.PlayerRegisteredToClub, AsyncSession)
    async def handle(self, event: player_events.PlayerRegisteredToClub, session: AsyncSession) -> None:
        app_logger.info(f"PlayerRegisteredToClub: {event.player_id}")
        player = await session.get(Player, event.player_id)
        if player:
            player.club_id = event.club_id
            player.season = event.season
            player.license_type = event.license_type
            await session.merge(player)
        club = await session.get(Club, event.club_id)
        if club:
            club.number_of_players = club.number_of_players + 1
            await session.merge(club)
        await service_locator.websocket_manager.send_message(event.club_id, {"type": "club_player_list_updated"})

    @dispatch(player_events.PlayerUnregisteredFromClub, AsyncSession)
    async def handle(self, event: player_events.PlayerUnregisteredFromClub, session: AsyncSession) -> None:
        app_logger.info(f"PlayerUnregisteredFromClub: {event.player_id}")
        player = await session.get(Player, event.player_id)
        if player:
            player.club_id = None
            await session.merge(player)
        club = await session.get(Club, event.club_id)
        if club:
            club.number_of_players = club.number_of_players - 1
            await session.merge(club)
        await service_locator.websocket_manager.send_message(event.club_id, {"type": "club_player_list_updated"})
    @dispatch(collective_events.CollectiveCreated, AsyncSession)
    async def handle(self, event: collective_events.CollectiveCreated, session: AsyncSession) -> None:
        app_logger.info(f"CollectiveCreated: {event.collective_id}")
        collective = Collective(id=event.collective_id, club_id=event.club_id, name=event.name, description=event.description)
        session.add(collective)
        await session.merge(collective)
        await service_locator.websocket_manager.send_message(event.club_id, {"type": "club_collective_list_updated"})

    @dispatch(collective_events.PlayerAddedToCollective, AsyncSession)
    async def handle(self, event: collective_events.PlayerAddedToCollective, session: AsyncSession) -> None:
        app_logger.info(f"PlayerAddedToCollective: {event.collective_id}")
        collective_player = await session.execute(select(CollectivePlayer).where(CollectivePlayer.collective_id == event.collective_id, CollectivePlayer.player_id == event.player_id))
        collective_player = collective_player.scalar_one_or_none()
        if collective_player is None:
            collective_player = CollectivePlayer(collective_id=event.collective_id, player_id=event.player_id)
            session.add(collective_player)
            await session.merge(collective_player)
        collective = await session.get(Collective, event.collective_id)
        if collective:
            collective.number_of_players = collective.number_of_players + 1
            await session.merge(collective)
        await service_locator.websocket_manager.send_message(collective.club_id, {"type": "club_collective_list_updated"})

    @dispatch(collective_events.PlayerRemovedFromCollective, AsyncSession)
    async def handle(self, event: collective_events.PlayerRemovedFromCollective, session: AsyncSession) -> None:
        app_logger.info(f"PlayerRemovedFromCollective: {event.collective_id}")
        collective_player = await session.execute(select(CollectivePlayer).where(CollectivePlayer.collective_id == event.collective_id, CollectivePlayer.player_id == event.player_id))
        collective_player = collective_player.scalar_one_or_none()
        if collective_player:
            await session.delete(collective_player)
            await session.commit()
        collective = await session.get(Collective, event.collective_id)
        if collective:
            collective.number_of_players = collective.number_of_players - 1
            await session.merge(collective)
        await service_locator.websocket_manager.send_message(collective.club_id, {"type": "club_collective_list_updated"})

    @dispatch(training_session_events.TrainingSessionCreated, AsyncSession)
    async def handle(self, event: training_session_events.TrainingSessionCreated, session: AsyncSession) -> None:
        app_logger.info(f"TrainingSessionCreated: {event.training_session_id}")
        training_session = TrainingSession(id=event.training_session_id, club_id=event.club_id, start_time=event.start_time, end_time=event.end_time)
        session.add(training_session)
        await session.merge(training_session)
        await service_locator.websocket_manager.send_message(event.club_id, {"type": "club_training_session_list_updated"})

    @dispatch(training_session_events.PlayerTrainingSessionStatusChangedToPresent, AsyncSession)
    async def handle(self, event: training_session_events.PlayerTrainingSessionStatusChangedToPresent, session: AsyncSession) -> None:
        training_session = await session.get(TrainingSession, event.training_session_id)
        training_session_player = await session.execute(select(TrainingSessionPlayer).where(TrainingSessionPlayer.training_session_id == event.training_session_id, TrainingSessionPlayer.player_id == event.player_id))
        training_session_player = training_session_player.scalar_one_or_none()
        if training_session_player:
            match training_session_player.status:
                case TrainingSessionPlayerStatus.PRESENT:
                    return
                case TrainingSessionPlayerStatus.ABSENT:
                    training_session.number_of_players_absent -= 1
                case TrainingSessionPlayerStatus.LATE:
                    training_session.number_of_players_late -= 1
            await session.merge(training_session_player)
            training_session_player.status = TrainingSessionPlayerStatus.PRESENT
            training_session_player.reason = None
            training_session_player.with_reason = False
            training_session_player.arrival_time = None
            await session.merge(training_session_player)
        else:
            training_session_player = TrainingSessionPlayer(training_session_id=event.training_session_id, player_id=event.player_id, status=TrainingSessionPlayerStatus.PRESENT)
        app_logger.info(f"PlayerTrainingSessionStatusChangedToPresent: {event.training_session_id}")
        
        training_session.number_of_players_present += 1
        await session.merge(training_session)
        await service_locator.websocket_manager.send_message(event.club_id, {"type": "club_training_session_updated"})
        await service_locator.websocket_manager.send_message(event.club_id, {"type": "club_training_session_list_updated"})
        
    @dispatch(training_session_events.PlayerTrainingSessionStatusChangedToAbsent, AsyncSession)
    async def handle(self, event: training_session_events.PlayerTrainingSessionStatusChangedToAbsent, session: AsyncSession) -> None:
        training_session = await session.get(TrainingSession, event.training_session_id)
        training_session_player = await session.execute(select(TrainingSessionPlayer).where(TrainingSessionPlayer.training_session_id == event.training_session_id, TrainingSessionPlayer.player_id == event.player_id))
        training_session_player = training_session_player.scalar_one_or_none()
        if training_session_player:
            match training_session_player.status:
                case TrainingSessionPlayerStatus.PRESENT:
                    training_session.number_of_players_present -= 1
                case TrainingSessionPlayerStatus.ABSENT:
                    return
                case TrainingSessionPlayerStatus.LATE:
                    training_session.number_of_players_late -= 1
            await session.merge(training_session_player)
            training_session_player.status = TrainingSessionPlayerStatus.ABSENT
            training_session_player.reason = event.reason
            training_session_player.with_reason = event.with_reason
            training_session_player.arrival_time = None
            await session.merge(training_session_player)
        else:
            training_session_player = TrainingSessionPlayer(training_session_id=event.training_session_id, player_id=event.player_id, status=TrainingSessionPlayerStatus.ABSENT, reason=event.reason, with_reason=event.with_reason)
        app_logger.info(f"PlayerTrainingSessionStatusChangedToAbsent: {event.training_session_id}")
        
        training_session.number_of_players_absent += 1
        await session.merge(training_session)
        await service_locator.websocket_manager.send_message(event.club_id, {"type": "club_training_session_updated"})
        await service_locator.websocket_manager.send_message(event.club_id, {"type": "club_training_session_list_updated"})
    
    @dispatch(training_session_events.PlayerTrainingSessionStatusChangedToLate, AsyncSession)
    async def handle(self, event: training_session_events.PlayerTrainingSessionStatusChangedToLate, session: AsyncSession) -> None:
        training_session = await session.get(TrainingSession, event.training_session_id)
        training_session_player = await session.execute(select(TrainingSessionPlayer).where(TrainingSessionPlayer.training_session_id == event.training_session_id, TrainingSessionPlayer.player_id == event.player_id))
        training_session_player = training_session_player.scalar_one_or_none()
        if training_session_player:
            match training_session_player.status:
                case TrainingSessionPlayerStatus.PRESENT:
                    training_session.number_of_players_present -= 1
                case TrainingSessionPlayerStatus.ABSENT:
                    training_session.number_of_players_absent -= 1
                case TrainingSessionPlayerStatus.LATE:
                    training_session.number_of_players_late -= 1
            await session.merge(training_session_player)
            training_session_player.status = TrainingSessionPlayerStatus.LATE
            training_session_player.reason = event.reason
            training_session_player.with_reason = event.with_reason
            training_session_player.arrival_time = event.arrival_time
            await session.merge(training_session_player)
        else:
            training_session_player = TrainingSessionPlayer(training_session_id=event.training_session_id, player_id=event.player_id, status=TrainingSessionPlayerStatus.LATE, reason=event.reason, with_reason=event.with_reason, arrival_time=event.arrival_time)
        app_logger.info(f"PlayerTrainingSessionStatusChangedToLate: {event.training_session_id}")
        
        training_session.number_of_players_late += 1
        await session.merge(training_session)
        await service_locator.websocket_manager.send_message(event.club_id, {"type": "club_training_session_updated"})
        await service_locator.websocket_manager.send_message(event.club_id, {"type": "club_training_session_list_updated"})