from datetime import datetime, timedelta, timezone
from fastapi.exceptions import HTTPException
from fastapi import APIRouter, Depends, Request, Response, Cookie
from src.common.enums import StaffMemberRole
from src.dependencies import get_current_user_from_session
from src.infrastructure.session_manager import Session
from src.service_locator import service_locator
from fastapi.responses import JSONResponse, RedirectResponse
from src.settings import settings
from authlib.integrations.starlette_client import OAuth
from jose import jwt
from pydantic import BaseModel
from typing import Annotated

oauth = OAuth()
oauth.register(
    name="google",
    client_id=settings.GOOGLE_AUTH_CLIENT_ID,
    client_secret=settings.GOOGLE_AUTH_CLIENT_SECRET,
    authorize_url="https://accounts.google.com/o/oauth2/auth",
    access_token_url="https://accounts.google.com/o/oauth2/token",
    userinfo_endpoint="https://openidconnect.googleapis.com/v1/userinfo",
    jwks_uri="https://www.googleapis.com/oauth2/v3/certs",
    redirect_uri=f"{settings.BASE_URL}/auth/google",
    client_kwargs={"scope": "openid profile email", "access_type": "offline", "prompt": "consent"},
)


router = APIRouter(prefix="/auth", tags=["Auth"])

class FrontendAuthRequest(BaseModel):
    id_token: str

def create_access_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + (expires_delta or timedelta(minutes=settings.JWT_EXPIRATION_TIME))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)


@router.get("/login")
async def login(request: Request):
    login_redirect_url = request.session.pop("login_redirect", f"{settings.BASE_URL}/docs")
    auth_redirect_url = f"{settings.BASE_URL}/auth/google"
    request.session["login_redirect"] = login_redirect_url 

    return await oauth.google.authorize_redirect(request, auth_redirect_url, prompt="consent")

@router.get("/google")
async def auth(request: Request):
    token = await oauth.google.authorize_access_token(request)
    print(token)
    user_profile = await oauth.google.userinfo(token=token)
    user_info = token.get("userinfo")
    first_name = user_profile.get("given_name")
    last_name = user_profile.get("family_name")
    name = user_profile.get("name")
    picture = user_profile.get("picture")
    expires_in = token.get("expires_in")
    user_id = user_info.get("sub")
    iss = user_info.get("iss")
    user_email = user_info.get("email")

    if iss not in ["https://accounts.google.com", "accounts.google.com"]:
        raise HTTPException(status_code=401, detail="Google authentication failed.")

    if user_id is None:
        raise HTTPException(status_code=401, detail="Google authentication failed.")

    user = await service_locator.auth_service.sign_up_user_from_google_account(google_account_id=user_id, email=user_email, first_name=first_name, last_name=last_name, name=name)
    # Create JWT token

    session = await service_locator.session_manager.create_session(Session(user_id=user.user_id, google_id_token=token.get("id_token")))


    redirect_url = request.session.pop("login_redirect", "")
    response = RedirectResponse(redirect_url)
    response.set_cookie(
        key="session_id",
        value=session,
        httponly=True,
        secure=False,  # Ensure you're using HTTPS
        samesite="lax",  # Set the SameSite attribute to None
    )
    return response

@router.post("/frontend")
async def frontend_auth(request: FrontendAuthRequest):
    """
    Authenticate user from frontend using Google ID token
    """
    try:
        # Authenticate user using the Google ID token
        user = await service_locator.auth_service.authenticate_user_from_frontend(request.id_token)
        
        session = await service_locator.session_manager.create_session(Session(user_id=user.user_id, google_id_token=request.id_token))
        
        response = JSONResponse(
            content={
                "message": "Authentication successful",
                "user_id": user.user_id,
                "session_id": session
            },
            status_code=200
        )
        
        response.set_cookie(
            key="session_id",
            value=session,
            httponly=True,
            secure=False,  # Ensure you're using HTTPS
            samesite="lax",  # Set the SameSite attribute to None
        )
        return response
        
    except ValueError as e:
        raise HTTPException(status_code=401, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail="Authentication failed")


class ClubLoginRequest(BaseModel):
    club_id: str

@router.post("/login-to-club")
async def login_to_club(
    request: ClubLoginRequest,
    session: Session = Depends(get_current_user_from_session),
    session_id: Annotated[str | None, Cookie()] = None
):
    roles = await service_locator.auth_service.get_club_roles(session.user_id, request.club_id)
    if len(roles) == 0:
        raise HTTPException(status_code=403, detail="Access denied to club")
    
    if session_id:
        await service_locator.session_manager.update_session(session_id, request.club_id)
    return JSONResponse(content={
        "roles": roles
    })

@router.post("/logout-from-club")
async def logout_from_club(
    session: Session = Depends(get_current_user_from_session),
    session_id: Annotated[str | None, Cookie()] = None
):
    if session_id:
        await service_locator.session_manager.update_session(session_id, None)

        response = JSONResponse(
                content={
                    "message": "Logout from club successful",
                },
                status_code=200
            )
        return response

@router.post("/logout")
async def logout(
    session: Session = Depends(get_current_user_from_session), 
    response: Response = Response,
    session_id: Annotated[str | None, Cookie()] = None
):
    if session_id:
        await service_locator.session_manager.delete_session(session_id)
    response.delete_cookie(key="session_id")
    return response

@router.get("/me")
async def me(session: Session = Depends(get_current_user_from_session)) -> Session:
    return session

@router.get("/session")
async def get_session(session_id: Annotated[str | None, Cookie()] = None) -> dict:
    return {
        "session_id": session_id
    }