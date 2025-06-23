from fastapi import APIRouter, Request
from fastapi.responses import RedirectResponse
import os
import base64
import httpx
from dotenv import load_dotenv
from db import SessionLocal
from models import User, AccessToken, RefreshToken, SessionToken
from datetime import datetime, timedelta
import secrets
from urllib.parse import urlencode


router = APIRouter()
load_dotenv()

CLIENT_ID = os.getenv("SPOTIFY_CLIENT_ID")
CLIENT_SECRET = os.getenv("SPOTIFY_CLIENT_SECRET")
REDIRECT_URI = os.getenv("SPOTIFY_REDIRECT_URI")
FRONTEND_URL = os.getenv("FRONTEND_URL")

@router.get("/login")
async def login():
    params = {
        "response_type": "code",
        "client_id": CLIENT_ID,
        "scope": "user-read-private user-read-email user-top-read user-library-read playlist-read-private",
        "redirect_uri": REDIRECT_URI,
        "show_dialog": "true"
    }
    login_url = "https://accounts.spotify.com/authorize?" + urlencode(params)
    return RedirectResponse(login_url)

@router.get("/callback")
async def callback(request: Request):
    code = request.query_params.get("code")
    print("Authorization code received:", code)
    if not code:
        return {"error": "No code provided"}

    basic_auth = base64.b64encode(f"{CLIENT_ID}:{CLIENT_SECRET}".encode()).decode()

    async with httpx.AsyncClient() as client:
        response = await client.post(
            "https://accounts.spotify.com/api/token",
            data = {
                "grant_type": "authorization_code",
                "code": code,
                "redirect_uri": REDIRECT_URI
            },
            headers={
                "Authorization": f"Basic {basic_auth}",
                "Content-Type": "application/x-www-form-urlencoded"
            }
        )
    print("Token exchange response:", response.status_code, response.json()) 
    if response.status_code != 200:
        return {"error": "Failed to get token", "Details": response.json()}
    tokens = response.json()
    access_token = tokens["access_token"]
    refresh_token = tokens["refresh_token"]
    expires_in = tokens["expires_in"]
    print(access_token, response.text)
    async with httpx.AsyncClient() as client:
        profile_resp = await client.get("https://api.spotify.com/v1/me", headers={"Authorization": f"Bearer {access_token}"})
    if profile_resp.status_code != 200:
        return {"error": f"Failed to fetch user profile: {profile_resp.status_code}"}
    profile = profile_resp.json()
    spotify_id = profile["id"]
    display_name = profile.get("display_name", "")
    print(profile)
    db = SessionLocal()
    user = db.query(User).filter_by(spotify_id=spotify_id).first()

    if not user:
        user = User(spotify_id=spotify_id, display_name=display_name)
        db.add(user)
        db.commit()
        db.refresh(user)
    db.add(AccessToken(
        user_id=user.id,
        access_token=access_token,
        expires_at=datetime.utcnow() + timedelta(seconds=expires_in)
    ))
    db.add(RefreshToken(
        user_id=user.id,
        refresh_token=refresh_token
    ))
    session_token = secrets.token_urlsafe(32)
    db.add(SessionToken(
        user_id=user.id,
        session_token=session_token
    ))
    db.commit()
    db.close()

    response = RedirectResponse(url=FRONTEND_URL, status_code=302)
    response.set_cookie(
        key="session_token",
        value=session_token,
        httponly=True,
        max_age=60*60*24*7,
        secure=True,
        samesite="none",
    )

    return response

@router.get("/logout")
async def logout(request: Request):
    response = RedirectResponse(url=FRONTEND_URL)
    response.delete_cookie(key="session_token", path="/")
    return response
