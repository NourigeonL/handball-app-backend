from typing import Annotated
from uuid import UUID
from fastapi import APIRouter, Depends
from pydantic import BaseModel
from src.dependencies import UserSession, get_current_user
from src.service_locator import service_locator

router = APIRouter(prefix="/clubs", tags=["clubs"])

