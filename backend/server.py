from dotenv import load_dotenv
load_dotenv()

from fastapi import FastAPI, APIRouter, HTTPException, Request, Response, File, UploadFile, Depends, Header, Query
from fastapi.responses import StreamingResponse
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
from bson import ObjectId
import os
import logging
import uuid
import secrets
import bcrypt
import jwt
import requests
from pathlib import Path
from pydantic import BaseModel, Field, ConfigDict, EmailStr
from typing import List, Optional, Dict, Any
from datetime import datetime, timezone, timedelta
from io import BytesIO

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

# JWT Configuration
JWT_ALGORITHM = "HS256"
def get_jwt_secret() -> str:
    return os.environ["JWT_SECRET"]

# Object Storage Configuration
STORAGE_URL = "https://integrations.emergentagent.com/objstore/api/v1/storage"
EMERGENT_KEY = os.environ.get("EMERGENT_LLM_KEY")
APP_NAME = "tunedrop"
storage_key = None

# Create the main app
app = FastAPI(title="TuneDrop Music Distribution API")

# Create router with /api prefix
api_router = APIRouter(prefix="/api")

# ============= MODELS =============
class UserCreate(BaseModel):
    email: EmailStr
    password: str
    name: str
    artist_name: Optional[str] = None

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserResponse(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str
    email: str
    name: str
    artist_name: Optional[str] = None
    role: str = "artist"
    plan: str = "free"
    avatar_url: Optional[str] = None
    created_at: str

class ArtistProfile(BaseModel):
    artist_name: str
    bio: Optional[str] = None
    genre: Optional[str] = None
    country: Optional[str] = None
    website: Optional[str] = None
    spotify_url: Optional[str] = None
    apple_music_url: Optional[str] = None
    instagram: Optional[str] = None
    twitter: Optional[str] = None

class ReleaseCreate(BaseModel):
    title: str
    release_type: str = "single"  # single, ep, album
    genre: str
    subgenre: Optional[str] = None
    release_date: str
    description: Optional[str] = None
    explicit: bool = False
    language: str = "en"

class ReleaseResponse(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str
    upc: str
    title: str
    release_type: str
    genre: str
    subgenre: Optional[str] = None
    release_date: str
    description: Optional[str] = None
    explicit: bool
    language: str
    cover_art_url: Optional[str] = None
    status: str
    artist_id: str
    artist_name: str
    track_count: int = 0
    created_at: str
    payment_status: str = "pending"

class TrackCreate(BaseModel):
    release_id: str
    title: str
    track_number: int
    duration: Optional[int] = None
    explicit: bool = False
    lyrics: Optional[str] = None
    composers: Optional[List[str]] = []
    producers: Optional[List[str]] = []

class TrackResponse(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str
    isrc: str
    release_id: str
    title: str
    track_number: int
    duration: Optional[int] = None
    explicit: bool
    audio_url: Optional[str] = None
    status: str
    created_at: str

class DistributionStore(BaseModel):
    store_id: str
    store_name: str
    enabled: bool = True

class WalletResponse(BaseModel):
    balance: float
    pending_balance: float
    currency: str = "USD"
    total_earnings: float
    total_withdrawn: float

class WithdrawalRequest(BaseModel):
    amount: float
    method: str  # paypal, bank_transfer
    paypal_email: Optional[str] = None

class PaymentCheckout(BaseModel):
    release_id: str
    origin_url: str

class AnalyticsResponse(BaseModel):
    total_streams: int
    total_downloads: int
    total_earnings: float
    streams_by_store: Dict[str, int]
    streams_by_country: Dict[str, int]
    daily_streams: List[Dict[str, Any]]

class AIMetadataRequest(BaseModel):
    title: str
    artist_name: str
    audio_features: Optional[Dict[str, Any]] = None

class AIDescriptionRequest(BaseModel):
    title: str
    artist_name: str
    genre: str
    mood: Optional[str] = None

# ============= SPLIT PAYMENT MODELS =============
class Collaborator(BaseModel):
    name: str
    email: EmailStr
    role: str  # songwriter, producer, featured_artist, etc.
    percentage: float

class SplitCreate(BaseModel):
    track_id: str
    collaborators: List[Collaborator]

class SplitUpdate(BaseModel):
    collaborators: List[Collaborator]

# ============= ADMIN MODELS =============
class AdminReviewAction(BaseModel):
    action: str  # approve, reject
    notes: Optional[str] = None

class AdminUserUpdate(BaseModel):
    role: Optional[str] = None
    plan: Optional[str] = None
    status: Optional[str] = None  # active, suspended

# ============= HELPER FUNCTIONS =============
def hash_password(password: str) -> str:
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password.encode("utf-8"), salt)
    return hashed.decode("utf-8")

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return bcrypt.checkpw(plain_password.encode("utf-8"), hashed_password.encode("utf-8"))

def create_access_token(user_id: str, email: str) -> str:
    payload = {"sub": user_id, "email": email, "exp": datetime.now(timezone.utc) + timedelta(minutes=60), "type": "access"}
    return jwt.encode(payload, get_jwt_secret(), algorithm=JWT_ALGORITHM)

def create_refresh_token(user_id: str) -> str:
    payload = {"sub": user_id, "exp": datetime.now(timezone.utc) + timedelta(days=7), "type": "refresh"}
    return jwt.encode(payload, get_jwt_secret(), algorithm=JWT_ALGORITHM)

def generate_upc() -> str:
    """Generate a unique 12-digit UPC code"""
    return f"8{secrets.randbelow(10**11):011d}"

def generate_isrc() -> str:
    """Generate a unique ISRC code (CC-XXX-YY-NNNNN)"""
    country = "US"
    registrant = "TD" + secrets.token_hex(1).upper()[:1]
    year = str(datetime.now().year)[2:]
    designation = f"{secrets.randbelow(100000):05d}"
    return f"{country}{registrant}{year}{designation}"

async def get_current_user(request: Request) -> dict:
    token = request.cookies.get("access_token")
    if not token:
        auth_header = request.headers.get("Authorization", "")
        if auth_header.startswith("Bearer "):
            token = auth_header[7:]
    if not token:
        raise HTTPException(status_code=401, detail="Not authenticated")
    try:
        payload = jwt.decode(token, get_jwt_secret(), algorithms=[JWT_ALGORITHM])
        if payload.get("type") != "access":
            raise HTTPException(status_code=401, detail="Invalid token type")
        user = await db.users.find_one({"id": payload["sub"]}, {"_id": 0})
        if not user:
            raise HTTPException(status_code=401, detail="User not found")
        if user.get("status") == "suspended":
            raise HTTPException(status_code=403, detail="Account suspended")
        user.pop("password_hash", None)
        return user
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")

async def require_admin(request: Request) -> dict:
    user = await get_current_user(request)
    if user.get("role") != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")
    return user

# Object Storage helpers
def init_storage():
    global storage_key
    if storage_key:
        return storage_key
    try:
        resp = requests.post(f"{STORAGE_URL}/init", json={"emergent_key": EMERGENT_KEY}, timeout=30)
        resp.raise_for_status()
        storage_key = resp.json()["storage_key"]
        return storage_key
    except Exception as e:
        logger.error(f"Storage init failed: {e}")
        return None

def put_object(path: str, data: bytes, content_type: str) -> dict:
    key = init_storage()
    if not key:
        raise HTTPException(status_code=500, detail="Storage unavailable")
    resp = requests.put(
        f"{STORAGE_URL}/objects/{path}",
        headers={"X-Storage-Key": key, "Content-Type": content_type},
        data=data, timeout=120
    )
    resp.raise_for_status()
    return resp.json()

def get_object(path: str) -> tuple:
    key = init_storage()
    if not key:
        raise HTTPException(status_code=500, detail="Storage unavailable")
    resp = requests.get(
        f"{STORAGE_URL}/objects/{path}",
        headers={"X-Storage-Key": key}, timeout=60
    )
    resp.raise_for_status()
    return resp.content, resp.headers.get("Content-Type", "application/octet-stream")

# ============= AUTH ENDPOINTS =============
@api_router.post("/auth/register")
async def register(user_data: UserCreate, response: Response):
    email = user_data.email.lower()
    existing = await db.users.find_one({"email": email})
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    user_id = f"user_{uuid.uuid4().hex[:12]}"
    user_doc = {
        "id": user_id,
        "email": email,
        "name": user_data.name,
        "artist_name": user_data.artist_name or user_data.name,
        "password_hash": hash_password(user_data.password),
        "role": "artist",
        "plan": "free",
        "avatar_url": None,
        "created_at": datetime.now(timezone.utc).isoformat()
    }
    await db.users.insert_one(user_doc)
    
    # Create wallet for user
    await db.wallets.insert_one({
        "user_id": user_id,
        "balance": 0.0,
        "pending_balance": 0.0,
        "currency": "USD",
        "total_earnings": 0.0,
        "total_withdrawn": 0.0,
        "created_at": datetime.now(timezone.utc).isoformat()
    })
    
    access_token = create_access_token(user_id, email)
    refresh_token = create_refresh_token(user_id)
    
    response.set_cookie(key="access_token", value=access_token, httponly=True, secure=True, samesite="none", max_age=3600, path="/")
    response.set_cookie(key="refresh_token", value=refresh_token, httponly=True, secure=True, samesite="none", max_age=604800, path="/")
    
    user_doc.pop("password_hash", None)
    user_doc.pop("_id", None)
    return user_doc

@api_router.post("/auth/login")
async def login(credentials: UserLogin, response: Response):
    email = credentials.email.lower()
    user = await db.users.find_one({"email": email}, {"_id": 0})
    if not user:
        raise HTTPException(status_code=401, detail="Invalid email or password")
    
    if not verify_password(credentials.password, user["password_hash"]):
        raise HTTPException(status_code=401, detail="Invalid email or password")
    
    access_token = create_access_token(user["id"], email)
    refresh_token = create_refresh_token(user["id"])
    
    response.set_cookie(key="access_token", value=access_token, httponly=True, secure=True, samesite="none", max_age=3600, path="/")
    response.set_cookie(key="refresh_token", value=refresh_token, httponly=True, secure=True, samesite="none", max_age=604800, path="/")
    
    user.pop("password_hash", None)
    return user

@api_router.get("/auth/me")
async def get_me(request: Request):
    user = await get_current_user(request)
    return user

@api_router.post("/auth/logout")
async def logout(response: Response):
    response.delete_cookie(key="access_token", path="/")
    response.delete_cookie(key="refresh_token", path="/")
    return {"message": "Logged out successfully"}

@api_router.post("/auth/refresh")
async def refresh_token(request: Request, response: Response):
    token = request.cookies.get("refresh_token")
    if not token:
        raise HTTPException(status_code=401, detail="No refresh token")
    try:
        payload = jwt.decode(token, get_jwt_secret(), algorithms=[JWT_ALGORITHM])
        if payload.get("type") != "refresh":
            raise HTTPException(status_code=401, detail="Invalid token type")
        user = await db.users.find_one({"id": payload["sub"]}, {"_id": 0})
        if not user:
            raise HTTPException(status_code=401, detail="User not found")
        access_token = create_access_token(user["id"], user["email"])
        response.set_cookie(key="access_token", value=access_token, httponly=True, secure=True, samesite="none", max_age=3600, path="/")
        return {"message": "Token refreshed"}
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid refresh token")

# Google OAuth Session endpoint
@api_router.post("/auth/session")
async def process_google_session(request: Request, response: Response):
    body = await request.json()
    session_id = body.get("session_id")
    if not session_id:
        raise HTTPException(status_code=400, detail="Session ID required")
    
    try:
        # Call Emergent Auth to get session data
        resp = requests.get(
            "https://demobackend.emergentagent.com/auth/v1/env/oauth/session-data",
            headers={"X-Session-ID": session_id},
            timeout=10
        )
        resp.raise_for_status()
        session_data = resp.json()
        
        email = session_data["email"].lower()
        user = await db.users.find_one({"email": email}, {"_id": 0})
        
        if not user:
            # Create new user from Google auth
            user_id = f"user_{uuid.uuid4().hex[:12]}"
            user = {
                "id": user_id,
                "email": email,
                "name": session_data["name"],
                "artist_name": session_data["name"],
                "password_hash": "",  # No password for OAuth users
                "role": "artist",
                "plan": "free",
                "avatar_url": session_data.get("picture"),
                "auth_provider": "google",
                "created_at": datetime.now(timezone.utc).isoformat()
            }
            await db.users.insert_one(user)
            await db.wallets.insert_one({
                "user_id": user_id,
                "balance": 0.0,
                "pending_balance": 0.0,
                "currency": "USD",
                "total_earnings": 0.0,
                "total_withdrawn": 0.0,
                "created_at": datetime.now(timezone.utc).isoformat()
            })
        
        access_token = create_access_token(user["id"], email)
        refresh_token = create_refresh_token(user["id"])
        
        response.set_cookie(key="access_token", value=access_token, httponly=True, secure=True, samesite="none", max_age=3600, path="/")
        response.set_cookie(key="refresh_token", value=refresh_token, httponly=True, secure=True, samesite="none", max_age=604800, path="/")
        
        user.pop("password_hash", None)
        user.pop("_id", None)
        return user
    except Exception as e:
        logger.error(f"Google auth error: {e}")
        raise HTTPException(status_code=400, detail="Failed to process Google authentication")

# ============= ARTIST ENDPOINTS =============
@api_router.get("/artists/profile")
async def get_artist_profile(request: Request):
    user = await get_current_user(request)
    profile = await db.artist_profiles.find_one({"user_id": user["id"]}, {"_id": 0})
    if not profile:
        return {
            "user_id": user["id"],
            "artist_name": user.get("artist_name", user["name"]),
            "bio": None,
            "genre": None,
            "country": None,
            "website": None,
            "spotify_url": None,
            "apple_music_url": None,
            "instagram": None,
            "twitter": None
        }
    return profile

@api_router.put("/artists/profile")
async def update_artist_profile(profile: ArtistProfile, request: Request):
    user = await get_current_user(request)
    profile_doc = profile.model_dump()
    profile_doc["user_id"] = user["id"]
    profile_doc["updated_at"] = datetime.now(timezone.utc).isoformat()
    
    await db.artist_profiles.update_one(
        {"user_id": user["id"]},
        {"$set": profile_doc},
        upsert=True
    )
    
    # Update artist_name in users collection too
    await db.users.update_one(
        {"id": user["id"]},
        {"$set": {"artist_name": profile.artist_name}}
    )
    
    return {"message": "Profile updated", **profile_doc}

@api_router.post("/artists/avatar")
async def upload_avatar(request: Request, file: UploadFile = File(...)):
    user = await get_current_user(request)
    
    if not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="File must be an image")
    
    ext = file.filename.split(".")[-1] if "." in file.filename else "jpg"
    path = f"{APP_NAME}/avatars/{user['id']}/{uuid.uuid4()}.{ext}"
    data = await file.read()
    
    result = put_object(path, data, file.content_type)
    
    await db.users.update_one(
        {"id": user["id"]},
        {"$set": {"avatar_url": result["path"]}}
    )
    
    return {"avatar_url": result["path"]}

# ============= RELEASE ENDPOINTS =============
@api_router.post("/releases", response_model=ReleaseResponse)
async def create_release(release: ReleaseCreate, request: Request):
    user = await get_current_user(request)
    
    release_id = f"rel_{uuid.uuid4().hex[:12]}"
    upc = generate_upc()
    
    release_doc = {
        "id": release_id,
        "upc": upc,
        "artist_id": user["id"],
        "artist_name": user.get("artist_name", user["name"]),
        **release.model_dump(),
        "cover_art_url": None,
        "status": "draft",
        "track_count": 0,
        "payment_status": "pending",
        "created_at": datetime.now(timezone.utc).isoformat()
    }
    
    await db.releases.insert_one(release_doc)
    release_doc.pop("_id", None)
    return release_doc

@api_router.get("/releases")
async def get_releases(request: Request, status: Optional[str] = None):
    user = await get_current_user(request)
    query = {"artist_id": user["id"]}
    if status:
        query["status"] = status
    
    releases = await db.releases.find(query, {"_id": 0}).sort("created_at", -1).to_list(100)
    return releases

@api_router.get("/releases/{release_id}")
async def get_release(release_id: str, request: Request):
    user = await get_current_user(request)
    release = await db.releases.find_one({"id": release_id, "artist_id": user["id"]}, {"_id": 0})
    if not release:
        raise HTTPException(status_code=404, detail="Release not found")
    
    # Get tracks for this release
    tracks = await db.tracks.find({"release_id": release_id}, {"_id": 0}).sort("track_number", 1).to_list(50)
    release["tracks"] = tracks
    
    return release

@api_router.post("/releases/{release_id}/cover")
async def upload_cover_art(release_id: str, request: Request, file: UploadFile = File(...)):
    user = await get_current_user(request)
    release = await db.releases.find_one({"id": release_id, "artist_id": user["id"]})
    if not release:
        raise HTTPException(status_code=404, detail="Release not found")
    
    if not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="File must be an image")
    
    ext = file.filename.split(".")[-1] if "." in file.filename else "jpg"
    path = f"{APP_NAME}/covers/{user['id']}/{release_id}/{uuid.uuid4()}.{ext}"
    data = await file.read()
    
    result = put_object(path, data, file.content_type)
    
    await db.releases.update_one(
        {"id": release_id},
        {"$set": {"cover_art_url": result["path"]}}
    )
    
    return {"cover_art_url": result["path"]}

