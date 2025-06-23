import json
from functools import wraps
from datetime import datetime, timedelta
from db import SessionLocal
from models import AccessToken, RefreshToken, SessionToken
import httpx
import os
import base64
from fastapi import Request, HTTPException
from sklearn.cluster import KMeans
import pandas as pd


CLIENT_ID = os.getenv("SPOTIFY_CLIENT_ID")
CLIENT_SECRET = os.getenv("SPOTIFY_CLIENT_SECRET")

def ensure_valid_token(func):
    @wraps(func)
    async def wrapper(request: Request, *args, **kwargs):
        session_token = request.cookies.get("session_token")
        if not session_token:
            raise HTTPException(status_code=401, detail="No session token")

        db = SessionLocal()
        session = db.query(SessionToken).filter_by(session_token=session_token).first()
        if not session:
            db.close()
            raise HTTPException(status_code=401, detail="Invalid session token")

        user_id = session.user_id
        access_token_obj = db.query(AccessToken).filter_by(user_id=user_id).order_by(AccessToken.id.desc()).first()
        refresh_token_obj = db.query(RefreshToken).filter_by(user_id=user_id).order_by(RefreshToken.id.desc()).first()

        if not access_token_obj or not refresh_token_obj:
            db.close()
            raise HTTPException(status_code=401, detail="No token info found")

        # check if token is expired or not
        if access_token_obj.expires_at < datetime.utcnow():
            print("Access token expired, refreshing...")
            client_id = os.getenv("SPOTIFY_CLIENT_ID")
            client_secret = os.getenv("SPOTIFY_CLIENT_SECRET")
            basic_auth = base64.b64encode(f"{client_id}:{client_secret}".encode()).decode()

            async with httpx.AsyncClient() as client:
                response = await client.post(
                    "https://accounts.spotify.com/api/token",
                    data={
                        "grant_type": "refresh_token",
                        "refresh_token": refresh_token_obj.refresh_token,
                    },
                    headers={
                        "Authorization": f"Basic {basic_auth}",
                        "Content-Type": "application/x-www-form-urlencoded"
                    }
                )
            if response.status_code != 200:
                db.close()
                raise HTTPException(status_code=401, detail="Failed to refresh token")

            token_data = response.json()
            new_access_token = token_data["access_token"]
            expires_in = token_data.get("expires_in", 3600)

            new_token_obj = AccessToken(
                user_id=user_id,
                access_token=new_access_token,
                expires_at=datetime.utcnow() + timedelta(seconds=expires_in)
            )
            db.add(new_token_obj)
            db.commit()

            access_token_obj = new_token_obj

        # finally, attach token to request
        request.state.access_token = access_token_obj.access_token
        db.close()

        return await func(request, *args, **kwargs)
    return wrapper


def serialize_tracks(tracks):
    return json.dumps(tracks)

def deserialize_tracks(tracks_str):
    return json.loads(tracks_str)

def retrieve_access_token_from_db(session_token: str) -> str | None:
    db: Session = SessionLocal()
    try:
        session = db.query(SessionToken).filter(SessionToken.session_token == session_token).first()
        if not session:
            return None

        access = db.query(AccessToken).filter(AccessToken.user_id == session.user_id).first()
        if access:
            return access #should be access.access_token?
    finally:
        db.close()

    return None

def retrieve_token_data_from_db(session_token):
    db: Session = SessionLocal()
    try:
        session = db.query(SessionToken).filter(SessionToken.session_token == session_token).first()
        if not session:
            return None
        access = db.query(AccessToken).filter(AccessToken.user_id == session.user_id).first()
        refresh = db.query(RefreshToken).filter(RefreshToken.user_id == session.user_id).first()
        #expires_at = #help!
        user_id = session.user_id
        if access and refresh:
            return {
                "access_token": access.access_token,
                "refresh_token": refresh.refresh_token,
                "expires_at": access.expires_at,
                "user_id": user_id,
            }
    finally:
        db.close()
    print("hi")
    return None

def refresh_access_token_and_update_db(refresh_token_str, user_id):
    db: Session = SessionLocal()
    try:
        payload = {
            "grant_type": "refresh_token",
            "refresh_token": refresh_token_str,
            "client_id": CLIENT_ID,
            "client_secret": CLIENT_SECRET
        }

        response = httpx.post("https://accounts.spotify.com/api/token", data=payload)
        response.raise_for_status()
        token_data = response.json()

        new_access_token = token_data["access_token"]
        expires_in = token_data.get("expires_in", 3600)
        expires_at = datetime.utcnow() + timedelta(seconds=expires_in)

        access_row = db.query(AccessToken).filter(AccessToken.user_id == user_id).first()
        if access_row:
            access_row.access_token = new_access_token
            access_row.expires_at = expires_at
        else:
            access_row = AccessToken(
                user_id=user_id,
                access_token=new_access_token,
                expires_at=expires_at
            )
            print("Expires at". expires_at)
            db.add(access_row)
        db.commit()
        return new_access_token
    except httpx.HTTPStatusError as e:
        print("Failed to refresh access token:", e)
        return None
    finally:
        db.close()

def cluster_tracks_by_audio_features(audio_features: list[dict]):
    df = pd.DataFrame(audio_features)
    df = df.drop_duplicates(subset="id")
    df = df.dropna(subset=["danceability", "energy", "valence", "tempo"])

    n_clusters = 3

    if df.empty or len(df) < n_clusters:
        print("Returning 0 seed ids...")
        return []

    features = df[["danceability", "energy", "valence", "tempo"]]

    kmeans = KMeans(n_clusters=n_clusters)
    kmeans.fit(features)

    centroids = kmeans.cluster_centers_

    return centroids


