from dataclasses import dataclass
from multipledispatch import dispatch
from src.eventsourcing.exceptions import InvalidOperationError
from src.eventsourcing.messages import Command, IMessageBroker, MessageHandler
from src.features.federation.aggregates import Federation
from src.eventsourcing.repositories import IRepository
from src.features.club.commands import RegisterPlayerToClub
from src.features.federation import integration_events

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
            await self._message_broker.publish(integration_events.IEClubRegistered(registration_number=command.registration_number, owner_id=command.owner_id))
        except InvalidOperationError as e:
            raise e

    @dispatch(RegisterPlayer)
    async def _handle(self, command : RegisterPlayer) -> None:
        federation = await self.__federation_repo.get_by_id(Federation.id)
        federation.register_player(command.license_id)
        await self.__federation_repo.save(federation, federation.version)
        await self._message_broker.publish(integration_events.IEPlayerLicensed(license_id=command.license_id, first_name=command.first_name, last_name=command.last_name, date_of_birth=command.date_of_birth, email=command.email, phone=command.phone))