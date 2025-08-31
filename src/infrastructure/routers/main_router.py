import asyncio
import random
import time
from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.openapi.docs import get_swagger_ui_html
from fastapi.openapi.utils import get_openapi
from fastapi.responses import JSONResponse, HTMLResponse
from starlette.responses import RedirectResponse
from src.dependencies import get_current_user_from_session, get_current_user_from_websocket
from src.service_locator import service_locator
from src.infrastructure.session_manager import Session
from src.settings import settings
from src.common.loggers import app_logger

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

@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket, current_user : Annotated[Session, Depends(get_current_user_from_websocket)]):
    await websocket.accept()
    await service_locator.websocket_manager.register_connection(websocket, current_user.club_id)
    try:
        while True:
            data = await websocket.receive_text()
            if data == "ping":
                await websocket.send_text("pong")
            else:
                await websocket.send_text(f"Message received: {data}")
    except WebSocketDisconnect:
        app_logger.info(f"WebSocket connection closed for club {current_user.club_id}")
        await service_locator.websocket_manager.unregister_connection(websocket)
    except Exception as e:
        app_logger.error(f"Error in websocket: {e}")
        app_logger.debug(f"Unregistering websocket connection for club {current_user.club_id}")
        await service_locator.websocket_manager.unregister_connection(websocket)