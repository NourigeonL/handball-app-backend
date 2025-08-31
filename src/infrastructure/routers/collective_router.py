from typing import Annotated
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from src.dependencies import get_current_user_from_session
from src.service_locator import service_locator
from src.application.collective.commands import CreateCollectiveCommand, AddPlayerToCollectiveCommand, RemovePlayerFromCollectiveCommand
from src.read_facades.dtos import CollectiveDTO, CollectiveListDTO
from src.read_facades.interface import IReadFacade
from src.infrastructure.session_manager import Session

router = APIRouter(prefix="/clubs/{club_id}/collectives", tags=["collectives"])

class CollectiveCreateRequest(BaseModel):
    name: str
    description: str | None = None

@router.post("/create")
async def create_collective(
    club_id: str,
    collective_create_request: CollectiveCreateRequest, 
    current_user: Session = Depends(get_current_user_from_session)
):
    await service_locator.collective_service.handle(CreateCollectiveCommand(
        actor_id=current_user.user_id, 
        name=collective_create_request.name, 
        description=collective_create_request.description,
        club_id=club_id,
    ))
    return JSONResponse(status_code=201, content={"message": "Collective created successfully"})

class AddPlayerToCollectiveRequest(BaseModel):
    player_id: str
    collective_id: str

@router.post("/add-player")
async def add_player_to_collective(
    club_id: str,
    add_player_request: AddPlayerToCollectiveRequest, 
    current_user: Session = Depends(get_current_user_from_session)
):
    await service_locator.collective_service.handle(AddPlayerToCollectiveCommand(
        actor_id=current_user.user_id, 
        player_id=add_player_request.player_id, 
        collective_id=add_player_request.collective_id,
    ))
    return JSONResponse(status_code=200, content={"message": "Player added to collective successfully"})

class RemovePlayerFromCollectiveRequest(BaseModel):
    player_id: str
    collective_id: str

@router.post("/remove-player")
async def remove_player_from_collective(
    club_id: str,
    remove_player_request: RemovePlayerFromCollectiveRequest, 
    current_user: Session = Depends(get_current_user_from_session)
):
    await service_locator.collective_service.handle(RemovePlayerFromCollectiveCommand(
        actor_id=current_user.user_id, 
        player_id=remove_player_request.player_id, 
        collective_id=remove_player_request.collective_id,
    ))
    return JSONResponse(status_code=200, content={"message": "Player removed from collective successfully"})


@router.get("")
async def get_collective_list(
    club_id: str,
    current_user: Session = Depends(get_current_user_from_session)
):
    return await service_locator.club_read_facade.get_collective_list(club_id)
