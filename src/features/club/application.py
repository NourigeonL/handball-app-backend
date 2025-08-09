

from dataclasses import dataclass
from datetime import date

from multipledispatch import dispatch
from src.common.enums import LicenseType
from src.eventsourcing.exceptions import InvalidOperationError, UnauthorizedError
from src.eventsourcing.messages import Command, IMessageBroker, IntegrationEvent, MessageHandler
from src.eventsourcing.repositories import IRepository
from src.features.club.domain.models import Club
from src.features.federation import application as federation_integration_events


@dataclass
class RegisterPlayerToClub(Command):
    club_id: str
    player_id : str
    license_type : LicenseType
    season : str

@dataclass
class PlayerJoinedClubIE(IntegrationEvent):
    player_id : str
    club_id : str
    license_type : LicenseType
    season : str


class ClubCommandHandler(MessageHandler):
    def __init__(self, repo : IRepository[Club], message_broker : IMessageBroker) -> None:
        super().__init__(message_broker)
        self.__repo = repo
    
class ClubIntegrationEventHandler(MessageHandler):
    def __init__(self, club_repo : IRepository[Club], message_broker : IMessageBroker) -> None:
        super().__init__(message_broker)
        self.__club_repo = club_repo

    @dispatch(federation_integration_events.IEClubRegistered)
    async def _handle(self, event : federation_integration_events.IEClubRegistered) -> None:
        club = Club(registration_number=event.registration_number, owner_id=event.owner_id)
        await self.__club_repo.save(club, -1)

    @dispatch(federation_integration_events.IEFederationApprovedPlayerRegistration)
    async def _handle(self, event : federation_integration_events.IEFederationApprovedPlayerRegistration) -> None:
        club = await self.__club_repo.get_by_id(event.club_id)
        club.register_player(player_id=event.license_id, license_type=event.license_type, season=event.season)
        await self.__club_repo.save(club, club.version)
        await self._message_broker.publish(PlayerJoinedClubIE(player_id=event.license_id, club_id=event.club_id, license_type=event.license_type, season=event.season))