@api_router.put("/releases/{release_id}")
async def update_release(release_id: str, release: ReleaseCreate, request: Request):
    user = await get_current_user(request)
    existing = await db.releases.find_one({"id": release_id, "artist_id": user["id"]})
    if not existing:
        raise HTTPException(status_code=404, detail="Release not found")
    
    await db.releases.update_one(
        {"id": release_id},
        {"$set": {**release.model_dump(), "updated_at": datetime.now(timezone.utc).isoformat()}}
    )
    
    return {"message": "Release updated"}

@api_router.delete("/releases/{release_id}")
async def delete_release(release_id: str, request: Request):
    user = await get_current_user(request)
    result = await db.releases.delete_one({"id": release_id, "artist_id": user["id"], "status": "draft"})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Release not found or cannot be deleted")
    
    # Delete associated tracks
    await db.tracks.delete_many({"release_id": release_id})
    
    return {"message": "Release deleted"}

# ============= TRACK ENDPOINTS =============
@api_router.post("/tracks", response_model=TrackResponse)
async def create_track(track: TrackCreate, request: Request):
    user = await get_current_user(request)
    
    # Verify release belongs to user
    release = await db.releases.find_one({"id": track.release_id, "artist_id": user["id"]})
    if not release:
        raise HTTPException(status_code=404, detail="Release not found")
    
    track_id = f"trk_{uuid.uuid4().hex[:12]}"
    isrc = generate_isrc()
    
    track_doc = {
        "id": track_id,
        "isrc": isrc,
        "artist_id": user["id"],
        **track.model_dump(),
        "audio_url": None,
        "status": "pending",
        "created_at": datetime.now(timezone.utc).isoformat()
    }
    
    await db.tracks.insert_one(track_doc)
    
    # Update track count on release
    await db.releases.update_one(
        {"id": track.release_id},
        {"$inc": {"track_count": 1}}
    )
    
    track_doc.pop("_id", None)
    return track_doc

