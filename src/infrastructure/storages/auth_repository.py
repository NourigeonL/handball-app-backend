import json
import os

from src.application.auth.models import DBUser


class AuthRepository:

    def __init__(self, file_path: str):
        self.file_path = file_path
        self.db : dict = {}
        if not os.path.exists(file_path):
            with open(file_path, "w") as f:
                json.dump({}, f)

        self.load()

    def load(self) -> None:
        with open(self.file_path, "r") as f:
            self.db = json.load(f)

    def save(self) -> None:
        with open(self.file_path, "w") as f:
            json.dump(self.db, f)

    async def get_user_by_google_account_id(self, google_account_id: str) -> DBUser | None:
        user_id = self.db.get("google_accounts", {}).get(google_account_id)
        if user_id:
            user_dict = self.db.get("users", {}).get(user_id)
            if user_dict:
                return DBUser.model_validate(user_dict)
        return None
    
    async def get_user_by_email(self, email: str) -> DBUser | None:
        user_id = self.db.get("emails", {}).get(email)
        if user_id:
            print(f"Found user by email: {user_id}")
            user_dict = self.db.get("users", {}).get(user_id)
            if user_dict:
                return DBUser.model_validate(user_dict)
        return None
    
    async def save_user(self, user: DBUser) -> None:
        self.db.setdefault("users", {}).setdefault(user.user_id, user.model_dump())
        self.db.setdefault("google_accounts", {}).setdefault(user.google_account_id, user.user_id)
        self.db.setdefault("emails", {}).setdefault(user.email, user.user_id)
        self.save()