import abc
from src.common.eventsourcing.exceptions import UnauthorizedError
from src.common.eventsourcing.messages import Command

class IAuthService(abc.ABC):
    async def authorize_command(self, command: Command) -> None:
        if not await self._condition_are_met(command):
            raise UnauthorizedError("Condition are not met")

    async def _condition_are_met(self, command: Command) -> bool:
        """
        Abstract method to check if the condition are met.
        """