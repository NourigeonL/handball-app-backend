import asyncio
import random
import time
from fastapi import APIRouter, Depends
from fastapi.openapi.docs import get_swagger_ui_html
from fastapi.openapi.utils import get_openapi
from fastapi.responses import JSONResponse
from src.dependencies import get_current_user
from src.settings import settings

router = APIRouter(tags=["main"])


@router.get("/docs", include_in_schema=False)
async def docs(current_user: dict = Depends(get_current_user)):
    return get_swagger_ui_html(openapi_url="/openapi.json", title="Docs")

@router.get("/openapi.json", response_class=JSONResponse, include_in_schema=False)
async def get_openapi_json(current_user: dict = Depends(get_current_user)) -> JSONResponse:
    
    openapi_schema = get_openapi(
        title=settings.APP_NAME,
        version=settings.APP_VERSION,
        description="API documentation",
        routes=router.routes,
    )
    return JSONResponse(openapi_schema)
