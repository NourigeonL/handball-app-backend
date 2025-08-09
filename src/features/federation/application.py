from dataclasses import dataclass
from multipledispatch import dispatch
from src.common.enums import LicenseType
from src.eventsourcing.exceptions import InvalidOperationError
from src.eventsourcing.messages import Command, IMessageBroker, IntegrationEvent, MessageHandler
from src.eventsourcing.repositories import IRepository
from src.features.federation.aggregate import Federation

@dataclass
class IEClubRegistered(IntegrationEvent):
    registration_number : str
    owner_id : str

@dataclass
class IEFederationApprovedPlayerRegistration(IntegrationEvent):
    license_id : str
    first_name : str
    last_name : str
    date_of_birth : str
    club_id : str
    season : str
    license_type : LicenseType
    email : str | None = None
    phone : str | None = None


@dataclass
class RegisterClub(Command):
    registration_number : str
    name : str
    owner_id : str

@dataclass
class RegisterPlayer(Command):
    license_id : str
    first_name : str
    last_name : str
    date_of_birth : str
    club_id : str
    season : str
    license_type : LicenseType
    email : str | None = None
    phone : str | None = None



class FederationCommandHandler(MessageHandler):
    def __init__(self, federation_repo : IRepository[Federation], message_broker : IMessageBroker) -> None:
        super().__init__(message_broker)
        self.__federation_repo = federation_repo

    @dispatch(RegisterClub)
    async def _handle(self, command : RegisterClub) -> None:
        federation = await self.__federation_repo.get_by_id(Federation.id)
        try:
            federation.register_club(command.registration_number, command.name, command.owner_id)
            await self.__federation_repo.save(federation, federation.version)
            await self._message_broker.publish(IEClubRegistered(registration_number=command.registration_number, owner_id=command.owner_id))
        except InvalidOperationError as e:
            raise e

    @dispatch(RegisterPlayer)
    async def _handle(self, command : RegisterPlayer) -> None:
        federation = await self.__federation_repo.get_by_id(Federation.id)
        if command.club_id not in federation.clubs:
            raise InvalidOperationError(f"Club {command.club_id} not found")
        if command.license_id in federation.players:
            federation.register_player(command.license_id, command.first_name, command.last_name, command.date_of_birth, command.club_id, command.season, command.license_type, command.email, command.phone)
            await self.__federation_repo.save(federation, federation.version)
        await self._message_broker.publish(IEFederationApprovedPlayerRegistration(license_id=command.license_id, first_name=command.first_name, last_name=command.last_name, date_of_birth=command.date_of_birth, club_id=command.club_id, season=command.season, license_type=command.license_type, email=command.email, phone=command.phone))
