from typing import Annotated
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from starlette.responses import JSONResponse
from src.application.club.commands import CreateClubCommand
from src.dependencies import (
    UserSession, 
    get_current_user, 
    get_current_user_from_token
)
from src.service_locator import service_locator

router = APIRouter(prefix="/clubs", tags=["clubs"])

class ClubCreateRequest(BaseModel):
    name: str
    registration_number: str | None = None


@router.post("/create")
async def create_club(
    club_create_request: ClubCreateRequest, 
    current_user: UserSession = Depends(get_current_user_from_token)
):
    await service_locator.club_service.handle(CreateClubCommand(
        actor_id=current_user.user_id, 
        name=club_create_request.name, 
        registration_number=club_create_request.registration_number,
        owner_id=current_user.user_id,
    ))
    return JSONResponse(status_code=201, content={"message": "Club created successfully"})

@router.get("/my-clubs")
async def get_club_list(current_user: UserSession = Depends(get_current_user_from_token)):
    return await service_locator.public_read_facade.get_user_clubs(current_user.user_id)

@router.get("/{club_id}/players")
async def get_club_players(
    club_id: str, 
    current_user: UserSession = Depends(get_current_user_from_token)
):
    # Simple check: user is authenticated and can access the club
    if not await service_locator.auth_service.can_access_club(current_user.user_id, club_id):
        raise HTTPException(status_code=403, detail=f"Access denied to club {club_id}")
    
    return await service_locator.public_read_facade.get_club_players(club_id)

@router.get("/{club_id}/collectives")
async def get_club_collectives(
    club_id: str, 
    current_user: UserSession = Depends(get_current_user_from_token)
):
    # Simple check: user is authenticated and can access the club
    if not await service_locator.auth_service.can_access_club(current_user.user_id, club_id):
        raise HTTPException(status_code=403, detail=f"Access denied to club {club_id}")
    
    return await service_locator.public_read_facade.get_club_collectives(club_id)

@router.get("/{club_id}/collectives/{collective_id}")
async def get_collective(
    club_id: str, 
    collective_id: str, 
    current_user: UserSession = Depends(get_current_user_from_token)
):
    # Simple check: user is authenticated and can access the club
    if not await service_locator.auth_service.can_access_club(current_user.user_id, club_id):
        raise HTTPException(status_code=403, detail=f"Access denied to club {club_id}")
    
    return await service_locator.public_read_facade.get_collective(club_id, collective_id)

@router.get("/{club_id}/info")
async def get_club_info(
    club_id: str, 
    current_user: UserSession = Depends(get_current_user_from_token)
):
    """
    Get club information - can be accessed with Bearer token from frontend
    Uses standardized APIKeyHeader for authentication
    """
    # Simple check: user is authenticated and can access the club
    if not await service_locator.auth_service.can_access_club(current_user.user_id, club_id):
        raise HTTPException(status_code=403, detail=f"Access denied to club {club_id}")
    
    club_info = await service_locator.public_read_facade.get_club(club_id)
    user_access = service_locator.club_read_facade.get_user_club_access(current_user.user_id, club_id)
    
    return {
        "club": club_info,
        "authenticated_user": {
            "user_id": current_user.user_id,
            "email": current_user.user_email,
            "access_level": user_access.access_level if user_access else "none",
            "can_manage": user_access.can_manage if user_access else False
        }
    }

@router.get("/{club_id}/access")
async def get_club_access_info(
    club_id: str,
    current_user: UserSession = Depends(get_current_user_from_token)
):
    """
    Get user's access information for a specific club
    """
    # Simple check: user is authenticated and can access the club
    if not await service_locator.auth_service.can_access_club(current_user.user_id, club_id):
        raise HTTPException(status_code=403, detail=f"Access denied to club {club_id}")
    
    user_access = service_locator.club_read_facade.get_user_club_access(current_user.user_id, club_id)
    return user_access