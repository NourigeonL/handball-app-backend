
from multipledispatch import dispatch
from src.application.auth.models import DBUser
from src.common.eventsourcing import IEventStoreRepository
from src.common.cqrs import IAuthService, Command
from src.common.constants import SYSTEM_ACTOR_ID
from src.common.eventsourcing.exceptions import AggregateNotFoundError
from src.domains.club.model import Club
from src.domains.user.model import User, UserCreate
from src.infrastructure.storages.auth_repository import AuthRepository
from src.common.guid import guid


class AuthService(IAuthService):
    def __init__(self, auth_repository: AuthRepository, user_repo: IEventStoreRepository[User], club_repo: IEventStoreRepository[Club]):
        self._auth_repository = auth_repository
        self._user_repo = user_repo
        self._club_repo = club_repo

    async def _condition_are_met(self, command: Command) -> bool:
        return True

    async def sign_up_user_from_google_account(self, google_account_id: str, email: str, first_name: str | None = None, last_name: str | None = None, name: str | None = None) -> DBUser:
        db_user = await self._auth_repository.get_user_by_google_account_id(google_account_id)
        if db_user:
            print(f"Found user by google account id: {db_user}")
        else:
            db_user = await self._auth_repository.get_user_by_email(email)
            if db_user:
                print(f"Found user by email: {db_user}, updating google account id")
                db_user.google_account_id = google_account_id
                await self._auth_repository.save_user(db_user)
            else:
                print(f"No user found, creating new user")
                db_user = DBUser(user_id=guid(), email=email, google_account_id=google_account_id)
                await self._auth_repository.save_user(db_user)
        try: 
            user = await self._user_repo.get_by_id(db_user.user_id)
            if not user.name and name:
                user.update_name(first_name, last_name, name, SYSTEM_ACTOR_ID)
                await self._user_repo.save(user, user.version)
        except AggregateNotFoundError:
            user = User(user_create=UserCreate(user_id=db_user.user_id, actor_id=SYSTEM_ACTOR_ID, first_name=first_name, last_name=last_name, email=email))
            await self._user_repo.save(user, -1)
            
        
        return db_user