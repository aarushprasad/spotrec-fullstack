from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from dotenv import load_dotenv
from spotify_auth import router as auth_router
from spotify_api import router as api_router
import os
from db import Base, engine
import models
from utils import retrieve_token_data_from_db, refresh_access_token_and_update_db
from datetime import datetime
from vector_db import load_faiss_index

models.Base.metadata.create_all(bind=engine)

load_dotenv()

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

@app.on_event("startup")
def startup_event():
    load_faiss_index()

@app.get("/")
async def root():
    return {"message": "SpotRec Backend is live!"}
app.include_router(auth_router, prefix="/auth")
app.include_router(api_router, prefix="/api")

@app.middleware("http")
async def inject_access_token(request: Request, call_next):
    session_token = request.cookies.get("session_token")
    if not session_token:
        #return JSONResponse({"error": "Missing session token"}, status_code=401)
        request.state.access_token = None
        return await call_next(request)
    token_data = retrieve_token_data_from_db(session_token)
    print(token_data)
    if token_data is None:
        #return JSONResponse({"error": "Invalid session token"}, status_code=401)
        request.state.access_token = None
        return await call_next(request)
    if datetime.utcnow() >= token_data["expires_at"]:
        print("Access token expired, refreshing...")
        new_access_token = refresh_access_token_and_update_db(token_data["refresh_token"], token_data["user_id"])
        request.state.access_token = new_access_token
    else:
        request.state.access_token = token_data["access_token"]
    return await call_next(request)

