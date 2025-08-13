from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from src.application.collective.commands import AddPlayerToCollectiveCommand, CreateCollectiveCommand, RemovePlayerFromCollectiveCommand
from src.dependencies import UserSession, get_current_user, get_current_user_from_token
from src.service_locator import service_locator

router = APIRouter(prefix="/collectives", tags=["collectives"])

class CollectiveCreateRequest(BaseModel):
    club_id: str
    name: str
    description: str | None = None

@router.post("/create")
async def create_collective(
    collective_create_data: CollectiveCreateRequest, 
    current_user: UserSession = Depends(get_current_user_from_token)
):
    """
    Create a new collective - requires management access to the club
    """
    # Simple check: user is authenticated and can manage the club
    if not await service_locator.auth_service.can_manage_club(current_user.user_id, collective_create_data.club_id):
        raise HTTPException(status_code=403, detail=f"Management access denied to club {collective_create_data.club_id}")
    
    await service_locator.collective_service.handle(CreateCollectiveCommand(
        actor_id=current_user.user_id, 
        club_id=collective_create_data.club_id, 
        name=collective_create_data.name, 
        description=collective_create_data.description))
    return JSONResponse(status_code=201, content={"message": "Collective created successfully"})

class AddPlayerToCollectiveRequest(BaseModel):
    player_id: str

@router.post("/{collective_id}/add-player")
async def add_player_to_collective(
    collective_id: str, 
    add_player_to_collective_data: AddPlayerToCollectiveRequest, 
    current_user: UserSession = Depends(get_current_user_from_token)
):
    """
    Add a player to a collective - requires management access to the club
    """
    # Get the collective to check club access
    collective = await service_locator.collective_service.get_by_id(collective_id)
    if not collective:
        raise HTTPException(status_code=404, detail="Collective not found")
    
    # Simple check: user is authenticated and can manage the club
    if not await service_locator.auth_service.can_manage_club(current_user.user_id, collective.club_id):
        raise HTTPException(status_code=403, detail=f"Management access denied to club {collective.club_id}")
    
    await service_locator.collective_service.handle(AddPlayerToCollectiveCommand(
        actor_id=current_user.user_id, 
        collective_id=collective_id, 
        player_id=add_player_to_collective_data.player_id))
    return JSONResponse(status_code=201, content={"message": "Player added to collective successfully"})

class RemovePlayerFromCollectiveRequest(BaseModel):
    player_id: str

@router.post("/{collective_id}/remove-player")
async def remove_player_from_collective(
    collective_id: str, 
    remove_player_from_collective_data: RemovePlayerFromCollectiveRequest, 
    current_user: UserSession = Depends(get_current_user_from_token)
):
    """
    Remove a player from a collective - requires management access to the club
    """
    # Get the collective to check club access
    collective = await service_locator.collective_service.get_by_id(collective_id)
    if not collective:
        raise HTTPException(status_code=404, detail="Collective not found")
    
    # Simple check: user is authenticated and can manage the club
    if not await service_locator.auth_service.can_manage_club(current_user.user_id, collective.club_id):
        raise HTTPException(status_code=403, detail=f"Management access denied to club {collective.club_id}")
    
    await service_locator.collective_service.handle(RemovePlayerFromCollectiveCommand(
        actor_id=current_user.user_id, 
        collective_id=collective_id, 
        player_id=remove_player_from_collective_data.player_id))
    return JSONResponse(status_code=200, content={"message": "Player removed from collective successfully"})