@api_router.post("/tracks/{track_id}/audio")
async def upload_audio(track_id: str, request: Request, file: UploadFile = File(...)):
    user = await get_current_user(request)
    track = await db.tracks.find_one({"id": track_id, "artist_id": user["id"]})
    if not track:
        raise HTTPException(status_code=404, detail="Track not found")
    
    allowed_types = ["audio/wav", "audio/mpeg", "audio/mp3", "audio/x-wav", "audio/flac"]
    if file.content_type not in allowed_types:
        raise HTTPException(status_code=400, detail="File must be WAV, MP3, or FLAC")
    
    ext = file.filename.split(".")[-1] if "." in file.filename else "wav"
    path = f"{APP_NAME}/audio/{user['id']}/{track['release_id']}/{track_id}.{ext}"
    data = await file.read()
    
    result = put_object(path, data, file.content_type)
    
    # Estimate duration (rough calculation based on file size for WAV)
    duration = len(data) // (44100 * 2 * 2)  # Rough estimate for 16-bit stereo 44.1kHz
    
    await db.tracks.update_one(
        {"id": track_id},
        {"$set": {"audio_url": result["path"], "duration": duration, "status": "ready"}}
    )
    
    return {"audio_url": result["path"], "duration": duration}

@api_router.get("/tracks/{track_id}/stream")
async def stream_audio(track_id: str, request: Request):
    user = await get_current_user(request)
    track = await db.tracks.find_one({"id": track_id}, {"_id": 0})
    if not track or not track.get("audio_url"):
        raise HTTPException(status_code=404, detail="Track or audio not found")
    
    data, content_type = get_object(track["audio_url"])
    
    return StreamingResponse(
        BytesIO(data),
        media_type=content_type,
        headers={"Content-Disposition": f"inline; filename={track['title']}.{track['audio_url'].split('.')[-1]}"}
    )

