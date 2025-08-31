from typing import Annotated
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import JSONResponse
from httpx import get
from pydantic import BaseModel
from src.dependencies import check_club_access, get_current_user_from_session
from src.read_facades.dtos import CollectiveDTO, CollectiveListDTO, CollectivePlayerDTO
from src.read_facades.pagination import PaginatedDTO
from src.service_locator import service_locator
from src.application.collective.commands import CreateCollectiveCommand, AddPlayerToCollectiveCommand, RemovePlayerFromCollectiveCommand
from src.infrastructure.session_manager import Session
from src.common.loggers import app_logger

router = APIRouter(prefix="/collectives", tags=["collectives"])

class CollectiveCreateRequest(BaseModel):
    name: str
    description: str | None = None

@router.post("/create")
async def create_collective(
    collective_create_request: CollectiveCreateRequest, 
    current_user: Session = Depends(get_current_user_from_session)
):
    app_logger.info(f"Creating collective {collective_create_request.name}")
    await service_locator.collective_service.handle(CreateCollectiveCommand(
        actor_id=current_user.user_id, 
        name=collective_create_request.name, 
        description=collective_create_request.description,
        club_id=current_user.club_id,
    ))
    return JSONResponse(status_code=201, content={"message": "Collective created successfully"})

class AddPlayerToCollectiveRequest(BaseModel):
    player_id: str

@router.post("/{collective_id}/add-player")
async def add_player_to_collective(
    collective_id: str,
    add_player_request: AddPlayerToCollectiveRequest, 
    current_user: Session = Depends(get_current_user_from_session)
):
    app_logger.info(f"Adding player {add_player_request.player_id} to collective {collective_id}")
    await service_locator.collective_service.handle(AddPlayerToCollectiveCommand(
        actor_id=current_user.user_id, 
        player_id=add_player_request.player_id, 
        collective_id=collective_id,
        club_id=current_user.club_id,
    ))
    return JSONResponse(status_code=200, content={"message": "Player added to collective successfully"})

class RemovePlayerFromCollectiveRequest(BaseModel):
    player_id: str

@router.post("/{collective_id}/remove-player")
async def remove_player_from_collective(
    collective_id: str,
    remove_player_request: RemovePlayerFromCollectiveRequest, 
    current_user: Session = Depends(get_current_user_from_session)
):
    app_logger.info(f"Removing player {remove_player_request.player_id} from collective {collective_id}")
    await service_locator.collective_service.handle(RemovePlayerFromCollectiveCommand(
        actor_id=current_user.user_id, 
        player_id=remove_player_request.player_id, 
        collective_id=collective_id,
        club_id=current_user.club_id,
    ))
    return JSONResponse(status_code=200, content={"message": "Player removed from collective successfully"})


@router.get("")
async def get_collective_list(
    current_user: Session = Depends(get_current_user_from_session)
) -> list[CollectiveListDTO]:
    return await service_locator.club_read_facade.get_collective_list(current_user.club_id)


@router.get("/{collective_id}")
async def get_collective(
    collective_id: str,
    current_user: Session = Depends(get_current_user_from_session)
) -> CollectiveDTO:
    return await service_locator.club_read_facade.get_collective(current_user.club_id, collective_id)

@router.get("/{collective_id}/players")
async def get_collective_players(
    collective_id: str,
    current_user: Session = Depends(get_current_user_from_session),
    page: int = 0,
    per_page: int = 10
) -> PaginatedDTO[CollectivePlayerDTO]:
    return await service_locator.club_read_facade.get_collective_players(current_user.club_id, collective_id, page, per_page)

@router.get("/{collective_id}/unassigned-players/search")
async def get_unassigned_players(
    collective_id: str,
    q : str = Query(default=""),
    current_user: Session = Depends(get_current_user_from_session),
) -> list[CollectivePlayerDTO]:
    return await service_locator.club_read_facade.search_unassigned_players_in_collective(current_user.club_id, collective_id, q)