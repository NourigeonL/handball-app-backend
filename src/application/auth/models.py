
from pydantic import BaseModel


class DBUser(BaseModel):
    user_id: str
    email : str
    google_account_id : str | None = None
