from datetime import date, datetime
from fastapi import APIRouter, Depends
from pydantic import BaseModel
from src.application.training_session.commands import ChangePlayerTrainingSessionStatusCommand, CreateTrainingSessionCommand
from src.common.enums import TrainingSessionPlayerStatus
from src.dependencies import get_current_user_from_session
from src.read_facades.dtos import TrainingSessionDTO, TrainingSessionPlayerDTO
from src.read_facades.pagination import PaginatedDTO
from src.service_locator import service_locator
from src.infrastructure.session_manager import Session

router = APIRouter(prefix="/training-sessions", tags=["training-sessions"])

class CreateTrainingSessionRequest(BaseModel):
    start_time: datetime
    end_time: datetime

class ChangePlayerStatusRequest(BaseModel):
    player_id: str
    status: TrainingSessionPlayerStatus

@router.get("/{training_session_id}")
async def get_training_session(
    training_session_id: str,
    current_user: Session = Depends(get_current_user_from_session)
) -> TrainingSessionDTO:
    return await service_locator.club_read_facade.get_training_session(current_user.club_id, training_session_id)

@router.get("")
async def get_training_session_list(
    current_user: Session = Depends(get_current_user_from_session),
    page: int = 0,
    per_page: int = 10
) -> PaginatedDTO[TrainingSessionDTO]:
    return await service_locator.club_read_facade.get_training_session_list(current_user.club_id, page, per_page)

@router.get("/{training_session_id}/players")
async def get_training_session_players(
    training_session_id: str,
    current_user: Session = Depends(get_current_user_from_session),
    page: int = 0,
    per_page: int = 10
) -> PaginatedDTO[TrainingSessionPlayerDTO]:
    return await service_locator.club_read_facade.get_training_session_players(current_user.club_id, training_session_id, page, per_page)

@router.post("/create")
async def create_training_session(
    create_training_session_request: CreateTrainingSessionRequest,
    current_user: Session = Depends(get_current_user_from_session)
):
    await service_locator.training_session_service.handle(CreateTrainingSessionCommand(
        actor_id=current_user.user_id,
        club_id=current_user.club_id,
        start_time=create_training_session_request.start_time,
        end_time=create_training_session_request.end_time))

@router.post("/{training_session_id}/change-player-status")
async def change_player_status(
    training_session_id: str,
    change_player_status_request: ChangePlayerStatusRequest,
    current_user: Session = Depends(get_current_user_from_session)
):
    await service_locator.training_session_service.handle(ChangePlayerTrainingSessionStatusCommand(
        actor_id=current_user.user_id,
        club_id=current_user.club_id,
        training_session_id=training_session_id,
        player_id=change_player_status_request.player_id,
        status=change_player_status_request.status))