from datetime import date
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from src.application.player.commands import RegisterPlayerCommand
from src.common.enums import Gender, LicenseType
from src.dependencies import UserSession, get_current_user, get_current_user_from_token
from src.service_locator import service_locator

router = APIRouter(prefix="/players", tags=["players"])

class RegisterPlayerRequest(BaseModel):
    club_id: str
    first_name: str
    last_name: str
    gender: Gender
    date_of_birth: date
    license_number: str | None = None
    license_type: LicenseType | None = None

@router.post("/register")
async def register_player(
    register_player_request: RegisterPlayerRequest, 
    current_user: UserSession = Depends(get_current_user_from_token)
):
    """
    Register a new player - requires management access to the club
    """
    # Simple check: user is authenticated and can manage the club
    if not await service_locator.auth_service.can_manage_club(current_user.user_id, register_player_request.club_id):
        raise HTTPException(status_code=403, detail=f"Management access denied to club {register_player_request.club_id}")
    
    await service_locator.player_service.handle(RegisterPlayerCommand(
        actor_id=current_user.user_id,
        club_id=register_player_request.club_id,
        first_name=register_player_request.first_name,
        last_name=register_player_request.last_name,
        gender=register_player_request.gender,
        date_of_birth=register_player_request.date_of_birth,
        license_number=register_player_request.license_number,
        license_type=register_player_request.license_type))
    return JSONResponse(status_code=201, content={"message": "Player registered successfully"})





