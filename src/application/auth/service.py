
from multipledispatch import dispatch
from src.common.eventsourcing import IRepository
from src.common.cqrs import IAuthService, Command

class AuthService(IAuthService):
    def __init__(self):
        pass

    async def _condition_are_met(self, command: Command) -> bool:
        return True