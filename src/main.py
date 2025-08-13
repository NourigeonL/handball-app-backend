from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from starlette.responses import JSONResponse
from src.common.exceptions import GenericError
from src.dependencies import lifespan
from src.infrastructure.routers.club_router import router as club_router
from src.infrastructure.routers.auth_router import router as auth_router
from src.infrastructure.routers.main_router import router as main_router
from src.infrastructure.routers.player_router import router as player_router
from src.infrastructure.routers.collective_router import router as collective_router
from src.infrastructure.routers.public.public_router import router as public_router
from starlette.middleware.sessions import SessionMiddleware
from src.settings import settings

def create_app() -> FastAPI:
    
    app = FastAPI(lifespan=lifespan, docs_url=None, redoc_url=None)
    
    # Add CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # In production, specify your frontend domain
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    app.add_middleware(SessionMiddleware, secret_key=settings.JWT_SECRET_KEY)
    app.include_router(club_router)
    app.include_router(auth_router)
    app.include_router(main_router)
    app.include_router(player_router)
    app.include_router(collective_router)
    app.include_router(public_router)
    return app


app = create_app()

@app.exception_handler(GenericError)
async def all_exception_handler(request: Request, exc: GenericError) -> JSONResponse:
    return JSONResponse(
        status_code=exc.status_code,
        content=exc.json(),
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)