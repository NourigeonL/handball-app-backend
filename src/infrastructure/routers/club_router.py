from typing import Annotated
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from starlette.responses import JSONResponse
from src.application.club.commands import CreateClubCommand
from src.dependencies import get_current_user_from_session, check_club_access
from src.read_facades.dtos import PublicClubDTO
from src.service_locator import service_locator
from src.infrastructure.session_manager import Session
from src.common.exceptions import GenericError

router = APIRouter(prefix="/clubs", tags=["clubs"])

class ClubCreateRequest(BaseModel):
    name: str
    registration_number: str | None = None

class ClubLoginRequest(BaseModel):
    club_id: str


@router.post("/create")
async def create_club(
    club_create_request: ClubCreateRequest, 
    current_user: Session = Depends(get_current_user_from_session)
):
    await service_locator.club_service.handle(CreateClubCommand(
        actor_id=current_user.user_id, 
        name=club_create_request.name, 
        registration_number=club_create_request.registration_number,
        owner_id=current_user.user_id,
    ))
    return JSONResponse(status_code=201, content={"message": "Club created successfully"})

@router.get("/my-clubs")
async def get_club_list(current_user: Session = Depends(get_current_user_from_session)) -> list[PublicClubDTO]:
    return await service_locator.public_read_facade.get_user_clubs(current_user.user_id)


@router.get("/{club_id}/info")
async def get_club_info(
    club_id: str, 
    current_user: Session = Depends(check_club_access)
):
    
    club_info = await service_locator.public_read_facade.get_club(club_id)
    user_access = await service_locator.club_read_facade.get_user_club_access(current_user.user_id, club_id)
    
    return {
        "club": club_info,
        "authenticated_user": {
            "user_id": current_user.user_id,
            "access_level": user_access.access_level if user_access else "none",
            "can_manage": user_access.can_manage if user_access else False
        }
    }
