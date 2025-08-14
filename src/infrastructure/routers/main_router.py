import asyncio
import random
import time
from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException
from fastapi.openapi.docs import get_swagger_ui_html
from fastapi.openapi.utils import get_openapi
from fastapi.responses import JSONResponse, HTMLResponse
from starlette.responses import RedirectResponse
from src.dependencies import get_current_user_from_session
from src.service_locator import service_locator
from src.infrastructure.session_manager import Session
from src.settings import settings

router = APIRouter(tags=["main"])


@router.get("/docs", include_in_schema=False)
async def docs(session: Session = Depends(get_current_user_from_session)):
    return get_swagger_ui_html(openapi_url="/openapi.json", title="Docs")

@router.get("/openapi.json", response_class=JSONResponse, include_in_schema=False)
async def get_openapi_json(session: Session = Depends(get_current_user_from_session)) -> JSONResponse:
    
    openapi_schema = get_openapi(
        title=settings.APP_NAME,
        version=settings.APP_VERSION,
        description="API documentation",
        routes=router.routes,
    )
    return JSONResponse(openapi_schema)
