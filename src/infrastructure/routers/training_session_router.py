from datetime import date, datetime
from typing import Annotated
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from src.application.player.commands import RegisterPlayerCommand
from src.application.training_session.commands import ChangePlayerTrainingSessionStatusCommand, CreateTrainingSessionCommand
from src.common.enums import Gender, LicenseType, TrainingSessionPlayerStatus
from src.dependencies import get_current_user_from_session
from src.service_locator import service_locator
from src.infrastructure.session_manager import Session

router = APIRouter(prefix="/training-sessions", tags=["training-sessions"])

class CreateTrainingSessionRequest(BaseModel):
    date: date
    start_time: datetime | None = None
    end_time: datetime | None = None

class ChangePlayerStatusRequest(BaseModel):
    player_id: str
    status: TrainingSessionPlayerStatus

@router.post("/create")
async def create_training_session(
    create_training_session_request: CreateTrainingSessionRequest,
    current_user: Session = Depends(get_current_user_from_session)
):
    await service_locator.training_session_service.handle(CreateTrainingSessionCommand(
        actor_id=current_user.user_id,
        club_id=current_user.club_id,
        date=create_training_session_request.date,
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