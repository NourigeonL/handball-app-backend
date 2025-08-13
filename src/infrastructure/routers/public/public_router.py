from fastapi import APIRouter
from src.service_locator import service_locator

router = APIRouter(prefix="/public", tags=["Public"])

@router.get("/clubs")
async def get_club_list():
    return await service_locator.public_read_facade.get_club_list()