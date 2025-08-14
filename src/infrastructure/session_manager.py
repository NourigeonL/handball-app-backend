import secrets

from pydantic import BaseModel

class Session(BaseModel):
    user_id: str
    club_id: str | None = None  

class SessionManager:

    def __init__(self) -> None:
        self.sessions : dict[str, Session] = {}

    def generate_session_id(self) -> str:
        return secrets.token_urlsafe(32)

    async def create_session(self, user_id: str, club_id: str | None = None) -> str:
        session_id = self.generate_session_id()
        self.sessions[session_id] = Session(user_id=user_id, club_id=club_id)
        return session_id

    async def update_session(self, session_id: str, club_id: str | None = None) -> None:
        if club_id is not None:
            self.sessions[session_id].club_id = club_id
    
    async def get_session(self, session_id: str | None = None) -> Session | None:
        if session_id is None:
            return None
        return self.sessions.get(session_id)
    
    async def delete_session(self, session_id: str) -> None:
        del self.sessions[session_id]

    async def get_all_sessions(self) -> list[Session]:
        return list(self.sessions.values())
    
    async def get_all_sessions_for_user(self, user_id: str) -> list[Session]:
        return [session for session in self.sessions.values() if session.user_id == user_id]
    