@api_router.delete("/tracks/{track_id}")
async def delete_track(track_id: str, request: Request):
    user = await get_current_user(request)
    track = await db.tracks.find_one({"id": track_id, "artist_id": user["id"]})
    if not track:
        raise HTTPException(status_code=404, detail="Track not found")
    
    await db.tracks.delete_one({"id": track_id})
    
    # Update track count on release
    await db.releases.update_one(
        {"id": track["release_id"]},
        {"$inc": {"track_count": -1}}
    )
    
    return {"message": "Track deleted"}

# ============= DISTRIBUTION ENDPOINTS =============
DSP_STORES = [
    {"store_id": "spotify", "store_name": "Spotify", "icon": "spotify"},
    {"store_id": "apple_music", "store_name": "Apple Music", "icon": "apple"},
    {"store_id": "amazon_music", "store_name": "Amazon Music", "icon": "amazon"},
    {"store_id": "youtube_music", "store_name": "YouTube Music", "icon": "youtube"},
    {"store_id": "tidal", "store_name": "Tidal", "icon": "tidal"},
    {"store_id": "deezer", "store_name": "Deezer", "icon": "deezer"},
    {"store_id": "soundcloud", "store_name": "SoundCloud", "icon": "soundcloud"},
    {"store_id": "pandora", "store_name": "Pandora", "icon": "pandora"},
    {"store_id": "tiktok", "store_name": "TikTok", "icon": "tiktok"},
    {"store_id": "instagram", "store_name": "Instagram/Facebook", "icon": "instagram"},
]

@api_router.get("/distributions/stores")
async def get_distribution_stores():
    return DSP_STORES

@api_router.post("/distributions/submit/{release_id}")
async def submit_distribution(release_id: str, stores: List[str], request: Request):
    user = await get_current_user(request)
    release = await db.releases.find_one({"id": release_id, "artist_id": user["id"]}, {"_id": 0})
    if not release:
        raise HTTPException(status_code=404, detail="Release not found")
    
    # Check if release has cover art and at least one track
    if not release.get("cover_art_url"):
        raise HTTPException(status_code=400, detail="Release must have cover art")
    
    tracks = await db.tracks.find({"release_id": release_id, "audio_url": {"$ne": None}}).to_list(50)
    if not tracks:
        raise HTTPException(status_code=400, detail="Release must have at least one track with audio")
    
    # Check payment status for paid plans
    if user.get("plan") != "free" and release.get("payment_status") != "paid":
        raise HTTPException(status_code=400, detail="Payment required before distribution")
    
    # Create distribution records
    for store_id in stores:
        store = next((s for s in DSP_STORES if s["store_id"] == store_id), None)
        if store:
            await db.distributions.update_one(
                {"release_id": release_id, "store_id": store_id},
                {"$set": {
                    "release_id": release_id,
                    "artist_id": user["id"],
                    "store_id": store_id,
                    "store_name": store["store_name"],
                    "status": "pending_review",
                    "submitted_at": datetime.now(timezone.utc).isoformat()
                }},
                upsert=True
            )
    
    # Create ingestion submission record
    submission_id = f"sub_{uuid.uuid4().hex[:12]}"
    await db.submissions.update_one(
        {"release_id": release_id},
        {"$set": {
            "id": submission_id,
            "release_id": release_id,
            "artist_id": user["id"],
            "artist_name": user.get("artist_name", user["name"]),
            "release_title": release["title"],
            "release_type": release["release_type"],
            "genre": release.get("genre", ""),
            "track_count": len(tracks),
            "stores": stores,
            "status": "pending_review",
            "submitted_at": datetime.now(timezone.utc).isoformat(),
            "reviewed_at": None,
            "reviewed_by": None,
            "review_notes": None
        }},
        upsert=True
    )
    
    # Update release status to pending_review (ingestion pipeline)
    await db.releases.update_one(
        {"id": release_id},
        {"$set": {"status": "pending_review", "submitted_stores": stores}}
    )
    
    # Notify admin
    await db.notifications.insert_one({
        "id": f"notif_{uuid.uuid4().hex[:12]}",
        "user_id": "admin",
        "type": "new_submission",
        "message": f"New submission: {release['title']} by {user.get('artist_name', user['name'])}",
        "release_id": release_id,
        "read": False,
        "created_at": datetime.now(timezone.utc).isoformat()
    })
    
    return {"message": f"Submitted for review to {len(stores)} stores", "stores": stores, "status": "pending_review"}

@api_router.get("/distributions/{release_id}")
async def get_distribution_status(release_id: str, request: Request):
    user = await get_current_user(request)
    distributions = await db.distributions.find(
        {"release_id": release_id, "artist_id": user["id"]},
        {"_id": 0}
    ).to_list(20)
    return distributions

# ============= PAYMENT ENDPOINTS =============
RELEASE_PRICES = {
    "single": 20.00,
    "ep": 35.00,
    "album": 50.00
}

@api_router.post("/payments/checkout")
async def create_checkout(checkout: PaymentCheckout, request: Request):
    from emergentintegrations.payments.stripe.checkout import StripeCheckout, CheckoutSessionRequest
    
    user = await get_current_user(request)
    release = await db.releases.find_one({"id": checkout.release_id, "artist_id": user["id"]})
    if not release:
        raise HTTPException(status_code=404, detail="Release not found")
    
    if user.get("plan") == "free":
        # Free plan - no payment needed but Kalmori takes 15%
        await db.releases.update_one(
            {"id": checkout.release_id},
            {"$set": {"payment_status": "free_tier"}}
        )
        return {"message": "Free tier activated", "redirect_url": None}
    
    amount = RELEASE_PRICES.get(release["release_type"], 20.00)
    
    stripe_api_key = os.environ.get("STRIPE_API_KEY")
    host_url = str(request.base_url)
    webhook_url = f"{host_url}api/webhook/stripe"
    
    stripe_checkout = StripeCheckout(api_key=stripe_api_key, webhook_url=webhook_url)
    
    success_url = f"{checkout.origin_url}/releases/{checkout.release_id}?payment=success&session_id={{CHECKOUT_SESSION_ID}}"
    cancel_url = f"{checkout.origin_url}/releases/{checkout.release_id}?payment=cancelled"
    
    checkout_request = CheckoutSessionRequest(
        amount=amount,
        currency="usd",
        success_url=success_url,
        cancel_url=cancel_url,
        metadata={
            "release_id": checkout.release_id,
            "user_id": user["id"],
            "release_type": release["release_type"]
        }
    )
    
    session = await stripe_checkout.create_checkout_session(checkout_request)
    
    # Record payment transaction
    await db.payment_transactions.insert_one({
        "id": f"txn_{uuid.uuid4().hex[:12]}",
        "session_id": session.session_id,
        "user_id": user["id"],
        "release_id": checkout.release_id,
        "amount": amount,
        "currency": "usd",
        "payment_status": "pending",
        "provider": "stripe",
        "created_at": datetime.now(timezone.utc).isoformat()
    })
    
    return {"checkout_url": session.url, "session_id": session.session_id}

