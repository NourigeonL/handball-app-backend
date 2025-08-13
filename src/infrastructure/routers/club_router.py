from typing import Annotated
from uuid import UUID
from fastapi import APIRouter, Depends
from pydantic import BaseModel
from starlette.responses import JSONResponse
from src.application.club.commands import CreateClubCommand
from src.dependencies import UserSession, get_current_user
from src.service_locator import service_locator

router = APIRouter(prefix="/clubs", tags=["clubs"])

class ClubCreateRequest(BaseModel):
    name: str
    registration_number: str | None = None


@router.post("/create")
async def create_club(club_create_request: ClubCreateRequest, current_user: UserSession = Depends(get_current_user)):
    await service_locator.club_service.handle(CreateClubCommand(
        actor_id=current_user.user_id, 
        name=club_create_request.name, 
        registration_number=club_create_request.registration_number))
    return JSONResponse(status_code=201, content={"message": "Club created successfully"})

@router.get("")
async def get_club_list(current_user: UserSession = Depends(get_current_user)):
    return await service_locator.public_read_facade.get_club_list()

@router.get("/{club_id}/players")
async def get_club_players(club_id: str, current_user: UserSession = Depends(get_current_user)):
    return await service_locator.club_read_facade.get_club_players(club_id)

@router.get("/{club_id}/collectives")
async def get_club_collectives(club_id: str, current_user: UserSession = Depends(get_current_user)):
    return await service_locator.club_read_facade.get_club_collectives(club_id)

@router.get("/{club_id}/collectives/{collective_id}")
async def get_collective(club_id: str, collective_id: str, current_user: UserSession = Depends(get_current_user)):
    return await service_locator.club_read_facade.get_collective(club_id, collective_id)