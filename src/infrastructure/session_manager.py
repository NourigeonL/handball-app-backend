import json
import os
import secrets

from pydantic import BaseModel

class Session(BaseModel):
    user_id: str
    google_id_token: str | None = None
    club_id: str | None = None  

class SessionManager:

    def __init__(self) -> None:
        if not os.path.exists("session_manager.json"):
            with open("session_manager.json", "w") as f:
                json.dump({}, f)
        else:
            with open("session_manager.json", "r") as f:
                self.sessions = json.load(f)

    def generate_session_id(self) -> str:
        return secrets.token_urlsafe(32)

    async def create_session(self, session: Session) -> str:
        session_id = self.generate_session_id()
        self.sessions[session_id] = session.model_dump()
        with open("session_manager.json", "w") as f:
            json.dump(self.sessions, f)
        return session_id

    async def update_session(self, session_id: str, club_id: str | None = None) -> None:
        if club_id is not None:
            self.sessions[session_id]["club_id"] = club_id
        with open("session_manager.json", "w") as f:
            json.dump(self.sessions, f)
    
    async def get_session(self, session_id: str | None = None) -> Session | None:
        if session_id is None:
            return None
        return Session.model_validate(self.sessions.get(session_id))
    
    async def delete_session(self, session_id: str) -> None:
        del self.sessions[session_id]
        with open("session_manager.json", "w") as f:
            json.dump(self.sessions, f)

    async def get_all_sessions(self) -> list[Session]:
        return [Session.model_validate(session) for session in self.sessions.values()]
    
    async def get_all_sessions_for_user(self, user_id: str) -> list[Session]:
        return [Session.model_validate(session) for session in self.sessions.values() if session.user_id == user_id]
    