@api_router.get("/payments/status/{session_id}")
async def check_payment_status(session_id: str, request: Request):
    from emergentintegrations.payments.stripe.checkout import StripeCheckout
    
    stripe_api_key = os.environ.get("STRIPE_API_KEY")
    host_url = str(request.base_url)
    webhook_url = f"{host_url}api/webhook/stripe"
    
    stripe_checkout = StripeCheckout(api_key=stripe_api_key, webhook_url=webhook_url)
    status = await stripe_checkout.get_checkout_status(session_id)
    
    # Update transaction and release if paid
    if status.payment_status == "paid":
        txn = await db.payment_transactions.find_one({"session_id": session_id})
        if txn and txn["payment_status"] != "paid":
            await db.payment_transactions.update_one(
                {"session_id": session_id},
                {"$set": {"payment_status": "paid", "paid_at": datetime.now(timezone.utc).isoformat()}}
            )
            await db.releases.update_one(
                {"id": txn["release_id"]},
                {"$set": {"payment_status": "paid"}}
            )
    
    return {
        "status": status.status,
        "payment_status": status.payment_status,
        "amount": status.amount_total / 100,  # Convert from cents
        "currency": status.currency
    }

@api_router.post("/webhook/stripe")
async def stripe_webhook(request: Request):
    from emergentintegrations.payments.stripe.checkout import StripeCheckout
    
    body = await request.body()
    signature = request.headers.get("Stripe-Signature")
    
    stripe_api_key = os.environ.get("STRIPE_API_KEY")
    host_url = str(request.base_url)
    webhook_url = f"{host_url}api/webhook/stripe"
    
    stripe_checkout = StripeCheckout(api_key=stripe_api_key, webhook_url=webhook_url)
    
    try:
        webhook_response = await stripe_checkout.handle_webhook(body, signature)
        
        if webhook_response.payment_status == "paid":
            release_id = webhook_response.metadata.get("release_id")
            if release_id:
                await db.releases.update_one(
                    {"id": release_id},
                    {"$set": {"payment_status": "paid"}}
                )
                await db.payment_transactions.update_one(
                    {"session_id": webhook_response.session_id},
                    {"$set": {"payment_status": "paid", "paid_at": datetime.now(timezone.utc).isoformat()}}
                )
        
        return {"status": "success"}
    except Exception as e:
        logger.error(f"Webhook error: {e}")
        raise HTTPException(status_code=400, detail="Webhook processing failed")

# ============= WALLET ENDPOINTS =============
@api_router.get("/wallet", response_model=WalletResponse)
async def get_wallet(request: Request):
    user = await get_current_user(request)
    wallet = await db.wallets.find_one({"user_id": user["id"]}, {"_id": 0})
    if not wallet:
        wallet = {
            "balance": 0.0,
            "pending_balance": 0.0,
            "currency": "USD",
            "total_earnings": 0.0,
            "total_withdrawn": 0.0
        }
    return wallet

@api_router.post("/wallet/withdraw")
async def request_withdrawal(withdrawal: WithdrawalRequest, request: Request):
    user = await get_current_user(request)
    wallet = await db.wallets.find_one({"user_id": user["id"]})
    
    if not wallet or wallet["balance"] < withdrawal.amount:
        raise HTTPException(status_code=400, detail="Insufficient balance")
    
    if withdrawal.amount < 10:
        raise HTTPException(status_code=400, detail="Minimum withdrawal is $10")
    
    withdrawal_id = f"wd_{uuid.uuid4().hex[:12]}"
    await db.withdrawals.insert_one({
        "id": withdrawal_id,
        "user_id": user["id"],
        "amount": withdrawal.amount,
        "method": withdrawal.method,
        "paypal_email": withdrawal.paypal_email,
        "status": "pending",
        "created_at": datetime.now(timezone.utc).isoformat()
    })
    
    # Update wallet
    await db.wallets.update_one(
        {"user_id": user["id"]},
        {
            "$inc": {"balance": -withdrawal.amount, "pending_balance": withdrawal.amount}
        }
    )
    
    return {"message": "Withdrawal requested", "withdrawal_id": withdrawal_id}

@api_router.get("/wallet/withdrawals")
async def get_withdrawals(request: Request):
    user = await get_current_user(request)
    withdrawals = await db.withdrawals.find(
        {"user_id": user["id"]},
        {"_id": 0}
    ).sort("created_at", -1).to_list(50)
    return withdrawals

# ============= ANALYTICS ENDPOINTS =============
@api_router.get("/analytics/overview")
async def get_analytics_overview(request: Request):
    user = await get_current_user(request)
    
    # Get all releases for user
    releases = await db.releases.find({"artist_id": user["id"]}, {"_id": 0}).to_list(100)
    release_ids = [r["id"] for r in releases]
    
    # Aggregate royalties
    pipeline = [
        {"$match": {"release_id": {"$in": release_ids}}},
        {"$group": {
            "_id": None,
            "total_streams": {"$sum": "$streams"},
            "total_downloads": {"$sum": "$downloads"},
            "total_earnings": {"$sum": "$earnings"}
        }}
    ]
    
    result = await db.royalties.aggregate(pipeline).to_list(1)
    
    if result:
        totals = result[0]
    else:
        totals = {"total_streams": 0, "total_downloads": 0, "total_earnings": 0.0}
    
    # Get streams by store (simulated data for demo)
    streams_by_store = {
        "Spotify": int(totals.get("total_streams", 0) * 0.45),
        "Apple Music": int(totals.get("total_streams", 0) * 0.25),
        "YouTube Music": int(totals.get("total_streams", 0) * 0.15),
        "Amazon Music": int(totals.get("total_streams", 0) * 0.10),
        "Other": int(totals.get("total_streams", 0) * 0.05)
    }
    
    # Get streams by country (simulated)
    streams_by_country = {
        "US": int(totals.get("total_streams", 0) * 0.35),
        "UK": int(totals.get("total_streams", 0) * 0.15),
        "DE": int(totals.get("total_streams", 0) * 0.10),
        "CA": int(totals.get("total_streams", 0) * 0.08),
        "AU": int(totals.get("total_streams", 0) * 0.07),
        "Other": int(totals.get("total_streams", 0) * 0.25)
    }
    
    # Generate daily streams for last 30 days (simulated)
    daily_streams = []
    base_streams = totals.get("total_streams", 1000) // 30
    for i in range(30):
        date = datetime.now(timezone.utc) - timedelta(days=29-i)
        import random
        variation = random.uniform(0.7, 1.3)
        daily_streams.append({
            "date": date.strftime("%Y-%m-%d"),
            "streams": int(base_streams * variation),
            "earnings": round(base_streams * variation * 0.004, 2)
        })
    
    return {
        "total_streams": totals.get("total_streams", 0),
        "total_downloads": totals.get("total_downloads", 0),
        "total_earnings": round(totals.get("total_earnings", 0.0), 2),
        "streams_by_store": streams_by_store,
        "streams_by_country": streams_by_country,
        "daily_streams": daily_streams,
        "release_count": len(releases)
    }

