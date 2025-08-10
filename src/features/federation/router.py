from typing import Annotated
from fastapi import APIRouter, Depends
from pydantic import BaseModel
from src.dependencies import get_current_user, UserSession
from src.service_locator import service_locator
from src.features.federation.application import RegisterClub

router = APIRouter(prefix="/federation", tags=["federation"])

class RegisterClubRequest(BaseModel):
    registration_number : str
    name : str


@router.post("/register-club")
async def register_club(request: RegisterClubRequest, current_user : Annotated[UserSession, Depends(get_current_user)]):
    if e:= await service_locator.event_publisher.send(RegisterClub(registration_number=request.registration_number, name=request.name, owner_id=current_user.user_id)):
        raise e

@router.get("/clubs")
async def get_clubs():
    return await service_locator.public_read_facade.get_club_list()