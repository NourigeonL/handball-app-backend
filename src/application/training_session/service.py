from multipledispatch import dispatch
from src.application.training_session.commands import ChangePlayerTrainingSessionStatusCommand, CreateTrainingSessionCommand, RemovePlayerFromTrainingSessionCommand
from src.common.cqrs.messages import CommandHandler, IAuthService, IEventPublisher
from src.common.eventsourcing.exceptions import InvalidOperationError
from src.common.eventsourcing.repositories import IEventStoreRepository
from src.domains.player.model import Player
from src.domains.training_session.model import TrainingSession, TrainingSessionCreate
from src.common.loggers import app_logger

class TrainingSessionService(CommandHandler):

    def __init__(self, auth_service: IAuthService, event_publisher: IEventPublisher, training_session_repo: IEventStoreRepository[TrainingSession], player_repo: IEventStoreRepository[Player]):
        super().__init__(auth_service, event_publisher)
        self._training_session_repo = training_session_repo
        self._player_repo = player_repo

    @dispatch(CreateTrainingSessionCommand)
    async def _handle(self, command: CreateTrainingSessionCommand) -> None:
        training_session = TrainingSession(create=TrainingSessionCreate(
            actor_id=command.actor_id,
            club_id=command.club_id,
            start_time=command.start_time,
            end_time=command.end_time,
        ))
        await self._training_session_repo.save(training_session, -1)

    @dispatch(ChangePlayerTrainingSessionStatusCommand)
    async def _handle(self, command: ChangePlayerTrainingSessionStatusCommand) -> None:
        training_session = await self._training_session_repo.get_by_id(command.training_session_id)
        app_logger.info(f"Training session: {training_session.id} {training_session.club_id} {command.club_id}")
        if training_session.club_id != command.club_id:
            raise InvalidOperationError("Training session is not in the club")
        player = await self._player_repo.get_by_id(command.player_id)
        if player.club_id != command.club_id:
            raise InvalidOperationError("Player is not in the club")
        
        training_session.change_player_status(actor_id=command.actor_id, player_id=command.player_id, status=command.status, reason=command.reason, with_reason=command.with_reason, arrival_time=command.arrival_time)
        await self._training_session_repo.save(training_session, training_session.version)

    @dispatch(RemovePlayerFromTrainingSessionCommand)
    async def _handle(self, command: RemovePlayerFromTrainingSessionCommand) -> None:
        training_session = await self._training_session_repo.get_by_id(command.training_session_id)
        training_session.remove_player(actor_id=command.actor_id, player_id=command.player_id)
        await self._training_session_repo.save(training_session, training_session.version)