@api_router.get("/analytics/release/{release_id}")
async def get_release_analytics(release_id: str, request: Request):
    user = await get_current_user(request)
    release = await db.releases.find_one({"id": release_id, "artist_id": user["id"]})
    if not release:
        raise HTTPException(status_code=404, detail="Release not found")
    
    # Get royalty data for this release
    royalties = await db.royalties.find({"release_id": release_id}, {"_id": 0}).to_list(100)
    
    total_streams = sum(r.get("streams", 0) for r in royalties)
    total_earnings = sum(r.get("earnings", 0) for r in royalties)
    
    return {
        "release_id": release_id,
        "title": release["title"],
        "total_streams": total_streams,
        "total_earnings": round(total_earnings, 2),
        "royalties": royalties
    }

# ============= AI ENDPOINTS =============
@api_router.post("/ai/metadata-suggestions")
async def get_ai_metadata_suggestions(req: AIMetadataRequest, request: Request):
    from emergentintegrations.llm.chat import LlmChat, UserMessage
    
    user = await get_current_user(request)
    
    chat = LlmChat(
        api_key=EMERGENT_KEY,
        session_id=f"metadata_{user['id']}_{uuid.uuid4().hex[:8]}",
        system_message="You are a music metadata expert. Suggest genres, moods, and tags for music releases based on the title and artist information. Return JSON format."
    ).with_model("openai", "gpt-5.2")
    
    prompt = f"""Analyze this music release and suggest metadata:
Title: {req.title}
Artist: {req.artist_name}
{f'Audio Features: {req.audio_features}' if req.audio_features else ''}

Return a JSON object with:
- primary_genre: string
- secondary_genres: array of strings (max 3)
- moods: array of strings (max 5)
- tags: array of strings (max 10)
- suggested_description: string (2-3 sentences)"""

    message = UserMessage(text=prompt)
    response = await chat.send_message(message)
    
    # Try to parse as JSON
    import json
    try:
        # Extract JSON from response
        json_str = response
        if "```json" in response:
            json_str = response.split("```json")[1].split("```")[0]
        elif "```" in response:
            json_str = response.split("```")[1].split("```")[0]
        suggestions = json.loads(json_str)
    except:
        suggestions = {"raw_response": response}
    
    return suggestions

@api_router.post("/ai/generate-description")
async def generate_ai_description(req: AIDescriptionRequest, request: Request):
    from emergentintegrations.llm.chat import LlmChat, UserMessage
    
    user = await get_current_user(request)
    
    chat = LlmChat(
        api_key=EMERGENT_KEY,
        session_id=f"desc_{user['id']}_{uuid.uuid4().hex[:8]}",
        system_message="You are a music marketing copywriter. Write compelling, professional release descriptions for music distribution platforms."
    ).with_model("openai", "gpt-5.2")
    
    prompt = f"""Write a compelling release description for music distribution:
Title: {req.title}
Artist: {req.artist_name}
Genre: {req.genre}
{f'Mood: {req.mood}' if req.mood else ''}

Write 2-3 engaging sentences that would appear on streaming platforms. Be professional and captivating."""

    message = UserMessage(text=prompt)
    description = await chat.send_message(message)
    
    return {"description": description.strip()}

@api_router.get("/ai/analytics-insights")
async def get_ai_analytics_insights(request: Request):
    from emergentintegrations.llm.chat import LlmChat, UserMessage
    
    user = await get_current_user(request)
    
    # Get user's analytics data
    releases = await db.releases.find({"artist_id": user["id"]}, {"_id": 0}).to_list(100)
    wallet = await db.wallets.find_one({"user_id": user["id"]}, {"_id": 0})
    
    chat = LlmChat(
        api_key=EMERGENT_KEY,
        session_id=f"insights_{user['id']}_{uuid.uuid4().hex[:8]}",
        system_message="You are a music industry analyst. Provide actionable insights and recommendations based on streaming data."
    ).with_model("openai", "gpt-5.2")
    
    prompt = f"""Analyze this artist's performance and provide insights:
- Total releases: {len(releases)}
- Total earnings: ${wallet.get('total_earnings', 0) if wallet else 0:.2f}
- Current balance: ${wallet.get('balance', 0) if wallet else 0:.2f}

Provide 3-5 actionable insights and recommendations for growing their music career."""

    message = UserMessage(text=prompt)
    insights = await chat.send_message(message)
    
    return {"insights": insights.strip()}

# ============= SUBSCRIPTION ENDPOINTS =============
SUBSCRIPTION_PLANS = {
    "free": {"name": "Free", "price": 0, "revenue_share": 15, "features": ["Basic distribution", "Standard analytics"]},
    "rise": {"name": "Rise", "price": 9.99, "revenue_share": 0, "features": ["All platforms", "Keep 100% royalties", "Priority support"]},
    "pro": {"name": "Pro", "price": 19.99, "revenue_share": 0, "features": ["All Rise features", "YouTube Content ID", "Spotify Canvas", "Advanced analytics"]}
}

@api_router.get("/subscriptions/plans")
async def get_subscription_plans():
    return SUBSCRIPTION_PLANS

@api_router.post("/subscriptions/upgrade")
async def upgrade_subscription(plan: str, request: Request):
    user = await get_current_user(request)
    
    if plan not in SUBSCRIPTION_PLANS:
        raise HTTPException(status_code=400, detail="Invalid plan")
    
    await db.users.update_one(
        {"id": user["id"]},
        {"$set": {"plan": plan}}
    )
    
    return {"message": f"Upgraded to {SUBSCRIPTION_PLANS[plan]['name']} plan"}

# ============= NOTIFICATIONS ENDPOINTS =============
@api_router.get("/notifications")
async def get_notifications(request: Request):
    user = await get_current_user(request)
    notifications = await db.notifications.find(
        {"user_id": user["id"]},
        {"_id": 0}
    ).sort("created_at", -1).to_list(50)
    return notifications

@api_router.put("/notifications/{notification_id}/read")
async def mark_notification_read(notification_id: str, request: Request):
    user = await get_current_user(request)
    await db.notifications.update_one(
        {"id": notification_id, "user_id": user["id"]},
        {"$set": {"read": True}}
    )
    return {"message": "Marked as read"}

