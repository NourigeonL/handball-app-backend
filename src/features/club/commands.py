

from dataclasses import dataclass
from datetime import date

from multipledispatch import dispatch
from src.common.enums import LicenseType
from src.eventsourcing.exceptions import InvalidOperationError, UnauthorizedError
from src.eventsourcing.messages import Command, IMessageBroker, MessageHandler
from src.eventsourcing.repositories import IRepository
from src.features.club.aggregates import Club



@dataclass
class RegisterPlayerToClub(Command):
    club_id: str
    player_id : str
    license_type : LicenseType
    season : str

class ClubCommandHandler(MessageHandler):
    def __init__(self, repo : IRepository[Club], message_broker : IMessageBroker) -> None:
        super().__init__(message_broker)
        self.__repo = repo

    @dispatch(RegisterPlayerToClub)
    async def _handle(self, command: RegisterPlayerToClub) -> None:
        club = await self.__repo.get_by_id(command.club_id)
        if command.user_id not in club.staff_members:
            raise UnauthorizedError(f"User {command.user_id} is not a staff member of club {command.club_id}")
        club.register_player(player_id=command.player_id, license_type=command.license_type, season=command.season)
        await self.__repo.save(club, club.version)

    
