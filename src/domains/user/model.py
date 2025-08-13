from multipledispatch import dispatch
from pydantic import BaseModel
from src.common.eventsourcing.aggregates import AggregateRoot
from src.domains.user.events import UserEmailUpdated, UserNameUpdated, UserSignedUp


class UserCreate(BaseModel):
    user_id: str
    actor_id: str
    first_name: str | None = None
    last_name: str | None = None
    name: str | None = None
    email: str | None = None

class User(AggregateRoot):

    @property
    def id(self) -> str:
        return self.__id

    @staticmethod
    def to_stream_id(id: str) -> str:
        return f"user-{id}"

    def __init__(self, user_create: UserCreate | None = None):
        super().__init__()
        self.first_name : str | None = None
        self.last_name : str | None = None
        self.email : str | None = None
        self.name : str | None = None
        if user_create:
            self._apply_change(UserSignedUp(user_id=user_create.user_id, actor_id=user_create.actor_id, first_name=user_create.first_name, last_name=user_create.last_name, email=user_create.email, name=user_create.name))

    def update_name(self, first_name: str, last_name: str, name: str, actor_id: str):
        self._apply_change(UserNameUpdated(user_id=self.__id, actor_id=actor_id, first_name=first_name, last_name=last_name, name=name))

    def update_email(self, email: str, actor_id: str):
        self._apply_change(UserEmailUpdated(user_id=self.__id, actor_id=actor_id, email=email))


    @dispatch(UserSignedUp)
    def _apply(self, event: UserSignedUp):
        self.__id = event.user_id
        self.first_name = event.first_name
        self.last_name = event.last_name
        self.email = event.email
        self.name = event.name
    
    @dispatch(UserNameUpdated)
    def _apply(self, event: UserNameUpdated):
        self.first_name = event.first_name
        self.last_name = event.last_name
        self.name = event.name

    @dispatch(UserEmailUpdated)
    def _apply(self, event: UserEmailUpdated):
        self.email = event.email