# ============= ADMIN ENDPOINTS =============
@api_router.get("/admin/dashboard")
async def admin_dashboard(request: Request):
    admin = await require_admin(request)
    
    total_users = await db.users.count_documents({})
    total_releases = await db.releases.count_documents({})
    total_tracks = await db.tracks.count_documents({})
    pending_submissions = await db.submissions.count_documents({"status": "pending_review"})
    approved_submissions = await db.submissions.count_documents({"status": "approved"})
    rejected_submissions = await db.submissions.count_documents({"status": "rejected"})
    
    # Revenue stats
    pipeline = [{"$group": {"_id": None, "total": {"$sum": "$amount"}}}]
    revenue_result = await db.payment_transactions.aggregate(pipeline).to_list(1)
    total_revenue = revenue_result[0]["total"] if revenue_result else 0
    
    # Users by plan
    plan_pipeline = [{"$group": {"_id": "$plan", "count": {"$sum": 1}}}]
    plan_result = await db.users.aggregate(plan_pipeline).to_list(10)
    users_by_plan = {r["_id"]: r["count"] for r in plan_result}
    
    # Recent activity (last 7 days)
    week_ago = (datetime.now(timezone.utc) - timedelta(days=7)).isoformat()
    new_users_week = await db.users.count_documents({"created_at": {"$gte": week_ago}})
    new_releases_week = await db.releases.count_documents({"created_at": {"$gte": week_ago}})
    
    return {
        "total_users": total_users,
        "total_releases": total_releases,
        "total_tracks": total_tracks,
        "pending_submissions": pending_submissions,
        "approved_submissions": approved_submissions,
        "rejected_submissions": rejected_submissions,
        "total_revenue": round(total_revenue, 2),
        "users_by_plan": users_by_plan,
        "new_users_week": new_users_week,
        "new_releases_week": new_releases_week
    }

