from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session
from db import SessionLocal
from models import User, AccessToken
import httpx
from utils import ensure_valid_token, cluster_tracks_by_audio_features
from fastapi.responses import JSONResponse
import pandas as pd
from vector_db import get_index_from_track_id, get_nearest_neighbors, get_track_id_from_index, index_to_id
import random
import numpy as np

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

async def fetch_liked_songs(request: Request):
    access_token = request.state.access_token
    print(access_token)
    async with httpx.AsyncClient() as client:
        res = await client.get(
            "https://api.spotify.com/v1/me/tracks",
            headers={"Authorization": f"Bearer {access_token}"}
        )
    #res.raise_for_status()
    data = res.json()
    return data["items"]

@router.get("/me/tracks")
#@ensure_valid_token
async def get_liked_songs(request: Request):
    liked_tracks = await fetch_liked_songs(request)
    liked_tracks = [track["track"]["id"] for track in liked_tracks]
    return JSONResponse({"liked_track_ids": liked_tracks})

@router.get("/me/recommendations")
async def generate_recomendations(request: Request):
    access_token = request.state.access_token
    print("access_token: ", access_token)
    if not access_token:
        return JSONResponse({"error": "Not authenticated"}, status_code=401)

    liked_tracks = await fetch_liked_songs(request)
    liked_ids = [track["track"]["id"] for track in liked_tracks]

    liked_dicts = get_audio_features_for_tracks(liked_ids)
    print(liked_dicts)
    if len(liked_dicts) >= 5:
        centroids = cluster_tracks_by_audio_features(liked_dicts)
        recommended_indices = []
        for centroid in centroids:
            neighbors = get_nearest_neighbors(centroid, k=20)
            recommended_indices.extend(neighbors)
        recommended_ids = [get_track_id_from_index(x) for x in recommended_indices]
        recommended_ids = list(set(recommended_ids) - set(liked_ids))
    else:
        recommended_indices = []
        for v in liked_dicts:
            neighbors = get_nearest_neighbors(np.array([
                v["danceability"], v["energy"], v["valence"], v["tempo"]
            ]), k=40)
            recommended_indices.extend(neighbors)
        recommended_ids = [get_track_id_from_index(x) for x in recommended_indices]
        recommended_ids = list(set(recommended_ids) - set(liked_ids))

    final_recs = random.sample(recommended_ids, min(len(recommended_ids), 12))
    print("final_recs:", final_recs)
    print("types:", [type(x) for x in final_recs])
    return JSONResponse({"recommended_track_ids": final_recs})
'''
def get_recommendations_from_seeds(seed_track_ids: list[str], access_token: str) -> list[dict]:
    response = httpx.get(
        "https://api.spotify.com/v1/recommendations",
        params={
            "seed_tracks": ",".join(seed_track_ids),
            "limit": 10
        },
        headers={"Authorization": f"Bearer {access_token}"}
    )
    print("RESPONSE: ", response.status_code, ", ", response.text)
    return response.json().get("tracks", [])
'''
def get_audio_features_for_tracks(track_ids: list[str]) -> list[dict]:
    df = pd.read_csv("resources/songs.csv")
    df.columns = df.columns.str.strip()

    filtered = df[df["track_id"].isin(track_ids)]
    filtered = filtered[["track_id", "danceability", "energy", "valence", "tempo"]].copy()
    filtered.rename(columns={"track_id": "id"}, inplace=True)

    audio_features = filtered.to_dict(orient="records")
    return audio_features

