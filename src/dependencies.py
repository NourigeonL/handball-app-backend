
from contextlib import asynccontextmanager
from typing import Any, AsyncGenerator
from fastapi import FastAPI, HTTPException, Request, status
from pydantic import BaseModel
from src.eventsourcing.event_stores import IEventStore, JsonFileEventStore
from src.eventsourcing.exceptions import AggregateNotFoundError
from src.eventsourcing.messages import IMessageBroker
from src.eventsourcing.repositories import EventStoreRepository
from src.features.club.aggregates import Club
from src.features.club.application import ClubIntegrationEventHandler
from src.features.federation.aggregates import Federation
from src.features.federation.commands import FederationCommandHandler, RegisterClub
from src.features.federation import integration_events as federation_integration_events
from src.read_facades.db import InMemDB
from src.read_facades.public_read_facade import PublicReadFacade
from src.service_locator import service_locator
from jose import jwt, ExpiredSignatureError, JWTError
from src.settings import settings
from src.common.loggers import app_logger
from src.in_mem_bus import InMemBus
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


async def init_message_broker(message_broker : InMemBus, event_store : IEventStore) -> IMessageBroker:
    federation_repo = EventStoreRepository(event_store, Federation)
    try:
        await federation_repo.get_by_id(Federation.to_stream_id())
    except AggregateNotFoundError:
        await federation_repo.save(Federation(), -1)
    federation_command_handler = FederationCommandHandler(federation_repo, message_broker)
    club_repo = EventStoreRepository(event_store, Club)
    club_integration_event_handler = ClubIntegrationEventHandler(club_repo, message_broker)

    message_broker.register_handler(RegisterClub, federation_command_handler)
    message_broker.register_handler(federation_integration_events.IEClubRegistered, club_integration_event_handler)

    return message_broker

@asynccontextmanager
async def lifespan(app : FastAPI)-> AsyncGenerator[Any, None]:
    event_store = JsonFileEventStore("./event_store.json")
    in_mem_db = InMemDB(event_store.file_path)
    service_locator.public_read_facade = PublicReadFacade(in_mem_db)
    service_locator.message_broker = await init_message_broker(InMemBus(), event_store)
    yield
    
    