@api_router.get("/admin/submissions")
async def get_submissions(request: Request, status: Optional[str] = None, page: int = 1, limit: int = 20):
    admin = await require_admin(request)
    
    query = {}
    if status:
        query["status"] = status
    
    skip = (page - 1) * limit
    total = await db.submissions.count_documents(query)
    submissions = await db.submissions.find(query, {"_id": 0}).sort("submitted_at", -1).skip(skip).limit(limit).to_list(limit)
    
    return {"submissions": submissions, "total": total, "page": page, "pages": (total + limit - 1) // limit}

@api_router.get("/admin/submissions/{release_id}")
async def get_submission_detail(release_id: str, request: Request):
    admin = await require_admin(request)
    
    submission = await db.submissions.find_one({"release_id": release_id}, {"_id": 0})
    if not submission:
        raise HTTPException(status_code=404, detail="Submission not found")
    
    release = await db.releases.find_one({"id": release_id}, {"_id": 0})
    tracks = await db.tracks.find({"release_id": release_id}, {"_id": 0}).sort("track_number", 1).to_list(50)
    artist = await db.users.find_one({"id": submission["artist_id"]}, {"_id": 0, "password_hash": 0})
    
    return {
        "submission": submission,
        "release": release,
        "tracks": tracks,
        "artist": artist
    }

@api_router.put("/admin/submissions/{release_id}/review")
async def review_submission(release_id: str, review: AdminReviewAction, request: Request):
    admin = await require_admin(request)
    
    submission = await db.submissions.find_one({"release_id": release_id})
    if not submission:
        raise HTTPException(status_code=404, detail="Submission not found")
    
    if submission["status"] != "pending_review":
        raise HTTPException(status_code=400, detail="Submission already reviewed")
    
    new_status = "approved" if review.action == "approve" else "rejected"
    now = datetime.now(timezone.utc).isoformat()
    
    # Update submission
    await db.submissions.update_one(
        {"release_id": release_id},
        {"$set": {
            "status": new_status,
            "reviewed_at": now,
            "reviewed_by": admin["id"],
            "review_notes": review.notes
        }}
    )
    
    if review.action == "approve":
        # Update release status to distributed
        await db.releases.update_one(
            {"id": release_id},
            {"$set": {"status": "distributed"}}
        )
        # Update distribution records
        await db.distributions.update_many(
            {"release_id": release_id},
            {"$set": {"status": "live", "approved_at": now}}
        )
        notify_msg = f"Your release has been approved and is now live on all selected stores!"
    else:
        # Update release status to rejected
        await db.releases.update_one(
            {"id": release_id},
            {"$set": {"status": "rejected", "rejection_reason": review.notes}}
        )
        await db.distributions.update_many(
            {"release_id": release_id},
            {"$set": {"status": "rejected"}}
        )
        notify_msg = f"Your release was not approved. Reason: {review.notes or 'Does not meet guidelines.'}"
    
    # Notify artist
    await db.notifications.insert_one({
        "id": f"notif_{uuid.uuid4().hex[:12]}",
        "user_id": submission["artist_id"],
        "type": "review_result",
        "message": notify_msg,
        "release_id": release_id,
        "read": False,
        "created_at": now
    })
    
    # Audit log
    await db.admin_actions.insert_one({
        "id": f"act_{uuid.uuid4().hex[:12]}",
        "admin_id": admin["id"],
        "action": f"review_{review.action}",
        "target_type": "release",
        "target_id": release_id,
        "notes": review.notes,
        "created_at": now
    })
    
    return {"message": f"Submission {new_status}", "status": new_status}

@api_router.get("/admin/users")
async def admin_get_users(request: Request, page: int = 1, limit: int = 20, search: Optional[str] = None):
    admin = await require_admin(request)
    
    query = {}
    if search:
        query["$or"] = [
            {"name": {"$regex": search, "$options": "i"}},
            {"email": {"$regex": search, "$options": "i"}},
            {"artist_name": {"$regex": search, "$options": "i"}}
        ]
    
    skip = (page - 1) * limit
    total = await db.users.count_documents(query)
    users = await db.users.find(query, {"_id": 0, "password_hash": 0}).sort("created_at", -1).skip(skip).limit(limit).to_list(limit)
    
    # Enrich with release count
    for user in users:
        user["release_count"] = await db.releases.count_documents({"artist_id": user["id"]})
    
    return {"users": users, "total": total, "page": page, "pages": (total + limit - 1) // limit}

@api_router.put("/admin/users/{user_id}")
async def admin_update_user(user_id: str, update: AdminUserUpdate, request: Request):
    admin = await require_admin(request)
    
    user = await db.users.find_one({"id": user_id})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    update_doc = {}
    if update.role:
        update_doc["role"] = update.role
    if update.plan:
        update_doc["plan"] = update.plan
    if update.status:
        update_doc["status"] = update.status
    
    if update_doc:
        update_doc["updated_at"] = datetime.now(timezone.utc).isoformat()
        await db.users.update_one({"id": user_id}, {"$set": update_doc})
    
    # Audit log
    await db.admin_actions.insert_one({
        "id": f"act_{uuid.uuid4().hex[:12]}",
        "admin_id": admin["id"],
        "action": "update_user",
        "target_type": "user",
        "target_id": user_id,
        "notes": str(update_doc),
        "created_at": datetime.now(timezone.utc).isoformat()
    })
    
    return {"message": "User updated"}

# ============= SPLIT PAYMENT ENDPOINTS =============
@api_router.post("/splits")
async def create_split(split: SplitCreate, request: Request):
    user = await get_current_user(request)
    
    # Verify track belongs to user
    track = await db.tracks.find_one({"id": split.track_id, "artist_id": user["id"]})
    if not track:
        raise HTTPException(status_code=404, detail="Track not found")
    
    # Validate percentages sum to <= 100
    total_pct = sum(c.percentage for c in split.collaborators)
    if total_pct > 100:
        raise HTTPException(status_code=400, detail="Total split percentages cannot exceed 100%")
    if total_pct < 0:
        raise HTTPException(status_code=400, detail="Percentages must be positive")
    
    # Owner gets the remainder
    owner_percentage = 100.0 - total_pct
    
    split_id = f"split_{uuid.uuid4().hex[:12]}"
    split_doc = {
        "id": split_id,
        "track_id": split.track_id,
        "release_id": track["release_id"],
        "owner_id": user["id"],
        "owner_name": user.get("artist_name", user["name"]),
        "owner_percentage": owner_percentage,
        "collaborators": [c.model_dump() for c in split.collaborators],
        "status": "active",
        "created_at": datetime.now(timezone.utc).isoformat()
    }
    
    # Upsert — one split agreement per track
    await db.splits.update_one(
        {"track_id": split.track_id},
        {"$set": split_doc},
        upsert=True
    )
    
    return {"message": "Split agreement created", "split_id": split_id, "owner_percentage": owner_percentage}

@api_router.get("/splits/{track_id}")
async def get_split(track_id: str, request: Request):
    user = await get_current_user(request)
    
    split = await db.splits.find_one({"track_id": track_id}, {"_id": 0})
    if not split:
        return {"track_id": track_id, "collaborators": [], "owner_percentage": 100.0}
    
    return split

@api_router.put("/splits/{track_id}")
async def update_split(track_id: str, update: SplitUpdate, request: Request):
    user = await get_current_user(request)
    
    track = await db.tracks.find_one({"id": track_id, "artist_id": user["id"]})
    if not track:
        raise HTTPException(status_code=404, detail="Track not found")
    
    total_pct = sum(c.percentage for c in update.collaborators)
    if total_pct > 100:
        raise HTTPException(status_code=400, detail="Total split percentages cannot exceed 100%")
    
    owner_percentage = 100.0 - total_pct
    
    await db.splits.update_one(
        {"track_id": track_id},
        {"$set": {
            "collaborators": [c.model_dump() for c in update.collaborators],
            "owner_percentage": owner_percentage,
            "updated_at": datetime.now(timezone.utc).isoformat()
        }}
    )
    
    return {"message": "Split updated", "owner_percentage": owner_percentage}

@api_router.delete("/splits/{track_id}")
async def delete_split(track_id: str, request: Request):
    user = await get_current_user(request)
    
    track = await db.tracks.find_one({"id": track_id, "artist_id": user["id"]})
    if not track:
        raise HTTPException(status_code=404, detail="Track not found")
    
    await db.splits.delete_one({"track_id": track_id})
    return {"message": "Split agreement removed"}

# ============= FILE SERVING =============
@api_router.get("/files/{path:path}")
async def serve_file(path: str, request: Request, auth: Optional[str] = Query(None)):
    # Verify auth (from cookie or query param)
    token = request.cookies.get("access_token") or auth
    if not token:
        auth_header = request.headers.get("Authorization", "")
        if auth_header.startswith("Bearer "):
            token = auth_header[7:]
    
    if not token:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    try:
        data, content_type = get_object(path)
        return Response(content=data, media_type=content_type)
    except Exception as e:
        logger.error(f"File serve error: {e}")
        raise HTTPException(status_code=404, detail="File not found")

# ============= HEALTH CHECK =============
@api_router.get("/health")
async def health_check():
    return {"status": "healthy", "timestamp": datetime.now(timezone.utc).isoformat()}

# Include router
app.include_router(api_router)

# CORS middleware - specific origins for cookie-based auth
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://tunedrop-gateway.preview.emergentagent.com",
        "http://localhost:3000",
        os.environ.get("FRONTEND_URL", "http://localhost:3000")
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"],
)

# Startup events
@app.on_event("startup")
async def startup():
    # Create indexes
    await db.users.create_index("email", unique=True)
    await db.users.create_index("id", unique=True)
    await db.releases.create_index("artist_id")
    await db.releases.create_index("id", unique=True)
    await db.tracks.create_index("release_id")
    await db.tracks.create_index("id", unique=True)
    await db.distributions.create_index([("release_id", 1), ("store_id", 1)])
    await db.royalties.create_index("release_id")
    await db.wallets.create_index("user_id", unique=True)
    await db.submissions.create_index("release_id", unique=True)
    await db.submissions.create_index("status")
    await db.splits.create_index("track_id", unique=True)
    await db.admin_actions.create_index("admin_id")
    
    # Initialize storage
    try:
        init_storage()
        logger.info("Object storage initialized")
    except Exception as e:
        logger.error(f"Storage init failed: {e}")
    
    # Seed admin user
    admin_email = os.environ.get("ADMIN_EMAIL", "admin@tunedrop.com")
    admin_password = os.environ.get("ADMIN_PASSWORD", "Admin123!")
    existing = await db.users.find_one({"email": admin_email})
    if not existing:
        admin_id = f"user_{uuid.uuid4().hex[:12]}"
        await db.users.insert_one({
            "id": admin_id,
            "email": admin_email,
            "name": "Admin",
            "artist_name": "TuneDrop Admin",
            "password_hash": hash_password(admin_password),
            "role": "admin",
            "plan": "pro",
            "avatar_url": None,
            "created_at": datetime.now(timezone.utc).isoformat()
        })
        await db.wallets.insert_one({
            "user_id": admin_id,
            "balance": 0.0,
            "pending_balance": 0.0,
            "currency": "USD",
            "total_earnings": 0.0,
            "total_withdrawn": 0.0,
            "created_at": datetime.now(timezone.utc).isoformat()
        })
        logger.info(f"Admin user created: {admin_email}")
    
    # Write test credentials
    from pathlib import Path
    Path("/app/memory").mkdir(exist_ok=True)
    with open("/app/memory/test_credentials.md", "w") as f:
        f.write(f"""# Test Credentials

## Admin User
- Email: {admin_email}
- Password: {admin_password}
- Role: admin

## Auth Endpoints
- POST /api/auth/register
- POST /api/auth/login
- GET /api/auth/me
- POST /api/auth/logout
- POST /api/auth/refresh
- POST /api/auth/session (Google OAuth)
""")

@app.on_event("shutdown")
async def shutdown():
    client.close()
