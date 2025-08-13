from datetime import datetime, timedelta, timezone
from fastapi.exceptions import HTTPException
from fastapi import APIRouter, Depends, Request, Response
from src.dependencies import UserSession, get_current_user, get_current_user_from_token
from src.service_locator import service_locator
from fastapi.responses import JSONResponse, RedirectResponse
from src.settings import settings
from authlib.integrations.starlette_client import OAuth
from jose import jwt
from pydantic import BaseModel

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
    access_token_expires = timedelta(seconds=expires_in)
    access_token = create_access_token(data={"user_id": user.user_id, "email": user_email, "first_name": first_name, "last_name": last_name, "name": name, "picture": picture}, expires_delta=access_token_expires)

    redirect_url = request.session.pop("login_redirect", "")
    response = RedirectResponse(redirect_url)
    response.set_cookie(
        key="access_token",
        value=access_token,
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
        
        # Create JWT token
        access_token_expires = timedelta(minutes=settings.JWT_EXPIRATION_TIME)
        access_token = create_access_token(
            data={
                "user_id": user.user_id, 
                "email": user.email
            }, 
            expires_delta=access_token_expires
        )
        
        return JSONResponse(content={
            "access_token": access_token,
            "token_type": "bearer",
            "expires_in": settings.JWT_EXPIRATION_TIME * 60,  # Convert to seconds
            "user": {
                "user_id": user.user_id,
                "email": user.email,
                "google_account_id": user.google_account_id
            }
        })
        
    except ValueError as e:
        raise HTTPException(status_code=401, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail="Authentication failed")

@router.get("/test-token")
async def test_bearer_token(current_user: UserSession = Depends(get_current_user_from_token)):
    """
    Test endpoint to verify Bearer token authentication is working
    Use this to test your Authorization header: 'Authorization: Bearer <your_token>'
    """
    return {
        "message": "Bearer token authentication successful!",
        "user": {
            "user_id": current_user.user_id,
            "email": current_user.user_email
        },
        "timestamp": datetime.now().isoformat()
    }