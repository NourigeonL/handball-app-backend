

from src.application.auth.service import AuthService
from src.application.club.service import ClubService
from src.application.collective.service import CollectiveService
from src.application.player.service import PlayerService
from src.application.training_session.service import TrainingSessionService
from src.common.cqrs.messages import IEventPublisher
from src.infrastructure.session_manager import SessionManager
from src.read_facades.club_read_facade import ClubReadFacade
from src.read_facades.public_read_facade import PublicReadFacade

class ServiceLocator:
    __global = {}

    @property
    def public_read_facade(self) -> PublicReadFacade:
        return self.__global["public_read_facade"]
    
    @public_read_facade.setter
    def public_read_facade(self, public_read_facade : PublicReadFacade) -> None:
        self.__global["public_read_facade"] = public_read_facade

    @property
    def club_read_facade(self) -> ClubReadFacade:
        return self.__global["club_read_facade"]
    
    @club_read_facade.setter
    def club_read_facade(self, club_read_facade : ClubReadFacade) -> None:
        self.__global["club_read_facade"] = club_read_facade

    @property
    def event_publisher(self) -> IEventPublisher:
        return self.__global["event_publisher"]
    
    @event_publisher.setter
    def event_publisher(self, event_publisher : IEventPublisher) -> None:
        self.__global["event_publisher"] = event_publisher

    @property
    def club_service(self) -> ClubService:
        return self.__global["club_service"]
    
    @club_service.setter
    def club_service(self, club_service : ClubService) -> None:
        self.__global["club_service"] = club_service

    @property
    def player_service(self) -> PlayerService:
        return self.__global["player_service"]
    
    @player_service.setter
    def player_service(self, player_service : PlayerService) -> None:
        self.__global["player_service"] = player_service

    @property
    def collective_service(self) -> CollectiveService:
        return self.__global["collective_service"]
    
    @collective_service.setter
    def collective_service(self, collective_service : CollectiveService) -> None:
        self.__global["collective_service"] = collective_service

    @property
    def auth_service(self) -> AuthService:
        return self.__global["auth_service"]
    
    @auth_service.setter
    def auth_service(self, auth_service : AuthService) -> None:
        self.__global["auth_service"] = auth_service

    @property
    def session_manager(self) -> SessionManager:
        return self.__global["session_manager"]
    
    @session_manager.setter
    def session_manager(self, session_manager : SessionManager) -> None:
        self.__global["session_manager"] = session_manager

    @property
    def training_session_service(self) -> TrainingSessionService:
        return self.__global["training_session_service"]
    
    @training_session_service.setter
    def training_session_service(self, training_session_service : TrainingSessionService) -> None:
        self.__global["training_session_service"] = training_session_service

service_locator = ServiceLocator()