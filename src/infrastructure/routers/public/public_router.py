from fastapi import APIRouter
from src.common.enums import LicenseType, Season
from src.read_facades.dtos import PublicPlayerDTO
from src.service_locator import service_locator

router = APIRouter(prefix="/public", tags=["Public"])

@router.get("/clubs")
async def get_club_list():
    return await service_locator.public_read_facade.get_club_list()

@router.get("/players")
async def get_player_list() -> list[PublicPlayerDTO]:
    return await service_locator.public_read_facade.get_player_list()


@router.get("/season/current")
async def get_current_season() -> Season:
    return Season.current()

@router.get("/licenses")
async def get_license_list() -> list[LicenseType]:
    return list(LicenseType)