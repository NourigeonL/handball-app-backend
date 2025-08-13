
from contextlib import asynccontextmanager
from typing import Any, AsyncGenerator
from fastapi import FastAPI, HTTPException, Request, status
from pydantic import BaseModel
from src.application.auth.service import AuthService
from src.application.collective.service import CollectiveService
from src.application.player.service import PlayerService
from src.common.eventsourcing.event_stores import IEventStore, JsonFileEventStore
from src.common.cqrs.messages import IEventPublisher
from src.common.eventsourcing.repositories import EventStoreRepository
from src.domains.club.model import Club
from src.domains.collective.model import Collective
from src.domains.player.model import Player
from src.read_facades.club_read_facade import ClubReadFacade
from src.read_facades.public_read_facade import PublicReadFacade
from src.service_locator import service_locator
from jose import jwt, ExpiredSignatureError, JWTError
from src.settings import settings
from src.common.loggers import app_logger
from src.common.cqrs.in_mem_bus import InMemBus
from src.application.club.service import ClubService
sessions = {}



class UserSession(BaseModel):
    user_id: str
    user_email: str


async def get_current_user(request: Request) -> UserSession:
    print(request.cookies)
    access_token = request.cookies.get("access_token")
    print(access_token)
    if not access_token:
        redirect_url = request.url_for("login")
        request.session["login_redirect"] = str(request.url)
        raise HTTPException(
            status_code=status.HTTP_302_FOUND,
            headers={"Location": str(redirect_url)}
        )

    credentials_exception = HTTPException(
        status_code=401,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(access_token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
        print(payload)
        user_id: str = payload.get("sub")
        user_email: str = payload.get("email")

        if user_id is None or user_email is None:
            raise credentials_exception

        return UserSession(user_id=user_id, user_email=user_email)

    except ExpiredSignatureError as e:
        # Specifically handle expired tokens
        redirect_url = request.url_for("login")
        request.session["login_redirect"] = str(request.url)
        raise HTTPException(
            status_code=status.HTTP_302_FOUND,
            headers={"Location": str(redirect_url)}
        )
    except JWTError as e:
        # Handle other JWT-related errors
        app_logger.error(f"JWTError: {e}")
        raise credentials_exception
    except Exception as e:
        app_logger.error(f"Exception: {e}")
        raise HTTPException(status_code=401, detail="Not Authenticated")


async def init_message_broker(message_broker : InMemBus, event_store : IEventStore) -> IEventPublisher:
    return message_broker

@asynccontextmanager
async def lifespan(app : FastAPI)-> AsyncGenerator[Any, None]:
    public_read_facade = PublicReadFacade()
    club_read_facade = ClubReadFacade()
    event_store = JsonFileEventStore("./event_store.json", [public_read_facade, club_read_facade])
    service_locator.public_read_facade = public_read_facade
    service_locator.club_read_facade = club_read_facade
    service_locator.event_publisher = await init_message_broker(InMemBus(), event_store)
    club_repo = EventStoreRepository(event_store, Club)
    auth_service = AuthService()
    service_locator.club_service = ClubService(auth_service, service_locator.event_publisher, club_repo)
    player_repo = EventStoreRepository(event_store, Player)
    service_locator.player_service = PlayerService(auth_service, service_locator.event_publisher, player_repo, club_repo)
    collective_repo = EventStoreRepository(event_store, Collective)
    service_locator.collective_service = CollectiveService(auth_service, service_locator.event_publisher, collective_repo, club_repo)
    yield
    
    