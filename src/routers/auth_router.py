from datetime import datetime, timedelta, timezone
from http.client import HTTPException
from fastapi import APIRouter, Depends, Request
from src.service_locator import service_locator
from fastapi.responses import JSONResponse, RedirectResponse
from src.settings import settings
from authlib.integrations.starlette_client import OAuth
from jose import jwt

oauth = OAuth()
oauth.register(
    name="google",
    client_id=settings.GOOGLE_AUTH_CLIENT_ID,
    client_secret=settings.GOOGLE_AUTH_CLIENT_SECRET,
    authorize_url="https://accounts.google.com/o/oauth2/auth",
    access_token_url="https://accounts.google.com/o/oauth2/token",
    jwks_uri="https://www.googleapis.com/oauth2/v3/certs",
    redirect_uri=f"{settings.BASE_URL}/auth/google",
    client_kwargs={"scope": "openid profile email"},
)


router = APIRouter(prefix="/auth", tags=["Auth"])

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
    user_info = token.get("userinfo")
    print(user_info)
    expires_in = token.get("expires_in")
    user_id = user_info.get("sub")
    iss = user_info.get("iss")
    user_email = user_info.get("email")

    if iss not in ["https://accounts.google.com", "accounts.google.com"]:
        raise HTTPException(status_code=401, detail="Google authentication failed.")

    if user_id is None:
        raise HTTPException(status_code=401, detail="Google authentication failed.")

    # Create JWT token
    access_token_expires = timedelta(seconds=expires_in)
    access_token = create_access_token(data={"sub": user_id, "email": user_email}, expires_delta=access_token_expires)

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