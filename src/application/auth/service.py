
from multipledispatch import dispatch
from src.application.auth.models import DBUser
from src.common.enums import StaffMemberRole
from src.common.eventsourcing import IEventStoreRepository
from src.common.cqrs import IAuthService, Command
from src.common.constants import SYSTEM_ACTOR_ID
from src.common.eventsourcing.exceptions import AggregateNotFoundError
from src.domains.club.model import Club
from src.domains.user.model import User, UserCreate
from src.infrastructure.storages.auth_repository import AuthRepository
from src.common.guid import guid
from google.oauth2 import id_token
from google.auth.transport import requests as google_requests
from google.auth import exceptions as google_exceptions
from src.settings import settings
from datetime import datetime


class AuthService(IAuthService):
    """
    Unified service for authentication and authorization
    Handles user authentication, Google auth, and club access control
    """
    
    def __init__(self, auth_repository: AuthRepository, user_repo: IEventStoreRepository[User], club_repo: IEventStoreRepository[Club]):
        self._auth_repository = auth_repository
        self._user_repo = user_repo
        self._club_repo = club_repo

    async def _condition_are_met(self, command: Command) -> bool:
        return True

    # ============================================================================
    # USER AUTHENTICATION METHODS
    # ============================================================================

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

    async def verify_google_id_token(self, id_token_string: str) -> dict:
        """
        Verify Google ID token from frontend and return user information
        """
        try:
            # Verify the token
            idinfo = id_token.verify_oauth2_token(
                id_token_string, 
                google_requests.Request(), 
                settings.GOOGLE_AUTH_CLIENT_ID
            )
            
            # Verify the token was issued by Google
            if idinfo['iss'] not in ['https://accounts.google.com', 'accounts.google.com']:
                raise ValueError('Wrong issuer.')
            
            # Verify the token is not expired
            if idinfo['exp'] < datetime.now().timestamp():
                raise ValueError('Token expired.')
            
            # Extract user information
            user_info = {
                'google_account_id': idinfo['sub'],
                'email': idinfo['email'],
                'first_name': idinfo.get('given_name'),
                'last_name': idinfo.get('family_name'),
                'name': idinfo.get('name'),
                'picture': idinfo.get('picture')
            }
            
            return user_info
            
        except google_exceptions.GoogleAuthError as e:
            raise ValueError(f'Google authentication error: {e}')
        except Exception as e:
            raise ValueError(f'Token verification failed: {e}')

    async def authenticate_user_from_frontend(self, id_token_string: str) -> DBUser:
        """
        Authenticate user from frontend Google ID token
        """
        # Verify the token and get user info
        user_info = await self.verify_google_id_token(id_token_string)
        
        # Sign up or get existing user
        user = await self.sign_up_user_from_google_account(
            google_account_id=user_info['google_account_id'],
            email=user_info['email'],
            first_name=user_info['first_name'],
            last_name=user_info['last_name'],
            name=user_info['name']
        )
        
        return user

    # ============================================================================
    # CLUB AUTHORIZATION METHODS
    # ============================================================================

    async def get_club_roles(self, user_id: str, club_id: str) -> list[StaffMemberRole]:
        club = await self._club_repo.get_by_id(club_id)
        roles = []
        if club.owner_id == user_id:
            roles.append(StaffMemberRole.OWNER)
        if user_id in club.coaches:
            roles.append(StaffMemberRole.COACH)
        return roles