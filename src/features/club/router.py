from typing import Annotated
from fastapi import APIRouter, Depends
from pydantic import BaseModel
from src.common.enums import LicenseType
from src.dependencies import UserSession, get_current_user
from src.features.federation.application import RegisterPlayer
from src.service_locator import service_locator

router = APIRouter(prefix="/club", tags=["club"])

class RegisterPlayerRequest(BaseModel):
    license_id : str
    first_name : str
    last_name : str
    date_of_birth : str
    email : str | None = None
    phone : str | None = None
    license_type : LicenseType
    season : str


@router.post("{club_id}/register-player")
async def register_player(club_id: str, request: RegisterPlayerRequest, current_user: Annotated[UserSession, Depends(get_current_user)]):
    if e:= await service_locator.message_broker.send(RegisterPlayer(club_id=club_id, player_id=request.player_id, license_type=request.license_type, season=request.season, user_id=current_user.user_id)):
        raise e