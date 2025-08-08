from fastapi import FastAPI, Request
from starlette.responses import JSONResponse
from src.common.exceptions import GenericError
from src.dependencies import lifespan
from src.routers.club_router import router as club_router
from src.routers.auth_router import router as auth_router
from src.features.federation.router import router as federation_router
from src.main_router import router as main_router
from starlette.middleware.sessions import SessionMiddleware
from src.settings import settings

def create_app() -> FastAPI:
    
    app = FastAPI(lifespan=lifespan, docs_url=None, redoc_url=None)
    app.add_middleware(SessionMiddleware, secret_key=settings.JWT_SECRET_KEY)
    app.include_router(club_router)
    app.include_router(auth_router)
    app.include_router(main_router)
    app.include_router(federation_router)
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