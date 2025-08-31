
import asyncio
from contextlib import asynccontextmanager
from typing import Annotated, Any, AsyncGenerator
from fastapi import Cookie, FastAPI, HTTPException, Request, status, Depends
from pydantic import BaseModel
from src.application.auth.service import AuthService
from src.application.collective.service import CollectiveService
from src.application.player.service import PlayerService
from src.common.eventsourcing.event_stores import IEventStore, JsonFileEventStore
from src.common.cqrs.messages import IEventPublisher
from src.common.eventsourcing.repositories import EventStoreRepository
from src.domains.club.model import Club
from src.domains.collective.model import Collective
from src.domains.federation.model import Federation
from src.domains.player.model import Player
from src.domains.user.model import User
from src.infrastructure.session_manager import Session, SessionManager
from src.infrastructure.storages.auth_repository import AuthRepository
from src.read_facades.club_read_facade import ClubReadFacade
from src.read_facades.public_read_facade import PublicReadFacade
from src.service_locator import service_locator
from src.settings import settings
from src.common.loggers import app_logger
from src.common.cqrs.in_mem_bus import InMemBus
from src.application.club.service import ClubService
from src.worker import Worker
sessions = {}

async def get_current_user_from_session(request: Request) -> Session:
    """
    Get current user from session cookie
    """
    session_id = request.cookies.get("session_id")
    
    if not session_id:
        # No session cookie found, redirect to login
        redirect_url = request.url_for("login")
        raise HTTPException(
            status_code=status.HTTP_302_FOUND,
            detail="No session found. Redirecting to login.",
            headers={"Location": str(redirect_url)},
        )
    
    session = await service_locator.session_manager.get_session(session_id)
    if session is None:
        # Invalid or expired session, redirect to login
        redirect_url = request.url_for("login")
        raise HTTPException(
            status_code=status.HTTP_302_FOUND,
            detail="Invalid or expired session. Redirecting to login.",
            headers={"Location": str(redirect_url)},
        )
    
    return session


async def check_club_access(
    club_id: str,
    current_user: Session = Depends(get_current_user_from_session)
) -> Session:
    """
    Dependency to check if the current user has access to a specific club.
    Raises HTTPException if access is denied.
    Returns the current user session if access is granted.
    """
    if not current_user.club_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, 
            detail="You are not logged into any club. Please log into a club first."
        )
    
    if club_id != current_user.club_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, 
            detail="You are not authorized to access this club"
        )
    
    return current_user


async def check_club_access_optional(
    club_id: str | None = None,
    current_user: Session = Depends(get_current_user_from_session)
) -> Session:
    """
    Optional dependency to check club access.
    If no club_id is provided, just returns the current user.
    If club_id is provided, validates access to that club.
    """
    if club_id is None:
        return current_user
    
    return await check_club_access(club_id, current_user)


async def init_message_broker(message_broker : InMemBus, event_store : IEventStore) -> IEventPublisher:
    return message_broker

@asynccontextmanager
async def lifespan(app : FastAPI)-> AsyncGenerator[Any, None]:
    db_url = "sqlite+aiosqlite:///read_model.db"
    public_read_facade = PublicReadFacade(db_url)
    club_read_facade = ClubReadFacade(db_url)
    event_store = JsonFileEventStore("./event_store.json", [public_read_facade, club_read_facade])
    service_locator.public_read_facade = public_read_facade
    service_locator.club_read_facade = club_read_facade
    service_locator.event_publisher = await init_message_broker(InMemBus(), event_store)
    club_repo = EventStoreRepository(event_store, Club)
    auth_repo = AuthRepository("./auth_repository.json")
    user_repo = EventStoreRepository(event_store, User)
    federation_repo = EventStoreRepository(event_store, Federation)
    auth_service = AuthService(auth_repo, user_repo, club_repo)
    worker = Worker(event_store, db_url)
    service_locator.club_service = ClubService(auth_service, service_locator.event_publisher, club_repo)
    player_repo = EventStoreRepository(event_store, Player)
    service_locator.player_service = PlayerService(auth_service, service_locator.event_publisher, player_repo, club_repo, federation_repo)
    collective_repo = EventStoreRepository(event_store, Collective)
    service_locator.collective_service = CollectiveService(auth_service, service_locator.event_publisher, collective_repo, club_repo)
    service_locator.auth_service = auth_service
    service_locator.session_manager = SessionManager()
    asyncio.create_task(worker.start())
    yield
    worker.stop()
    
    