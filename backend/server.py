"""
TuneDrop / Kalmori - Music Distribution Platform
Modularized server entry point.
"""
from dotenv import load_dotenv
load_dotenv()

from fastapi import FastAPI, APIRouter, HTTPException, Request, Response, File, UploadFile, Query
from fastapi.responses import StreamingResponse
from starlette.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime, timezone, timedelta
import io
import csv
from io import BytesIO
import os
import logging
import uuid
import random

# Import shared core (db, models, helpers)
from core import (
    db, client, logger, APP_NAME, EMERGENT_KEY,
    # Models
    UserCreate, UserLogin, UserResponse, ArtistProfile,
    ReleaseCreate, ReleaseResponse, TrackCreate, TrackResponse,
    DistributionStore, WalletResponse, WithdrawalRequest, PaymentCheckout,
    AnalyticsResponse, AIMetadataRequest, AIDescriptionRequest,
    Collaborator, SplitCreate, SplitUpdate,
    AdminReviewAction, AdminUserUpdate,
    # Helpers
    hash_password, verify_password, create_access_token, create_refresh_token,
    generate_upc, generate_isrc, get_current_user, require_admin,
    init_storage, put_object, get_object, get_jwt_secret, JWT_ALGORITHM,
)
import jwt
import requests
import secrets

# Create the main app
app = FastAPI(title="TuneDrop Music Distribution API")

# Create router with /api prefix
api_router = APIRouter(prefix="/api")

# ============= AUTH ENDPOINTS =============
@api_router.post("/auth/register")
async def register(user_data: UserCreate, response: Response):
    # Verify reCAPTCHA if token provided
    recaptcha_secret = os.environ.get("RECAPTCHA_SECRET_KEY")
    if recaptcha_secret and user_data.recaptcha_token:
        try:
            recap_resp = requests.post("https://www.google.com/recaptcha/api/siteverify",
                data={"secret": recaptcha_secret, "response": user_data.recaptcha_token}, timeout=10)
            recap_data = recap_resp.json()
            if not recap_data.get("success"):
                raise HTTPException(status_code=400, detail="reCAPTCHA verification failed")
        except requests.RequestException:
            pass  # Allow registration if reCAPTCHA service is down

    email = user_data.email.lower()
    existing = await db.users.find_one({"email": email})
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")
    user_id = f"user_{uuid.uuid4().hex[:12]}"
    user_doc = {
        "id": user_id, "email": email,
        "name": user_data.name or user_data.artist_name or email.split("@")[0],
        "artist_name": user_data.artist_name or user_data.name or email.split("@")[0],
        "password_hash": hash_password(user_data.password),
        "role": "artist", "user_role": user_data.user_role or "artist", "plan": "free",
        "avatar_url": None, "legal_name": user_data.legal_name or "",
        "country": user_data.country or "", "state": user_data.state or "",
        "town": user_data.town or "", "post_code": user_data.post_code or "",
        "phone_number": user_data.phone_number or "",
        "email_verified": False,
        "created_at": datetime.now(timezone.utc).isoformat()
    }
    await db.users.insert_one(user_doc)
    await db.wallets.insert_one({
        "user_id": user_id, "balance": 0.0, "pending_balance": 0.0,
        "currency": "USD", "total_earnings": 0.0, "total_withdrawn": 0.0,
        "created_at": datetime.now(timezone.utc).isoformat()
    })
    access_token = create_access_token(user_id, email)
    refresh_token = create_refresh_token(user_id)
    response.set_cookie(key="access_token", value=access_token, httponly=True, secure=True, samesite="none", max_age=3600, path="/")
    response.set_cookie(key="refresh_token", value=refresh_token, httponly=True, secure=True, samesite="none", max_age=604800, path="/")
    user_doc.pop("password_hash", None)
    user_doc.pop("_id", None)
    # Send welcome email + verification + admin notification
    try:
        from routes.email_routes import send_welcome_email, send_verification_email, send_admin_signup_notification
        import asyncio
        import secrets as _secrets
        # Welcome email
        asyncio.ensure_future(send_welcome_email(email, user_doc.get("name", "Artist"), user_data.user_role or "artist"))
        # Verification email
        verify_token = _secrets.token_urlsafe(32)
        await db.email_verifications.insert_one({
            "id": str(uuid.uuid4()), "user_id": user_id, "email": email,
            "token": verify_token, "expires_at": datetime.now(timezone.utc) + timedelta(hours=24),
            "used": False, "created_at": datetime.now(timezone.utc),
        })
        asyncio.ensure_future(send_verification_email(email, user_doc.get("name", "Artist"), verify_token))
        # Admin notification
        asyncio.ensure_future(send_admin_signup_notification(user_doc.get("name", "Artist"), email, user_data.user_role or "artist"))
    except Exception as e:
        logger.warning(f"Sign-up email failed: {e}")
    return {"access_token": access_token, "refresh_token": refresh_token, "user": user_doc}

class SetRoleInput(BaseModel):
    role: str

@api_router.put("/auth/set-role")
async def set_user_role(data: SetRoleInput, request: Request):
    """Set user role after registration (artist, producer, or label)"""
    user = await get_current_user(request)
    valid_roles = ["artist", "producer", "label", "label_producer"]
    if data.role not in valid_roles:
        raise HTTPException(status_code=400, detail=f"Role must be one of: {', '.join(valid_roles)}")
    await db.users.update_one({"id": user["id"]}, {"$set": {"user_role": data.role, "role": data.role if data.role == "admin" else user.get("role", "artist")}})
    # Update artist_profiles with role
    await db.artist_profiles.update_one(
        {"user_id": user["id"]},
        {"$set": {"user_role": data.role, "updated_at": datetime.now(timezone.utc).isoformat()}},
        upsert=True
    )
    return {"message": "Role updated", "role": data.role}

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
    return {"access_token": access_token, "refresh_token": refresh_token, "user": user}

@api_router.get("/auth/me")
async def get_me(request: Request):
    return await get_current_user(request)

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

@api_router.post("/auth/session")
async def process_google_session(request: Request, response: Response):
    body = await request.json()
    session_id = body.get("session_id")
    if not session_id:
        raise HTTPException(status_code=400, detail="Session ID required")
    try:
        resp = requests.get("https://demobackend.emergentagent.com/auth/v1/env/oauth/session-data",
            headers={"X-Session-ID": session_id}, timeout=10)
        resp.raise_for_status()
        session_data = resp.json()
        email = session_data["email"].lower()
        user = await db.users.find_one({"email": email}, {"_id": 0})
        if not user:
            user_id = f"user_{uuid.uuid4().hex[:12]}"
            user = {
                "id": user_id, "email": email, "name": session_data["name"],
                "artist_name": session_data["name"], "password_hash": "",
                "role": "artist", "plan": "free",
                "avatar_url": session_data.get("picture"), "auth_provider": "google",
                "created_at": datetime.now(timezone.utc).isoformat()
            }
            await db.users.insert_one(user)
            await db.wallets.insert_one({
                "user_id": user_id, "balance": 0.0, "pending_balance": 0.0,
                "currency": "USD", "total_earnings": 0.0, "total_withdrawn": 0.0,
                "created_at": datetime.now(timezone.utc).isoformat()
            })
        access_token = create_access_token(user["id"], email)
        refresh_token_val = create_refresh_token(user["id"])
        response.set_cookie(key="access_token", value=access_token, httponly=True, secure=True, samesite="none", max_age=3600, path="/")
        response.set_cookie(key="refresh_token", value=refresh_token_val, httponly=True, secure=True, samesite="none", max_age=604800, path="/")
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
        return {"user_id": user["id"], "artist_name": user.get("artist_name", user["name"]),
                "bio": None, "genre": None, "country": None, "website": None,
                "spotify_url": None, "apple_music_url": None, "instagram": None, "twitter": None}
    return profile

@api_router.put("/artists/profile")
async def update_artist_profile(profile: ArtistProfile, request: Request):
    user = await get_current_user(request)
    profile_doc = profile.model_dump()
    profile_doc["user_id"] = user["id"]
    profile_doc["updated_at"] = datetime.now(timezone.utc).isoformat()
    await db.artist_profiles.update_one({"user_id": user["id"]}, {"$set": profile_doc}, upsert=True)
    await db.users.update_one({"id": user["id"]}, {"$set": {"artist_name": profile.artist_name}})
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
    await db.users.update_one({"id": user["id"]}, {"$set": {"avatar_url": result["path"]}})
    return {"avatar_url": result["path"]}

# ============= RELEASE ENDPOINTS =============
@api_router.post("/releases", response_model=ReleaseResponse)
async def create_release(release: ReleaseCreate, request: Request):
    user = await get_current_user(request)
    release_id = f"rel_{uuid.uuid4().hex[:12]}"
    release_doc = {"id": release_id, "upc": generate_upc(), "artist_id": user["id"],
        "artist_name": user.get("artist_name", user["name"]), **release.model_dump(),
        "cover_art_url": None, "status": "draft", "track_count": 0,
        "payment_status": "pending", "created_at": datetime.now(timezone.utc).isoformat()}
    await db.releases.insert_one(release_doc)
    release_doc.pop("_id", None)
    return release_doc

@api_router.get("/releases")
async def get_releases(request: Request, status: Optional[str] = None):
    user = await get_current_user(request)
    query = {"artist_id": user["id"]}
    if status: query["status"] = status
    return await db.releases.find(query, {"_id": 0}).sort("created_at", -1).to_list(100)

@api_router.get("/releases/{release_id}")
async def get_release(release_id: str, request: Request):
    user = await get_current_user(request)
    release = await db.releases.find_one({"id": release_id, "artist_id": user["id"]}, {"_id": 0})
    if not release: raise HTTPException(status_code=404, detail="Release not found")
    release["tracks"] = await db.tracks.find({"release_id": release_id}, {"_id": 0}).sort("track_number", 1).to_list(50)
    return release

@api_router.post("/releases/{release_id}/cover")
async def upload_cover_art(release_id: str, request: Request, file: UploadFile = File(...)):
    user = await get_current_user(request)
    release = await db.releases.find_one({"id": release_id, "artist_id": user["id"]})
    if not release: raise HTTPException(status_code=404, detail="Release not found")
    if not file.content_type.startswith("image/"): raise HTTPException(status_code=400, detail="File must be an image")
    ext = file.filename.split(".")[-1] if "." in file.filename else "jpg"
    path = f"{APP_NAME}/covers/{user['id']}/{release_id}/{uuid.uuid4()}.{ext}"
    result = put_object(path, await file.read(), file.content_type)
    await db.releases.update_one({"id": release_id}, {"$set": {"cover_art_url": result["path"]}})
    return {"cover_art_url": result["path"]}

@api_router.put("/releases/{release_id}")
async def update_release(release_id: str, release: ReleaseCreate, request: Request):
    user = await get_current_user(request)
    existing = await db.releases.find_one({"id": release_id, "artist_id": user["id"]})
    if not existing: raise HTTPException(status_code=404, detail="Release not found")
    await db.releases.update_one({"id": release_id}, {"$set": {**release.model_dump(), "updated_at": datetime.now(timezone.utc).isoformat()}})
    return {"message": "Release updated"}

@api_router.delete("/releases/{release_id}")
async def delete_release(release_id: str, request: Request):
    user = await get_current_user(request)
    result = await db.releases.delete_one({"id": release_id, "artist_id": user["id"], "status": "draft"})
    if result.deleted_count == 0: raise HTTPException(status_code=404, detail="Release not found or cannot be deleted")
    await db.tracks.delete_many({"release_id": release_id})
    return {"message": "Release deleted"}

# ============= TRACK ENDPOINTS =============
@api_router.post("/tracks", response_model=TrackResponse)
async def create_track(track: TrackCreate, request: Request):
    user = await get_current_user(request)
    release = await db.releases.find_one({"id": track.release_id, "artist_id": user["id"]})
    if not release: raise HTTPException(status_code=404, detail="Release not found")
    track_id = f"trk_{uuid.uuid4().hex[:12]}"
    track_doc = {"id": track_id, "artist_id": user["id"],
        **track.model_dump(), "audio_url": None, "status": "pending",
        "created_at": datetime.now(timezone.utc).isoformat()}
    if not track_doc.get("isrc"):
        track_doc["isrc"] = generate_isrc()
    await db.tracks.insert_one(track_doc)
    await db.releases.update_one({"id": track.release_id}, {"$inc": {"track_count": 1}})
    track_doc.pop("_id", None)
    return track_doc

@api_router.post("/tracks/{track_id}/audio")
async def upload_audio(track_id: str, request: Request, file: UploadFile = File(...)):
    user = await get_current_user(request)
    track = await db.tracks.find_one({"id": track_id, "artist_id": user["id"]})
    if not track: raise HTTPException(status_code=404, detail="Track not found")
    allowed = ["audio/wav", "audio/mpeg", "audio/mp3", "audio/x-wav", "audio/flac"]
    if file.content_type not in allowed: raise HTTPException(status_code=400, detail="File must be WAV, MP3, or FLAC")
    ext = file.filename.split(".")[-1] if "." in file.filename else "wav"
    path = f"{APP_NAME}/audio/{user['id']}/{track['release_id']}/{track_id}.{ext}"
    data = await file.read()
    result = put_object(path, data, file.content_type)
    duration = len(data) // (44100 * 2 * 2)
    await db.tracks.update_one({"id": track_id}, {"$set": {"audio_url": result["path"], "duration": duration, "status": "ready"}})
    return {"audio_url": result["path"], "duration": duration}

@api_router.get("/tracks/{track_id}/stream")
async def stream_audio(track_id: str, request: Request):
    await get_current_user(request)
    track = await db.tracks.find_one({"id": track_id}, {"_id": 0})
    if not track or not track.get("audio_url"): raise HTTPException(status_code=404, detail="Track or audio not found")
    data, content_type = get_object(track["audio_url"])
    return StreamingResponse(BytesIO(data), media_type=content_type,
        headers={"Content-Disposition": f"inline; filename={track['title']}.{track['audio_url'].split('.')[-1]}"})

@api_router.delete("/tracks/{track_id}")
async def delete_track(track_id: str, request: Request):
    user = await get_current_user(request)
    track = await db.tracks.find_one({"id": track_id, "artist_id": user["id"]})
    if not track: raise HTTPException(status_code=404, detail="Track not found")
    await db.tracks.delete_one({"id": track_id})
    await db.releases.update_one({"id": track["release_id"]}, {"$inc": {"track_count": -1}})
    return {"message": "Track deleted"}

@api_router.put("/tracks/{track_id}")
async def update_track(track_id: str, request: Request):
    user = await get_current_user(request)
    track = await db.tracks.find_one({"id": track_id, "artist_id": user["id"]})
    if not track: raise HTTPException(status_code=404, detail="Track not found")
    body = await request.json()
    allowed_fields = {"title", "title_version", "explicit", "isrc", "dolby_atmos_isrc",
                      "iswc", "audio_language", "production", "publisher",
                      "preview_start", "preview_end", "main_artist", "track_number",
                      "lyrics", "composers", "producers"}
    updates = {k: v for k, v in body.items() if k in allowed_fields}
    if not updates:
        return {"message": "No valid fields to update"}
    await db.tracks.update_one({"id": track_id}, {"$set": updates})
    updated = await db.tracks.find_one({"id": track_id}, {"_id": 0})
    return updated

# ============= DISTRIBUTION =============
DSP_STORES = [
    # Major Global Platforms
    {"store_id": "spotify", "store_name": "Spotify", "icon": "spotify", "region": "Global"},
    {"store_id": "apple_music", "store_name": "Apple Music", "icon": "apple", "region": "Global"},
    {"store_id": "amazon_music", "store_name": "Amazon Music", "icon": "amazon", "region": "Global"},
    {"store_id": "youtube_music", "store_name": "YouTube Music", "icon": "youtube", "region": "Global"},
    {"store_id": "tidal", "store_name": "Tidal", "icon": "tidal", "region": "Global"},
    {"store_id": "deezer", "store_name": "Deezer", "icon": "deezer", "region": "Global"},
    {"store_id": "soundcloud", "store_name": "SoundCloud", "icon": "soundcloud", "region": "Global"},
    {"store_id": "pandora", "store_name": "Pandora", "icon": "pandora", "region": "North America"},
    {"store_id": "tiktok", "store_name": "TikTok / Resso", "icon": "tiktok", "region": "Global"},
    {"store_id": "instagram", "store_name": "Instagram / Facebook", "icon": "instagram", "region": "Global"},
    {"store_id": "shazam", "store_name": "Shazam", "icon": "shazam", "region": "Global"},
    {"store_id": "iheartradio", "store_name": "iHeartRadio", "icon": "radio", "region": "North America"},
    {"store_id": "napster", "store_name": "Napster", "icon": "napster", "region": "Global"},
    {"store_id": "audiomack", "store_name": "Audiomack", "icon": "audiomack", "region": "Global"},
    {"store_id": "tencent", "store_name": "Tencent Music (QQ Music)", "icon": "tencent", "region": "China"},
    # Africa & Middle East
    {"store_id": "boomplay", "store_name": "Boomplay", "icon": "boomplay", "region": "Africa"},
    {"store_id": "mdundo", "store_name": "Mdundo", "icon": "mdundo", "region": "Africa"},
    {"store_id": "anghami", "store_name": "Anghami", "icon": "anghami", "region": "Middle East"},
    {"store_id": "deezer_mena", "store_name": "Deezer MENA", "icon": "deezer", "region": "Middle East"},
    {"store_id": "mxit", "store_name": "Simfy Africa", "icon": "simfy", "region": "Africa"},
    {"store_id": "music_time", "store_name": "MusicTime!", "icon": "musictime", "region": "Africa"},
    {"store_id": "songa", "store_name": "Songa", "icon": "songa", "region": "Africa"},
    {"store_id": "afro_beats", "store_name": "Afrobeats.com", "icon": "afrobeats", "region": "Africa"},
    {"store_id": "uduX", "store_name": "uduX", "icon": "udux", "region": "Africa"},
    # India & South Asia
    {"store_id": "jiosaavn", "store_name": "JioSaavn", "icon": "jiosaavn", "region": "India"},
    {"store_id": "gaana", "store_name": "Gaana", "icon": "gaana", "region": "India"},
    {"store_id": "wynk", "store_name": "Wynk Music", "icon": "wynk", "region": "India"},
    {"store_id": "hungama", "store_name": "Hungama Music", "icon": "hungama", "region": "India"},
    {"store_id": "resso_india", "store_name": "Resso India", "icon": "resso", "region": "India"},
    # Asia Pacific
    {"store_id": "kkbox", "store_name": "KKBOX", "icon": "kkbox", "region": "Asia"},
    {"store_id": "line_music", "store_name": "LINE MUSIC", "icon": "line", "region": "Japan"},
    {"store_id": "awa", "store_name": "AWA", "icon": "awa", "region": "Japan"},
    {"store_id": "recochoku", "store_name": "Recochoku", "icon": "recochoku", "region": "Japan"},
    {"store_id": "mora", "store_name": "mora", "icon": "mora", "region": "Japan"},
    {"store_id": "melon", "store_name": "Melon", "icon": "melon", "region": "South Korea"},
    {"store_id": "genie", "store_name": "Genie Music", "icon": "genie", "region": "South Korea"},
    {"store_id": "bugs", "store_name": "Bugs!", "icon": "bugs", "region": "South Korea"},
    {"store_id": "vibe", "store_name": "VIBE (Naver)", "icon": "vibe", "region": "South Korea"},
    {"store_id": "flo", "store_name": "FLO", "icon": "flo", "region": "South Korea"},
    {"store_id": "joox", "store_name": "JOOX", "icon": "joox", "region": "Southeast Asia"},
    {"store_id": "kugou", "store_name": "KuGou Music", "icon": "kugou", "region": "China"},
    {"store_id": "kuwo", "store_name": "Kuwo Music", "icon": "kuwo", "region": "China"},
    {"store_id": "netease", "store_name": "NetEase Cloud Music", "icon": "netease", "region": "China"},
    {"store_id": "qobuz", "store_name": "Qobuz", "icon": "qobuz", "region": "Global"},
    # Russia & Eastern Europe
    {"store_id": "yandex", "store_name": "Yandex Music", "icon": "yandex", "region": "Russia"},
    {"store_id": "vk_music", "store_name": "VK Music", "icon": "vk", "region": "Russia"},
    {"store_id": "zvuk", "store_name": "Zvuk (Sber)", "icon": "zvuk", "region": "Russia"},
    # Latin America
    {"store_id": "claro_musica", "store_name": "Claro Musica", "icon": "claro", "region": "Latin America"},
    {"store_id": "tigo_music", "store_name": "Tigo Music", "icon": "tigo", "region": "Latin America"},
    {"store_id": "movistar", "store_name": "Movistar Musica", "icon": "movistar", "region": "Latin America"},
    # Download & DJ Stores
    {"store_id": "itunes", "store_name": "iTunes Store", "icon": "apple", "region": "Global"},
    {"store_id": "amazon_mp3", "store_name": "Amazon MP3 Store", "icon": "amazon", "region": "Global"},
    {"store_id": "beatport", "store_name": "Beatport", "icon": "beatport", "region": "Global"},
    {"store_id": "traxsource", "store_name": "Traxsource", "icon": "traxsource", "region": "Global"},
    {"store_id": "juno", "store_name": "Juno Download", "icon": "juno", "region": "Global"},
    {"store_id": "bleep", "store_name": "Bleep", "icon": "bleep", "region": "Global"},
    {"store_id": "bandcamp", "store_name": "Bandcamp", "icon": "bandcamp", "region": "Global"},
    # Social & Video
    {"store_id": "facebook", "store_name": "Facebook Music", "icon": "facebook", "region": "Global"},
    {"store_id": "snapchat", "store_name": "Snapchat Sounds", "icon": "snapchat", "region": "Global"},
    {"store_id": "triller", "store_name": "Triller", "icon": "triller", "region": "Global"},
    {"store_id": "peloton", "store_name": "Peloton", "icon": "peloton", "region": "Global"},
    {"store_id": "twitch", "store_name": "Twitch", "icon": "twitch", "region": "Global"},
    # Smart Speakers & Assistants
    {"store_id": "alexa", "store_name": "Amazon Alexa", "icon": "alexa", "region": "Global"},
    {"store_id": "google_assistant", "store_name": "Google Home / Nest", "icon": "google", "region": "Global"},
    {"store_id": "siri", "store_name": "Siri / HomePod", "icon": "apple", "region": "Global"},
    # Fitness & Wellness
    {"store_id": "fitness_radio", "store_name": "Fitness Radio", "icon": "fitness", "region": "Global"},
    {"store_id": "feed_fm", "store_name": "Feed.fm", "icon": "feedfm", "region": "Global"},
    {"store_id": "soundtrack_player", "store_name": "Soundtrack Player", "icon": "soundtrack", "region": "Global"},
    # Telecom Bundled Music
    {"store_id": "vodafone_music", "store_name": "Vodafone Music", "icon": "vodafone", "region": "Europe"},
    {"store_id": "orange_music", "store_name": "Orange Music", "icon": "orange", "region": "Europe"},
    {"store_id": "turkcell", "store_name": "Turkcell Muzik", "icon": "turkcell", "region": "Turkey"},
    {"store_id": "mtn_music", "store_name": "MTN Music+", "icon": "mtn", "region": "Africa"},
    {"store_id": "airtel_wynk", "store_name": "Airtel Wynk", "icon": "airtel", "region": "India"},
    {"store_id": "etisalat", "store_name": "Etisalat Music", "icon": "etisalat", "region": "Middle East"},
    {"store_id": "safaricom", "store_name": "Safaricom Skiza", "icon": "safaricom", "region": "Africa"},
    {"store_id": "digicel", "store_name": "Digicel Music", "icon": "digicel", "region": "Caribbean"},
    # Streaming Radio & Discovery
    {"store_id": "slacker_radio", "store_name": "LiveOne (Slacker)", "icon": "slacker", "region": "North America"},
    {"store_id": "tunein", "store_name": "TuneIn", "icon": "tunein", "region": "Global"},
    {"store_id": "radio_com", "store_name": "Audacy (Radio.com)", "icon": "audacy", "region": "North America"},
    {"store_id": "8tracks", "store_name": "8tracks", "icon": "8tracks", "region": "Global"},
    {"store_id": "mixcloud", "store_name": "Mixcloud", "icon": "mixcloud", "region": "Global"},
    # Hi-Fi & Audiophile
    {"store_id": "tidal_hifi", "store_name": "Tidal HiFi Plus", "icon": "tidal", "region": "Global"},
    {"store_id": "amazon_hd", "store_name": "Amazon Music HD", "icon": "amazon", "region": "Global"},
    {"store_id": "apple_lossless", "store_name": "Apple Digital Masters", "icon": "apple", "region": "Global"},
    {"store_id": "nugs", "store_name": "nugs.net", "icon": "nugs", "region": "Global"},
    {"store_id": "presto_music", "store_name": "Presto Music", "icon": "presto", "region": "Global"},
    # Licensing & Sync
    {"store_id": "epidemic", "store_name": "Epidemic Sound", "icon": "epidemic", "region": "Global"},
    {"store_id": "artlist", "store_name": "Artlist", "icon": "artlist", "region": "Global"},
    {"store_id": "musicbed", "store_name": "Musicbed", "icon": "musicbed", "region": "Global"},
    {"store_id": "songtradr", "store_name": "Songtradr", "icon": "songtradr", "region": "Global"},
    {"store_id": "pond5", "store_name": "Pond5", "icon": "pond5", "region": "Global"},
    {"store_id": "shutterstock", "store_name": "Shutterstock Music", "icon": "shutterstock", "region": "Global"},
    # Additional Global & Regional
    {"store_id": "medianet", "store_name": "MediaNet", "icon": "medianet", "region": "Global"},
    {"store_id": "gracenote", "store_name": "Gracenote", "icon": "gracenote", "region": "Global"},
    {"store_id": "saavn_global", "store_name": "Saavn Global", "icon": "saavn", "region": "Global"},
    {"store_id": "trebel", "store_name": "Trebel Music", "icon": "trebel", "region": "Latin America"},
    {"store_id": "spinrilla", "store_name": "Spinrilla", "icon": "spinrilla", "region": "North America"},
    {"store_id": "datpiff", "store_name": "DatPiff", "icon": "datpiff", "region": "North America"},
    {"store_id": "spotify_kids", "store_name": "Spotify Kids", "icon": "spotify", "region": "Global"},
    {"store_id": "youtube_kids", "store_name": "YouTube Kids", "icon": "youtube", "region": "Global"},
    {"store_id": "amazon_kids", "store_name": "Amazon Music Kids", "icon": "amazon", "region": "Global"},
    # Gaming & Metaverse
    {"store_id": "roblox", "store_name": "Roblox", "icon": "roblox", "region": "Global"},
    {"store_id": "fortnite", "store_name": "Fortnite", "icon": "fortnite", "region": "Global"},
    {"store_id": "beat_saber", "store_name": "Beat Saber (Meta)", "icon": "meta", "region": "Global"},
    # Additional stores
    {"store_id": "7digital", "store_name": "7digital", "icon": "7digital", "region": "Global"},
    {"store_id": "plex", "store_name": "Plex Amp", "icon": "plex", "region": "Global"},
    {"store_id": "youtube_shorts", "store_name": "YouTube Shorts", "icon": "youtube", "region": "Global"},
    {"store_id": "instagram_reels", "store_name": "Instagram Reels", "icon": "instagram", "region": "Global"},
    {"store_id": "capcut", "store_name": "CapCut", "icon": "capcut", "region": "Global"},
    {"store_id": "snap_spotlight", "store_name": "Snapchat Spotlight", "icon": "snapchat", "region": "Global"},
    {"store_id": "likee", "store_name": "Likee", "icon": "likee", "region": "Global"},
    {"store_id": "clap_music", "store_name": "Clap Music", "icon": "clap", "region": "Global"},
    {"store_id": "music_island", "store_name": "Music Island", "icon": "musicisland", "region": "Asia"},
    {"store_id": "xiami", "store_name": "Xiami Music", "icon": "xiami", "region": "China"},
    {"store_id": "muud", "store_name": "muud", "icon": "muud", "region": "Turkey"},
    {"store_id": "fizy", "store_name": "Fizy", "icon": "fizy", "region": "Turkey"},
    {"store_id": "sberzvuk", "store_name": "SberZvuk", "icon": "sber", "region": "Russia"},
    {"store_id": "mts_music", "store_name": "MTS Music", "icon": "mts", "region": "Russia"},
    {"store_id": "boom", "store_name": "Boom", "icon": "boom", "region": "Russia"},
    {"store_id": "melomaniac", "store_name": "Melomaniac", "icon": "melomaniac", "region": "Europe"},
    {"store_id": "idagio", "store_name": "IDAGIO", "icon": "idagio", "region": "Global"},
    {"store_id": "classicalarchives", "store_name": "Classical Archives", "icon": "classical", "region": "Global"},
    {"store_id": "primephonic", "store_name": "Primephonic (Apple)", "icon": "apple", "region": "Global"},
    {"store_id": "roxi", "store_name": "ROXi", "icon": "roxi", "region": "Europe"},
    {"store_id": "awa_global", "store_name": "AWA Global", "icon": "awa", "region": "Global"},
    {"store_id": "wink_music", "store_name": "Wink Music", "icon": "wink", "region": "Russia"},
    {"store_id": "naver_now", "store_name": "Naver NOW", "icon": "naver", "region": "South Korea"},
    {"store_id": "wavve", "store_name": "Wavve Music", "icon": "wavve", "region": "South Korea"},
    {"store_id": "langit", "store_name": "Langit Musik", "icon": "langit", "region": "Indonesia"},
    {"store_id": "noice", "store_name": "Noice", "icon": "noice", "region": "Indonesia"},
    {"store_id": "nct", "store_name": "NCT Music", "icon": "nct", "region": "Vietnam"},
    {"store_id": "nhaccuatui", "store_name": "NhacCuaTui", "icon": "nhaccuatui", "region": "Vietnam"},
    {"store_id": "zing_mp3", "store_name": "Zing MP3", "icon": "zing", "region": "Vietnam"},
    {"store_id": "lark_player", "store_name": "Lark Player", "icon": "lark", "region": "Global"},
    {"store_id": "musi", "store_name": "Musi", "icon": "musi", "region": "Global"},
    {"store_id": "tononkira", "store_name": "Tononkira", "icon": "tononkira", "region": "Africa"},
    {"store_id": "playme", "store_name": "PlayMe", "icon": "playme", "region": "Middle East"},
    {"store_id": "weyno", "store_name": "Weyno", "icon": "weyno", "region": "Africa"},
    {"store_id": "kuack", "store_name": "Kuack Media", "icon": "kuack", "region": "Latin America"},
    {"store_id": "music_pro", "store_name": "Music Pro", "icon": "musicpro", "region": "Global"},
    {"store_id": "claromusica_br", "store_name": "Claro Musica Brazil", "icon": "claro", "region": "Brazil"},
    {"store_id": "tim_music", "store_name": "TIM Music", "icon": "tim", "region": "Brazil"},
    {"store_id": "vivo_music", "store_name": "Vivo Musica", "icon": "vivo", "region": "Brazil"},
    {"store_id": "music_streaming", "store_name": "Music Streaming Pro", "icon": "streaming", "region": "Global"},
    {"store_id": "digital_stores", "store_name": "Digital Stores", "icon": "digital", "region": "Global"},
    {"store_id": "global_sound", "store_name": "Global Sound", "icon": "globe", "region": "Global"},
    {"store_id": "akazoo", "store_name": "Akazoo", "icon": "akazoo", "region": "Global"},
    {"store_id": "hits_daily", "store_name": "Hits Daily Double", "icon": "hits", "region": "North America"},
    {"store_id": "music_ally", "store_name": "Music Ally", "icon": "musically", "region": "Global"},
    {"store_id": "songkick", "store_name": "Songkick", "icon": "songkick", "region": "Global"},
]

@api_router.get("/distributions/stores")
async def get_distribution_stores():
    return DSP_STORES

@api_router.post("/distributions/submit/{release_id}")
async def submit_distribution(release_id: str, stores: List[str], request: Request):
    user = await get_current_user(request)
    release = await db.releases.find_one({"id": release_id, "artist_id": user["id"]}, {"_id": 0})
    if not release: raise HTTPException(status_code=404, detail="Release not found")
    if not release.get("cover_art_url"): raise HTTPException(status_code=400, detail="Release must have cover art")
    tracks = await db.tracks.find({"release_id": release_id, "audio_url": {"$ne": None}}).to_list(50)
    if not tracks: raise HTTPException(status_code=400, detail="Release must have at least one track with audio")
    if user.get("plan") != "free" and release.get("payment_status") != "paid":
        raise HTTPException(status_code=400, detail="Payment required before distribution")
    for store_id in stores:
        store = next((s for s in DSP_STORES if s["store_id"] == store_id), None)
        if store:
            await db.distributions.update_one({"release_id": release_id, "store_id": store_id},
                {"$set": {"release_id": release_id, "artist_id": user["id"], "store_id": store_id,
                    "store_name": store["store_name"], "status": "pending_review",
                    "submitted_at": datetime.now(timezone.utc).isoformat()}}, upsert=True)
    submission_id = f"sub_{uuid.uuid4().hex[:12]}"
    await db.submissions.update_one({"release_id": release_id},
        {"$set": {"id": submission_id, "release_id": release_id, "artist_id": user["id"],
            "artist_name": user.get("artist_name", user["name"]), "release_title": release["title"],
            "release_type": release["release_type"], "genre": release.get("genre", ""),
            "track_count": len(tracks), "stores": stores, "status": "pending_review",
            "submitted_at": datetime.now(timezone.utc).isoformat(),
            "reviewed_at": None, "reviewed_by": None, "review_notes": None}}, upsert=True)
    await db.releases.update_one({"id": release_id}, {"$set": {"status": "pending_review", "submitted_stores": stores}})
    # Notify ALL admins
    all_admins = await db.users.find({"role": "admin"}, {"_id": 0, "id": 1}).to_list(50)
    for admin_user in all_admins:
        await db.notifications.insert_one({"id": f"notif_{uuid.uuid4().hex[:12]}", "user_id": admin_user["id"],
            "type": "new_submission", "message": f"New submission: {release['title']} by {user.get('artist_name', user['name'])}",
            "release_id": release_id, "read": False, "action_url": "/admin/submissions", "created_at": datetime.now(timezone.utc).isoformat()})
    return {"message": f"Submitted for review to {len(stores)} stores", "stores": stores, "status": "pending_review"}

@api_router.get("/distributions/{release_id}")
async def get_distribution_status(release_id: str, request: Request):
    user = await get_current_user(request)
    return await db.distributions.find({"release_id": release_id, "artist_id": user["id"]}, {"_id": 0}).to_list(20)

# ============= PAYMENTS (Stripe) =============
RELEASE_PRICES = {"single": 20.00, "ep": 35.00, "album": 50.00}

@api_router.post("/payments/checkout")
async def create_checkout(checkout: PaymentCheckout, request: Request):
    from emergentintegrations.payments.stripe.checkout import StripeCheckout, CheckoutSessionRequest
    user = await get_current_user(request)
    release = await db.releases.find_one({"id": checkout.release_id, "artist_id": user["id"]})
    if not release: raise HTTPException(status_code=404, detail="Release not found")
    if user.get("plan") == "free":
        await db.releases.update_one({"id": checkout.release_id}, {"$set": {"payment_status": "free_tier"}})
        return {"message": "Free tier activated", "redirect_url": None}
    amount = RELEASE_PRICES.get(release["release_type"], 20.00)
    stripe_api_key = os.environ.get("STRIPE_API_KEY")
    host_url = str(request.base_url)
    stripe_checkout = StripeCheckout(api_key=stripe_api_key, webhook_url=f"{host_url}api/webhook/stripe")
    session = await stripe_checkout.create_checkout_session(CheckoutSessionRequest(
        amount=amount, currency="usd",
        success_url=f"{checkout.origin_url}/releases/{checkout.release_id}?payment=success&session_id={{CHECKOUT_SESSION_ID}}",
        cancel_url=f"{checkout.origin_url}/releases/{checkout.release_id}?payment=cancelled",
        metadata={"release_id": checkout.release_id, "user_id": user["id"], "release_type": release["release_type"]}))
    await db.payment_transactions.insert_one({"id": f"txn_{uuid.uuid4().hex[:12]}", "session_id": session.session_id,
        "user_id": user["id"], "release_id": checkout.release_id, "amount": amount, "currency": "usd",
        "payment_status": "pending", "provider": "stripe", "created_at": datetime.now(timezone.utc).isoformat()})
    return {"checkout_url": session.url, "session_id": session.session_id}

@api_router.get("/payments/status/{session_id}")
async def check_payment_status(session_id: str, request: Request):
    from emergentintegrations.payments.stripe.checkout import StripeCheckout
    stripe_api_key = os.environ.get("STRIPE_API_KEY")
    host_url = str(request.base_url)
    stripe_checkout = StripeCheckout(api_key=stripe_api_key, webhook_url=f"{host_url}api/webhook/stripe")
    status = await stripe_checkout.get_checkout_status(session_id)
    if status.payment_status == "paid":
        txn = await db.payment_transactions.find_one({"session_id": session_id})
        if txn and txn["payment_status"] != "paid":
            await db.payment_transactions.update_one({"session_id": session_id},
                {"$set": {"payment_status": "paid", "paid_at": datetime.now(timezone.utc).isoformat()}})
            await db.releases.update_one({"id": txn["release_id"]}, {"$set": {"payment_status": "paid"}})
    return {"status": status.status, "payment_status": status.payment_status,
        "amount": status.amount_total / 100, "currency": status.currency}

@api_router.post("/webhook/stripe")
async def stripe_webhook(request: Request):
    from emergentintegrations.payments.stripe.checkout import StripeCheckout
    body = await request.body()
    signature = request.headers.get("Stripe-Signature")
    stripe_api_key = os.environ.get("STRIPE_API_KEY")
    host_url = str(request.base_url)
    stripe_checkout = StripeCheckout(api_key=stripe_api_key, webhook_url=f"{host_url}api/webhook/stripe")
    try:
        webhook_response = await stripe_checkout.handle_webhook(body, signature)
        if webhook_response.payment_status == "paid":
            now = datetime.now(timezone.utc).isoformat()
            metadata = webhook_response.metadata or {}
            purchase_type = metadata.get("type")
            # Handle beat purchases
            if purchase_type == "beat_purchase":
                beat_id = metadata.get("beat_id")
                user_id = metadata.get("user_id")
                contract_id = metadata.get("contract_id")
                if beat_id and user_id:
                    await db.beat_purchases.update_one({"session_id": webhook_response.session_id},
                        {"$set": {"payment_status": "paid", "paid_at": now}})
                    # Update contract payment status
                    if contract_id:
                        await db.beat_contracts.update_one({"id": contract_id}, {"$set": {"payment_status": "paid", "paid_at": now}})
                    # Send receipt
                    purchase = await db.beat_purchases.find_one({"session_id": webhook_response.session_id}, {"_id": 0})
                    user = await db.users.find_one({"id": user_id}, {"_id": 0, "password_hash": 0})
                    if purchase and user:
                        receipt_id = f"rcpt_{uuid.uuid4().hex[:12]}"
                        try:
                            from routes.email_routes import send_beat_purchase_receipt
                            await send_beat_purchase_receipt(user["email"], user.get("name", "Artist"),
                                purchase.get("beat_title", "Beat"), purchase.get("license_type", "basic_lease"),
                                purchase.get("amount", 0), receipt_id)
                        except Exception as e:
                            logger.warning(f"Webhook receipt email failed: {e}")
                        # Email signed contract PDF to buyer
                        if contract_id:
                            try:
                                contract = await db.beat_contracts.find_one({"id": contract_id}, {"_id": 0})
                                if contract:
                                    from routes.email_routes import send_email
                                    contract["payment_status"] = "paid"
                                    pdf_bytes = _generate_contract_pdf(contract)
                                    import base64
                                    pdf_b64 = base64.b64encode(pdf_bytes).decode()
                                    await send_email(user["email"],
                                        f"Your Kalmori License Agreement - {contract.get('beat_title', 'Beat')}",
                                        f"""<div style="font-family:Helvetica,Arial,sans-serif;max-width:600px;margin:0 auto;background:#000;color:#fff;border-radius:16px;overflow:hidden;">
                                        <div style="background:linear-gradient(135deg,#7C4DFF,#E040FB);padding:30px;text-align:center;">
                                        <h1 style="color:white;margin:0 0 4px;font-size:11px;letter-spacing:5px;font-weight:800;text-transform:uppercase;opacity:0.85;">KALMORI</h1>
                                        <h2 style="color:white;margin:0;font-size:22px;">License Agreement Confirmed</h2>
                                        </div>
                                        <div style="padding:30px;">
                                        <p style="color:#ccc;font-size:15px;">Your {contract.get('license_name', 'license')} for <b>"{contract.get('beat_title', '')}"</b> has been confirmed.</p>
                                        <p style="color:#888;font-size:13px;">Contract ID: {contract_id}</p>
                                        <p style="color:#888;font-size:13px;">You can download your signed contract from your Purchases page.</p>
                                        <p style="color:#555;font-size:12px;margin-top:28px;padding-top:16px;border-top:1px solid #222;text-align:center;">Kalmori Digital Distribution</p>
                                        </div></div>""")
                            except Exception as e:
                                logger.warning(f"Contract email failed: {e}")
                        # Auto-create royalty split for this beat license
                        try:
                            license_type = metadata.get("license_type", "basic_lease")
                            default_splits = DEFAULT_SPLITS.get(license_type, {"producer": 50, "artist": 50})
                            beat = await db.beats.find_one({"id": beat_id}, {"_id": 0})
                            producer_id = beat.get("uploaded_by") or beat.get("user_id") or "admin"
                            # Find admin/producer user for the beat
                            admin_users = await db.users.find({"role": "admin"}, {"_id": 0, "id": 1}).to_list(1)
                            if producer_id == "admin" and admin_users:
                                producer_id = admin_users[0]["id"]
                            split_doc = {
                                "id": f"split_{uuid.uuid4().hex[:12]}",
                                "beat_id": beat_id,
                                "beat_title": beat.get("title", "") if beat else "",
                                "contract_id": contract_id or "",
                                "license_type": license_type,
                                "producer_id": producer_id,
                                "producer_name": beat.get("artist_name", "Producer") if beat else "Producer",
                                "artist_id": user_id,
                                "artist_name": user.get("artist_name") or user.get("name", ""),
                                "producer_split": default_splits["producer"],
                                "artist_split": default_splits["artist"],
                                "status": "active",
                                "created_at": now,
                                "updated_at": now,
                            }
                            await db.royalty_splits.insert_one(split_doc)
                            logger.info(f"Royalty split created: {split_doc['id']} ({default_splits['producer']}/{default_splits['artist']})")
                        except Exception as e:
                            logger.warning(f"Royalty split creation failed: {e}")
            # Handle subscriptions
            elif purchase_type == "subscription":
                plan = metadata.get("plan")
                user_id = metadata.get("user_id")
                if plan and user_id:
                    await db.users.update_one({"id": user_id}, {"$set": {"plan": plan}})
                    await db.subscriptions.update_one({"user_id": user_id}, {"$set": {
                        "user_id": user_id, "plan": plan, "status": "active",
                        "updated_at": now}}, upsert=True)
                    await db.payment_transactions.update_one({"session_id": webhook_response.session_id},
                        {"$set": {"payment_status": "paid", "paid_at": now}})
            # Handle release payments
            else:
                release_id = metadata.get("release_id")
                if release_id:
                    await db.releases.update_one({"id": release_id}, {"$set": {"payment_status": "paid"}})
                    await db.payment_transactions.update_one({"session_id": webhook_response.session_id},
                        {"$set": {"payment_status": "paid", "paid_at": now}})
        return {"status": "success"}
    except Exception as e:
        logger.error(f"Webhook error: {e}")
        raise HTTPException(status_code=400, detail="Webhook processing failed")

# ============= WALLET =============
@api_router.get("/wallet", response_model=WalletResponse)
async def get_wallet(request: Request):
    user = await get_current_user(request)
    wallet = await db.wallets.find_one({"user_id": user["id"]}, {"_id": 0})
    if not wallet:
        wallet = {"balance": 0.0, "pending_balance": 0.0, "currency": "USD", "total_earnings": 0.0, "total_withdrawn": 0.0}
    return wallet

@api_router.post("/wallet/withdraw")
async def request_withdrawal(withdrawal: WithdrawalRequest, request: Request):
    user = await get_current_user(request)
    wallet = await db.wallets.find_one({"user_id": user["id"]})
    if not wallet or wallet["balance"] < withdrawal.amount: raise HTTPException(status_code=400, detail="Insufficient balance")
    if withdrawal.amount < 100: raise HTTPException(status_code=400, detail="Minimum payout threshold is $100.00")
    withdrawal_id = f"wd_{uuid.uuid4().hex[:12]}"
    await db.withdrawals.insert_one({"id": withdrawal_id, "user_id": user["id"], "amount": withdrawal.amount,
        "method": withdrawal.method, "paypal_email": withdrawal.paypal_email, "status": "pending",
        "created_at": datetime.now(timezone.utc).isoformat()})
    await db.wallets.update_one({"user_id": user["id"]}, {"$inc": {"balance": -withdrawal.amount, "pending_balance": withdrawal.amount}})
    return {"message": "Withdrawal requested", "withdrawal_id": withdrawal_id}

@api_router.get("/wallet/withdrawals")
async def get_withdrawals(request: Request):
    user = await get_current_user(request)
    return await db.withdrawals.find({"user_id": user["id"]}, {"_id": 0}).sort("created_at", -1).to_list(50)

# ============= COLLABORATION HUB =============

class CollabPostCreate(BaseModel):
    title: str
    looking_for: str  # "vocalist", "producer", "mixer", "songwriter", "feature", "dj", "other"
    genre: str = ""
    description: str = ""
    budget: Optional[str] = ""  # "free", "negotiable", "$100-500", "$500+"
    deadline: Optional[str] = ""

@api_router.post("/collab-hub/posts")
async def create_collab_post(data: CollabPostCreate, request: Request):
    user = await get_current_user(request)
    doc = {
        "id": f"collab_{uuid.uuid4().hex[:12]}",
        "user_id": user["id"],
        "artist_name": user.get("artist_name") or user.get("name", ""),
        "title": data.title,
        "looking_for": data.looking_for,
        "genre": data.genre,
        "description": data.description,
        "budget": data.budget,
        "deadline": data.deadline,
        "status": "open",
        "responses": 0,
        "created_at": datetime.now(timezone.utc).isoformat(),
    }
    await db.collab_posts.insert_one(doc)
    doc.pop("_id", None)
    return doc

@api_router.get("/collab-hub/posts")
async def list_collab_posts(request: Request, looking_for: str = None, genre: str = None):
    user = await get_current_user(request)
    query = {"status": "open", "user_id": {"$ne": user["id"]}}
    if looking_for:
        query["looking_for"] = looking_for
    if genre:
        query["genre"] = {"$regex": genre, "$options": "i"}
    posts = await db.collab_posts.find(query, {"_id": 0, "user_id": 0}).sort("created_at", -1).to_list(50)
    return posts

@api_router.get("/collab-hub/my-posts")
async def my_collab_posts(request: Request):
    user = await get_current_user(request)
    posts = await db.collab_posts.find({"user_id": user["id"]}, {"_id": 0}).sort("created_at", -1).to_list(50)
    return posts

@api_router.put("/collab-hub/posts/{post_id}")
async def update_collab_post(post_id: str, request: Request):
    user = await get_current_user(request)
    body = await request.json()
    allowed = {"title", "looking_for", "genre", "description", "budget", "deadline", "status"}
    updates = {k: v for k, v in body.items() if k in allowed}
    result = await db.collab_posts.update_one({"id": post_id, "user_id": user["id"]}, {"$set": updates})
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Post not found")
    updated = await db.collab_posts.find_one({"id": post_id}, {"_id": 0})
    return updated

@api_router.delete("/collab-hub/posts/{post_id}")
async def delete_collab_post(post_id: str, request: Request):
    user = await get_current_user(request)
    result = await db.collab_posts.delete_one({"id": post_id, "user_id": user["id"]})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Post not found")
    await db.collab_invites.delete_many({"post_id": post_id})
    return {"message": "Post deleted"}

@api_router.post("/collab-hub/invite")
async def send_collab_invite(request: Request):
    user = await get_current_user(request)
    body = await request.json()
    post_id = body.get("post_id", "")
    message = body.get("message", "")
    post = await db.collab_posts.find_one({"id": post_id})
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    if post["user_id"] == user["id"]:
        raise HTTPException(status_code=400, detail="Can't invite yourself")
    existing = await db.collab_invites.find_one({"post_id": post_id, "from_user_id": user["id"]})
    if existing:
        raise HTTPException(status_code=400, detail="Already sent an invite for this post")
    invite = {
        "id": f"inv_{uuid.uuid4().hex[:12]}",
        "post_id": post_id,
        "post_title": post.get("title", ""),
        "from_user_id": user["id"],
        "from_artist_name": user.get("artist_name") or user.get("name", ""),
        "to_user_id": post["user_id"],
        "to_artist_name": post.get("artist_name", ""),
        "message": message,
        "status": "pending",
        "created_at": datetime.now(timezone.utc).isoformat(),
    }
    await db.collab_invites.insert_one(invite)
    invite.pop("_id", None)
    await db.collab_posts.update_one({"id": post_id}, {"$inc": {"responses": 1}})
    # Remove internal user IDs from response
    invite.pop("from_user_id", None)
    invite.pop("to_user_id", None)
    await db.notifications.insert_one({
        "id": f"notif_{uuid.uuid4().hex[:12]}", "user_id": post["user_id"],
        "type": "collab_invite",
        "message": f"{user.get('artist_name', 'Someone')} wants to collaborate on \"{post['title']}\"",
        "read": False, "action_url": "/collaborations", "created_at": datetime.now(timezone.utc).isoformat(),
    })
    return invite

@api_router.get("/collab-hub/invites")
async def get_collab_invites(request: Request):
    user = await get_current_user(request)
    received = await db.collab_invites.find({"to_user_id": user["id"]}, {"_id": 0, "to_user_id": 0}).sort("created_at", -1).to_list(50)
    sent = await db.collab_invites.find({"from_user_id": user["id"]}, {"_id": 0, "from_user_id": 0}).sort("created_at", -1).to_list(50)
    return {"received": received, "sent": sent}

@api_router.put("/collab-hub/invites/{invite_id}")
async def respond_to_invite(invite_id: str, request: Request):
    user = await get_current_user(request)
    body = await request.json()
    action = body.get("action", "")  # "accept" or "decline"
    if action not in ("accept", "decline"):
        raise HTTPException(status_code=400, detail="Action must be accept or decline")
    invite = await db.collab_invites.find_one({"id": invite_id, "to_user_id": user["id"]})
    if not invite:
        raise HTTPException(status_code=404, detail="Invite not found")
    new_status = "accepted" if action == "accept" else "declined"
    await db.collab_invites.update_one({"id": invite_id}, {"$set": {"status": new_status}})
    if action == "accept":
        await db.collab_posts.update_one({"id": invite["post_id"]}, {"$set": {"status": "in_progress"}})
        # Auto-create a conversation between the two collaborators
        participants = sorted([user["id"], invite["from_user_id"]])
        existing_convo = await db.conversations.find_one({"participants": participants, "invite_id": invite_id})
        if not existing_convo:
            convo_id = f"convo_{uuid.uuid4().hex[:12]}"
            await db.conversations.insert_one({
                "id": convo_id,
                "participants": participants,
                "invite_id": invite_id,
                "post_title": invite.get("post_title", ""),
                "created_at": datetime.now(timezone.utc).isoformat(),
                "updated_at": datetime.now(timezone.utc).isoformat(),
            })
            # Insert a system message
            await db.messages.insert_one({
                "id": f"msg_{uuid.uuid4().hex[:12]}",
                "conversation_id": convo_id,
                "sender_id": "system",
                "sender_name": "Kalmori",
                "text": f"Collaboration accepted! You can now discuss \"{invite.get('post_title', 'your project')}\" here.",
                "read": False,
                "created_at": datetime.now(timezone.utc).isoformat(),
            })
    await db.notifications.insert_one({
        "id": f"notif_{uuid.uuid4().hex[:12]}", "user_id": invite["from_user_id"],
        "type": "collab_response",
        "message": f"{user.get('artist_name', 'Someone')} {new_status} your collaboration invite for \"{invite['post_title']}\"",
        "read": False, "action_url": "/collaborations", "created_at": datetime.now(timezone.utc).isoformat(),
    })
    return {"message": f"Invite {new_status}"}

# ============= IN-APP MESSAGING =============
# Moved to routes/messages_routes.py

# ============= RELEASE CALENDAR =============

INDUSTRY_DATES = [
    {"title": "New Music Friday", "type": "recurring", "day_of_week": 4, "color": "#7C4DFF", "icon": "music"},
    {"title": "Spotify Editorial Deadline", "type": "recurring", "day_of_week": 1, "color": "#1DB954", "icon": "spotify"},
    {"title": "Apple Music Submission Window", "type": "recurring", "day_of_week": 1, "color": "#FC3C44", "icon": "apple"},
]

@api_router.get("/calendar/events")
async def get_calendar_events(request: Request, month: int = None, year: int = None):
    user = await get_current_user(request)
    now = datetime.now(timezone.utc)
    m = month or now.month
    y = year or now.year

    # Get release dates
    releases = await db.releases.find(
        {"artist_id": user["id"]}, {"_id": 0, "id": 1, "title": 1, "release_date": 1, "status": 1}
    ).to_list(200)

    events = []
    for r in releases:
        if r.get("release_date"):
            events.append({
                "id": f"rel_{r['id']}",
                "title": r["title"],
                "date": r["release_date"],
                "type": "release",
                "status": r.get("status", "draft"),
                "color": "#E040FB",
                "release_id": r["id"],
            })

    # Get custom events
    custom = await db.calendar_events.find(
        {"user_id": user["id"]}, {"_id": 0}
    ).to_list(200)
    events.extend(custom)

    # Generate industry dates for the requested month
    import calendar
    _, days_in_month = calendar.monthrange(y, m)
    for day in range(1, days_in_month + 1):
        d = datetime(y, m, day)
        for ind in INDUSTRY_DATES:
            if ind["type"] == "recurring" and d.weekday() == ind["day_of_week"]:
                events.append({
                    "id": f"ind_{ind['title'][:3]}_{y}{m:02d}{day:02d}",
                    "title": ind["title"],
                    "date": d.strftime("%Y-%m-%d"),
                    "type": "industry",
                    "color": ind["color"],
                })

    return {"events": events, "month": m, "year": y}


class CalendarEventCreate(BaseModel):
    title: str
    date: str  # YYYY-MM-DD
    event_type: str = "custom"  # custom, reminder, deadline
    color: str = "#7C4DFF"
    notes: Optional[str] = ""
    reminder: bool = False

@api_router.post("/calendar/events")
async def create_calendar_event(data: CalendarEventCreate, request: Request):
    user = await get_current_user(request)
    doc = {
        "id": f"evt_{uuid.uuid4().hex[:12]}",
        "user_id": user["id"],
        "title": data.title,
        "date": data.date,
        "type": data.event_type,
        "color": data.color,
        "notes": data.notes,
        "reminder": data.reminder,
        "created_at": datetime.now(timezone.utc).isoformat(),
    }
    await db.calendar_events.insert_one(doc)
    doc.pop("_id", None)
    return doc

@api_router.put("/calendar/events/{event_id}")
async def update_calendar_event(event_id: str, request: Request):
    user = await get_current_user(request)
    body = await request.json()
    allowed = {"title", "date", "color", "notes", "reminder", "type"}
    updates = {k: v for k, v in body.items() if k in allowed}
    result = await db.calendar_events.update_one(
        {"id": event_id, "user_id": user["id"]}, {"$set": updates}
    )
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Event not found")
    updated = await db.calendar_events.find_one({"id": event_id}, {"_id": 0})
    return updated

@api_router.delete("/calendar/events/{event_id}")
async def delete_calendar_event(event_id: str, request: Request):
    user = await get_current_user(request)
    result = await db.calendar_events.delete_one({"id": event_id, "user_id": user["id"]})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Event not found")
    return {"message": "Event deleted"}

@api_router.get("/calendar/upcoming")
async def get_upcoming_events(request: Request):
    """Get countdown for upcoming release dates"""
    user = await get_current_user(request)
    now = datetime.now(timezone.utc)
    today = now.strftime("%Y-%m-%d")

    releases = await db.releases.find(
        {"artist_id": user["id"], "release_date": {"$gte": today}},
        {"_id": 0, "id": 1, "title": 1, "release_date": 1, "status": 1, "cover_url": 1}
    ).sort("release_date", 1).to_list(10)

    custom = await db.calendar_events.find(
        {"user_id": user["id"], "date": {"$gte": today}},
        {"_id": 0}
    ).sort("date", 1).to_list(10)

    upcoming = []
    for r in releases:
        rd = datetime.strptime(r["release_date"], "%Y-%m-%d").replace(tzinfo=timezone.utc)
        days_until = (rd - now).days
        upcoming.append({
            "id": r["id"], "title": r["title"], "date": r["release_date"],
            "days_until": max(0, days_until), "type": "release",
            "status": r.get("status"), "cover_url": r.get("cover_url"),
        })
    for e in custom:
        ed = datetime.strptime(e["date"], "%Y-%m-%d").replace(tzinfo=timezone.utc)
        days_until = (ed - now).days
        upcoming.append({
            "id": e["id"], "title": e["title"], "date": e["date"],
            "days_until": max(0, days_until), "type": e.get("type", "custom"),
            "color": e.get("color"),
        })

    upcoming.sort(key=lambda x: x["date"])
    return {"upcoming": upcoming[:10]}

# ============= NOTIFICATIONS =============
@api_router.get("/notifications")
async def get_notifications(request: Request):
    user = await get_current_user(request)
    return await db.notifications.find({"user_id": user["id"]}, {"_id": 0}).sort("created_at", -1).to_list(50)

@api_router.get("/notifications/unread-count")
async def get_unread_count(request: Request):
    user = await get_current_user(request)
    count = await db.notifications.count_documents({"user_id": user["id"], "read": False})
    return {"count": count}

@api_router.put("/notifications/{notification_id}/read")
async def mark_notification_read(notification_id: str, request: Request):
    user = await get_current_user(request)
    await db.notifications.update_one({"id": notification_id, "user_id": user["id"]}, {"$set": {"read": True}})
    return {"message": "Marked as read"}

@api_router.put("/notifications/read-all")
async def mark_all_notifications_read(request: Request):
    user = await get_current_user(request)
    result = await db.notifications.update_many({"user_id": user["id"], "read": False}, {"$set": {"read": True}})
    return {"message": f"Marked {result.modified_count} notifications as read"}


@api_router.get("/features")
async def get_features(request: Request):
    """Get all feature announcements with access info for the current user"""
    user = await get_current_user(request)
    user_plan = user.get("plan", "free")
    plan_hierarchy = {"free": 0, "rise": 1, "pro": 2}
    user_level = plan_hierarchy.get(user_plan, 0)

    announcements = await db.feature_announcements.find({}, {"_id": 0}).sort("created_at", -1).to_list(100)
    for a in announcements:
        min_level = plan_hierarchy.get(a.get("min_plan", "free"), 0)
        a["has_access"] = user_level >= min_level
        a["upgrade_plan"] = a.get("min_plan", "free").capitalize() if not a["has_access"] else None
    return announcements

# Admin routes moved to routes/admin_routes.py

# ============= SPLIT PAYMENTS =============
@api_router.post("/splits")
async def create_split(split: SplitCreate, request: Request):
    user = await get_current_user(request)
    track = await db.tracks.find_one({"id": split.track_id, "artist_id": user["id"]})
    if not track: raise HTTPException(status_code=404, detail="Track not found")
    total_pct = sum(c.percentage for c in split.collaborators)
    if total_pct > 100: raise HTTPException(status_code=400, detail="Total split percentages cannot exceed 100%")
    if total_pct < 0: raise HTTPException(status_code=400, detail="Percentages must be positive")
    owner_pct = 100.0 - total_pct
    split_id = f"split_{uuid.uuid4().hex[:12]}"
    split_doc = {"id": split_id, "track_id": split.track_id, "release_id": track["release_id"],
        "owner_id": user["id"], "owner_name": user.get("artist_name", user["name"]),
        "owner_percentage": owner_pct, "collaborators": [c.model_dump() for c in split.collaborators],
        "status": "active", "created_at": datetime.now(timezone.utc).isoformat()}
    await db.splits.update_one({"track_id": split.track_id}, {"$set": split_doc}, upsert=True)
    return {"message": "Split agreement created", "split_id": split_id, "owner_percentage": owner_pct}

@api_router.get("/splits/{track_id}")
async def get_split(track_id: str, request: Request):
    await get_current_user(request)
    split = await db.splits.find_one({"track_id": track_id}, {"_id": 0})
    if not split: return {"track_id": track_id, "collaborators": [], "owner_percentage": 100.0}
    return split

@api_router.put("/splits/{track_id}")
async def update_split(track_id: str, update: SplitUpdate, request: Request):
    user = await get_current_user(request)
    track = await db.tracks.find_one({"id": track_id, "artist_id": user["id"]})
    if not track: raise HTTPException(status_code=404, detail="Track not found")
    total_pct = sum(c.percentage for c in update.collaborators)
    if total_pct > 100: raise HTTPException(status_code=400, detail="Total split percentages cannot exceed 100%")
    await db.splits.update_one({"track_id": track_id}, {"$set": {
        "collaborators": [c.model_dump() for c in update.collaborators],
        "owner_percentage": 100.0 - total_pct, "updated_at": datetime.now(timezone.utc).isoformat()}})
    return {"message": "Split updated", "owner_percentage": 100.0 - total_pct}

@api_router.delete("/splits/{track_id}")
async def delete_split(track_id: str, request: Request):
    user = await get_current_user(request)
    track = await db.tracks.find_one({"id": track_id, "artist_id": user["id"]})
    if not track: raise HTTPException(status_code=404, detail="Track not found")
    await db.splits.delete_one({"track_id": track_id})
    return {"message": "Split agreement removed"}

# ============= BEAT PURCHASES & CONTRACTS =============

LICENSE_TERMS = {
    "basic_lease": {
        "name": "Basic Lease",
        "rights": "Non-exclusive license",
        "file_types": "MP3 (320kbps)",
        "streams": "Up to 5,000 streams",
        "sales": "Up to 500 sales",
        "music_video": "Not included",
        "credit": "Credit to producer required",
        "ownership": "Producer retains full ownership",
        "duration": "Perpetual (non-exclusive)",
    },
    "premium_lease": {
        "name": "Premium Lease",
        "rights": "Non-exclusive license",
        "file_types": "WAV + MP3 + Trackouts",
        "streams": "Up to 50,000 streams",
        "sales": "Up to 5,000 sales",
        "music_video": "1 music video allowed",
        "credit": "Credit to producer required",
        "ownership": "Producer retains full ownership",
        "duration": "Perpetual (non-exclusive)",
    },
    "unlimited_lease": {
        "name": "Unlimited Lease",
        "rights": "Non-exclusive license",
        "file_types": "WAV + MP3 + Stems",
        "streams": "Unlimited streams",
        "sales": "Unlimited sales",
        "music_video": "Unlimited music videos",
        "credit": "Credit to producer required",
        "ownership": "Producer retains full ownership",
        "duration": "Perpetual (non-exclusive)",
    },
    "exclusive": {
        "name": "Exclusive Rights",
        "rights": "Exclusive license — full ownership transfer",
        "file_types": "All files + Stems + Session files",
        "streams": "Unlimited",
        "sales": "Unlimited",
        "music_video": "Unlimited",
        "credit": "No credit required",
        "ownership": "Full ownership transfers to buyer. Beat removed from catalog.",
        "duration": "Perpetual (exclusive)",
    },
}

from pydantic import BaseModel as PydanticBaseModel

class ContractSign(PydanticBaseModel):
    beat_id: str
    license_type: str
    signer_name: str

@api_router.post("/beats/contract/sign")
async def sign_beat_contract(data: ContractSign, request: Request):
    """Sign a license contract before checkout"""
    user = await get_current_user(request)
    beat = await db.beats.find_one({"id": data.beat_id}, {"_id": 0})
    if not beat:
        raise HTTPException(status_code=404, detail="Beat not found")
    terms = LICENSE_TERMS.get(data.license_type)
    if not terms:
        raise HTTPException(status_code=400, detail="Invalid license type")
    prices = beat.get("prices", {})
    amount = prices.get(data.license_type)
    if not amount:
        raise HTTPException(status_code=400, detail="Price not available for this license")
    contract_id = f"contract_{uuid.uuid4().hex[:12]}"
    contract = {
        "id": contract_id,
        "user_id": user["id"],
        "buyer_email": user.get("email", ""),
        "buyer_name": user.get("artist_name") or user.get("name", ""),
        "signer_name": data.signer_name.strip(),
        "beat_id": data.beat_id,
        "beat_title": beat.get("title", ""),
        "beat_genre": beat.get("genre", ""),
        "beat_bpm": beat.get("bpm", 0),
        "beat_key": beat.get("key", ""),
        "producer_name": beat.get("artist_name") or beat.get("producer", "Kalmori"),
        "license_type": data.license_type,
        "license_name": terms["name"],
        "license_terms": terms,
        "amount": amount,
        "currency": "usd",
        "signed_at": datetime.now(timezone.utc).isoformat(),
        "payment_status": "pending",
        "created_at": datetime.now(timezone.utc).isoformat(),
    }
    await db.beat_contracts.insert_one(contract)
    contract.pop("_id", None)
    return contract

@api_router.get("/beats/contract/{contract_id}")
async def get_contract(contract_id: str, request: Request):
    """Get a signed contract"""
    user = await get_current_user(request)
    contract = await db.beat_contracts.find_one({"id": contract_id}, {"_id": 0})
    if not contract:
        raise HTTPException(status_code=404, detail="Contract not found")
    if contract["user_id"] != user["id"] and user.get("role") != "admin":
        raise HTTPException(status_code=403, detail="Access denied")
    return contract

@api_router.get("/beats/contract/{contract_id}/pdf")
async def download_contract_pdf(contract_id: str, request: Request):
    """Download a signed contract as PDF"""
    user = await get_current_user(request)
    contract = await db.beat_contracts.find_one({"id": contract_id}, {"_id": 0})
    if not contract:
        raise HTTPException(status_code=404, detail="Contract not found")
    if contract["user_id"] != user["id"] and user.get("role") != "admin":
        raise HTTPException(status_code=403, detail="Access denied")
    pdf_bytes = _generate_contract_pdf(contract)
    return StreamingResponse(
        BytesIO(pdf_bytes), media_type="application/pdf",
        headers={"Content-Disposition": f'attachment; filename="Kalmori_License_{contract_id}.pdf"'}
    )

@api_router.get("/admin/contracts")
async def admin_list_contracts(request: Request):
    """Admin: List all signed contracts"""
    await require_admin(request)
    contracts = await db.beat_contracts.find({}, {"_id": 0}).sort("created_at", -1).to_list(200)
    return {"contracts": contracts}

def _generate_contract_pdf(contract):
    from reportlab.lib.pagesizes import letter
    from reportlab.lib import colors
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import inch
    buf = BytesIO()
    doc = SimpleDocTemplate(buf, pagesize=letter, topMargin=0.6*inch, bottomMargin=0.6*inch, leftMargin=0.75*inch, rightMargin=0.75*inch)
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle('Title2', parent=styles['Title'], fontSize=20, spaceAfter=6, textColor=colors.HexColor('#7C4DFF'))
    sub_style = ParagraphStyle('Sub', parent=styles['Normal'], fontSize=10, textColor=colors.grey, spaceAfter=16)
    heading_style = ParagraphStyle('Heading', parent=styles['Heading2'], fontSize=13, textColor=colors.HexColor('#7C4DFF'), spaceAfter=8, spaceBefore=16)
    body_style = ParagraphStyle('Body2', parent=styles['Normal'], fontSize=10, leading=14, spaceAfter=6)
    small_style = ParagraphStyle('Small', parent=styles['Normal'], fontSize=8, textColor=colors.grey, spaceAfter=4)
    terms = contract.get("license_terms", {})
    elements = []
    elements.append(Paragraph("KALMORI", ParagraphStyle('Brand', parent=styles['Title'], fontSize=14, textColor=colors.HexColor('#7C4DFF'), spaceAfter=2, tracking=6)))
    elements.append(Paragraph("Beat License Agreement", title_style))
    elements.append(Paragraph(f"Contract ID: {contract['id']} | Date: {contract.get('signed_at', '')[:10]}", sub_style))
    elements.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor('#333333')))
    elements.append(Spacer(1, 12))
    elements.append(Paragraph("Parties", heading_style))
    party_data = [
        ["", "Licensor (Producer)", "Licensee (Buyer)"],
        ["Name", contract.get("producer_name", "N/A"), contract.get("signer_name", "N/A")],
        ["Email", "—", contract.get("buyer_email", "N/A")],
    ]
    party_table = Table(party_data, colWidths=[0.8*inch, 2.7*inch, 2.7*inch])
    party_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1a1a1a')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#333333')),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.HexColor('#0d0d0d'), colors.HexColor('#111111')]),
        ('TEXTCOLOR', (0, 1), (-1, -1), colors.HexColor('#cccccc')),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ('LEFTPADDING', (0, 0), (-1, -1), 8),
    ]))
    elements.append(party_table)
    elements.append(Spacer(1, 12))
    elements.append(Paragraph("Beat Details", heading_style))
    beat_data = [
        ["Title", contract.get("beat_title", "N/A")],
        ["Genre", contract.get("beat_genre", "N/A")],
        ["BPM", str(contract.get("beat_bpm", "N/A"))],
        ["Key", contract.get("beat_key", "N/A")],
    ]
    beat_table = Table(beat_data, colWidths=[1.5*inch, 4.7*inch])
    beat_table.setStyle(TableStyle([
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#333333')),
        ('TEXTCOLOR', (0, 0), (0, -1), colors.HexColor('#7C4DFF')),
        ('TEXTCOLOR', (1, 0), (1, -1), colors.HexColor('#cccccc')),
        ('ROWBACKGROUNDS', (0, 0), (-1, -1), [colors.HexColor('#0d0d0d'), colors.HexColor('#111111')]),
        ('TOPPADDING', (0, 0), (-1, -1), 5),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
        ('LEFTPADDING', (0, 0), (-1, -1), 8),
    ]))
    elements.append(beat_table)
    elements.append(Spacer(1, 12))
    elements.append(Paragraph("License Terms", heading_style))
    terms_data = [
        ["License Type", terms.get("name", "N/A")],
        ["Rights", terms.get("rights", "N/A")],
        ["File Types", terms.get("file_types", "N/A")],
        ["Streams", terms.get("streams", "N/A")],
        ["Sales", terms.get("sales", "N/A")],
        ["Music Video", terms.get("music_video", "N/A")],
        ["Credit", terms.get("credit", "N/A")],
        ["Ownership", terms.get("ownership", "N/A")],
        ["Duration", terms.get("duration", "N/A")],
        ["Price", f"${contract.get('amount', 0):.2f} USD"],
    ]
    terms_table = Table(terms_data, colWidths=[1.5*inch, 4.7*inch])
    terms_table.setStyle(TableStyle([
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#333333')),
        ('TEXTCOLOR', (0, 0), (0, -1), colors.HexColor('#7C4DFF')),
        ('TEXTCOLOR', (1, 0), (1, -1), colors.HexColor('#cccccc')),
        ('ROWBACKGROUNDS', (0, 0), (-1, -1), [colors.HexColor('#0d0d0d'), colors.HexColor('#111111')]),
        ('TOPPADDING', (0, 0), (-1, -1), 5),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
        ('LEFTPADDING', (0, 0), (-1, -1), 8),
    ]))
    elements.append(terms_table)
    elements.append(Spacer(1, 16))
    elements.append(Paragraph("Digital Signature", heading_style))
    elements.append(Paragraph(f"Signed by: <b>{contract.get('signer_name', 'N/A')}</b>", body_style))
    elements.append(Paragraph(f"Date: {contract.get('signed_at', '')[:10]}", body_style))
    elements.append(Paragraph(f"Payment Status: {contract.get('payment_status', 'pending').upper()}", body_style))
    elements.append(Spacer(1, 20))
    elements.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor('#333333')))
    elements.append(Spacer(1, 8))
    elements.append(Paragraph("This agreement is binding upon signing. The Licensee agrees to the terms above.", small_style))
    elements.append(Paragraph("Kalmori Digital Distribution Platform | support@kalmori.org", small_style))
    doc.build(elements)
    return buf.getvalue()

class BeatPurchaseCheckout(PydanticBaseModel):
    beat_id: str
    license_type: str
    contract_id: str
    origin_url: str

@api_router.post("/beats/purchase/checkout")
async def create_beat_purchase_checkout(data: BeatPurchaseCheckout, request: Request):
    from emergentintegrations.payments.stripe.checkout import StripeCheckout, CheckoutSessionRequest
    user = await get_current_user(request)
    # Verify signed contract exists
    contract = await db.beat_contracts.find_one({"id": data.contract_id, "user_id": user["id"], "payment_status": "pending"})
    if not contract:
        raise HTTPException(status_code=400, detail="Valid signed contract required before checkout")
    beat = await db.beats.find_one({"id": data.beat_id}, {"_id": 0})
    if not beat:
        raise HTTPException(status_code=404, detail="Beat not found")
    amount = contract["amount"]
    stripe_api_key = os.environ.get("STRIPE_API_KEY")
    host_url = str(request.base_url)
    stripe_checkout = StripeCheckout(api_key=stripe_api_key, webhook_url=f"{host_url}api/webhook/stripe")
    session = await stripe_checkout.create_checkout_session(CheckoutSessionRequest(
        amount=amount, currency="usd",
        success_url=f"{data.origin_url}/purchases?purchase=success&beat_id={data.beat_id}&license={data.license_type}&contract_id={data.contract_id}&session_id={{CHECKOUT_SESSION_ID}}",
        cancel_url=f"{data.origin_url}/instrumentals?purchase=cancelled",
        metadata={"beat_id": data.beat_id, "user_id": user["id"], "license_type": data.license_type, "contract_id": data.contract_id, "type": "beat_purchase"}))
    await db.beat_purchases.insert_one({
        "id": f"bp_{uuid.uuid4().hex[:12]}", "session_id": session.session_id,
        "user_id": user["id"], "beat_id": data.beat_id, "beat_title": beat["title"],
        "license_type": data.license_type, "contract_id": data.contract_id,
        "amount": amount, "currency": "usd",
        "payment_status": "pending", "created_at": datetime.now(timezone.utc).isoformat()})
    return {"checkout_url": session.url, "session_id": session.session_id, "amount": amount}

@api_router.get("/beats/purchases")
async def get_beat_purchases(request: Request):
    user = await get_current_user(request)
    purchases = await db.beat_purchases.find({"user_id": user["id"]}, {"_id": 0}).sort("created_at", -1).to_list(50)
    return {"purchases": purchases}

# ============= MY PURCHASES (enriched) =============
@api_router.get("/purchases")
async def get_my_purchases(request: Request):
    """Get all user purchases enriched with beat details"""
    user = await get_current_user(request)
    purchases = await db.beat_purchases.find({"user_id": user["id"]}, {"_id": 0}).sort("created_at", -1).to_list(100)
    enriched = []
    for p in purchases:
        beat = await db.beats.find_one({"id": p["beat_id"]}, {"_id": 0})
        enriched.append({
            **p,
            "beat": {
                "title": beat.get("title", p.get("beat_title", "Unknown")),
                "genre": beat.get("genre", ""),
                "bpm": beat.get("bpm", 0),
                "key": beat.get("key", ""),
                "mood": beat.get("mood", ""),
                "cover_url": beat.get("cover_url"),
                "audio_url": beat.get("audio_url"),
                "duration": beat.get("duration"),
            } if beat else {"title": p.get("beat_title", "Unknown"), "genre": "", "bpm": 0, "key": "", "mood": "", "cover_url": None, "audio_url": None, "duration": None}
        })
    return {"purchases": enriched, "total": len(enriched)}

@api_router.get("/purchases/{purchase_id}/download")
async def download_purchased_beat(purchase_id: str, request: Request):
    """Download a beat file for a verified purchase"""
    user = await get_current_user(request)
    purchase = await db.beat_purchases.find_one({"id": purchase_id, "user_id": user["id"]}, {"_id": 0})
    if not purchase:
        raise HTTPException(status_code=404, detail="Purchase not found")
    if purchase.get("payment_status") != "paid":
        raise HTTPException(status_code=403, detail="Payment not completed for this purchase")
    beat = await db.beats.find_one({"id": purchase["beat_id"]}, {"_id": 0})
    if not beat or not beat.get("audio_url"):
        raise HTTPException(status_code=404, detail="Beat audio file not available")
    data, content_type = get_object(beat["audio_url"])
    ext = beat["audio_url"].split(".")[-1] if "." in beat["audio_url"] else "mp3"
    safe_title = "".join(c for c in beat.get("title", "beat") if c.isalnum() or c in " _-").strip().replace(" ", "_")
    license_label = purchase.get("license_type", "lease").replace("_", "-")
    filename = f"{safe_title}_{license_label}.{ext}"
    return Response(content=data, media_type=content_type, headers={
        "Content-Disposition": f'attachment; filename="{filename}"',
        "Content-Length": str(len(data)),
    })

# ============= BEAT PURCHASE PAYMENT VERIFICATION =============
@api_router.get("/purchases/verify/{session_id}")
async def verify_beat_purchase(session_id: str, request: Request):
    """Verify and finalize a beat purchase after Stripe payment"""
    from emergentintegrations.payments.stripe.checkout import StripeCheckout
    user = await get_current_user(request)
    stripe_api_key = os.environ.get("STRIPE_API_KEY")
    host_url = str(request.base_url)
    stripe_checkout = StripeCheckout(api_key=stripe_api_key, webhook_url=f"{host_url}api/webhook/stripe")
    status = await stripe_checkout.get_checkout_status(session_id)
    purchase = await db.beat_purchases.find_one({"session_id": session_id, "user_id": user["id"]}, {"_id": 0})
    if not purchase:
        raise HTTPException(status_code=404, detail="Purchase not found")
    if status.payment_status == "paid" and purchase.get("payment_status") != "paid":
        now = datetime.now(timezone.utc).isoformat()
        await db.beat_purchases.update_one({"session_id": session_id},
            {"$set": {"payment_status": "paid", "paid_at": now}})
        # Send receipt email
        receipt_id = f"rcpt_{uuid.uuid4().hex[:12]}"
        await db.receipts.insert_one({
            "id": receipt_id, "user_id": user["id"], "email": user["email"],
            "type": "beat_purchase", "amount": purchase.get("amount", 0),
            "details": {"beat_title": purchase.get("beat_title"), "license_type": purchase.get("license_type")},
            "sent_at": now})
        try:
            from routes.email_routes import send_beat_purchase_receipt
            await send_beat_purchase_receipt(
                user["email"], user.get("name", user.get("artist_name", "Artist")),
                purchase.get("beat_title", "Beat"), purchase.get("license_type", "basic_lease"),
                purchase.get("amount", 0), receipt_id)
        except Exception as e:
            logger.warning(f"Receipt email failed: {e}")
        return {"status": "paid", "purchase": {**purchase, "payment_status": "paid", "paid_at": now}}
    return {"status": purchase.get("payment_status", "pending"), "purchase": purchase}

# ============= EMAIL RECEIPTS =============
@api_router.post("/receipts/send")
async def send_receipt(request: Request):
    """Send email receipt for a purchase (triggered after successful payment)"""
    user = await get_current_user(request)
    body = await request.json()
    txn_id = body.get("transaction_id") or body.get("session_id")
    if not txn_id: raise HTTPException(status_code=400, detail="Transaction ID required")
    txn = await db.payment_transactions.find_one({"$or": [{"id": txn_id}, {"session_id": txn_id}]}, {"_id": 0})
    if not txn:
        txn = await db.beat_purchases.find_one({"$or": [{"id": txn_id}, {"session_id": txn_id}]}, {"_id": 0})
    if not txn: raise HTTPException(status_code=404, detail="Transaction not found")
    receipt_id = f"rcpt_{uuid.uuid4().hex[:12]}"
    await db.receipts.insert_one({
        "id": receipt_id, "user_id": user["id"], "email": user["email"],
        "transaction": txn, "sent_at": datetime.now(timezone.utc).isoformat()})
    try:
        from routes.email_routes import send_email
        await send_email(user["email"], "Your Kalmori Receipt",
            f"<h2>Payment Receipt</h2><p>Thank you for your purchase!</p>"
            f"<p><strong>Amount:</strong> ${txn.get('amount', 0):.2f} USD</p>"
            f"<p><strong>Date:</strong> {txn.get('created_at', 'N/A')}</p>"
            f"<p><strong>Receipt ID:</strong> {receipt_id}</p>"
            f"<p>- The Kalmori Team</p>")
        return {"message": "Receipt sent", "receipt_id": receipt_id}
    except Exception as e:
        logger.warning(f"Receipt email failed: {e}")
        return {"message": "Receipt saved (email delivery pending)", "receipt_id": receipt_id}

# ============= PRODUCER ROYALTY SPLITS =============
# Moved to routes/royalty_routes.py

# ============= ADMIN PAYOUT DASHBOARD =============
# Moved to routes/payouts_routes.py

# ============= DSP DATA IMPORT (CSV) — ADMIN ONLY =============
@api_router.get("/share/beat/{beat_id}")
async def get_beat_share_data(beat_id: str):
    """Get shareable data for a beat (public, no auth)"""
    beat = await db.beats.find_one({"id": beat_id}, {"_id": 0})
    if not beat:
        raise HTTPException(status_code=404, detail="Beat not found")
    return {
        "type": "beat",
        "id": beat["id"],
        "title": beat.get("title", ""),
        "genre": beat.get("genre", ""),
        "bpm": beat.get("bpm", 0),
        "key": beat.get("key", ""),
        "mood": beat.get("mood", ""),
        "cover_url": beat.get("cover_url"),
        "price": beat.get("prices", {}).get("basic_lease", 29.99),
        "og_title": f"{beat.get('title', 'Beat')} | Kalmori Beats",
        "og_description": f"{beat.get('genre', '')} beat - {beat.get('bpm', '')} BPM, Key: {beat.get('key', '')}. Starting at ${beat.get('prices', {}).get('basic_lease', 29.99)}",
    }

@api_router.get("/share/release/{release_id}")
async def get_release_share_data(release_id: str):
    """Get shareable data for a release (public, no auth)"""
    release = await db.releases.find_one({"id": release_id}, {"_id": 0})
    if not release:
        raise HTTPException(status_code=404, detail="Release not found")
    tracks = await db.tracks.find({"release_id": release_id}, {"_id": 0}).to_list(50)
    artist = await db.users.find_one({"id": release.get("artist_id")}, {"_id": 0, "password_hash": 0})
    return {
        "type": "release",
        "id": release["id"],
        "title": release.get("title", ""),
        "artist_name": artist.get("artist_name") or artist.get("name", "") if artist else "",
        "genre": release.get("genre", ""),
        "track_count": len(tracks),
        "cover_url": release.get("cover_art_url"),
        "release_date": release.get("release_date", ""),
        "og_title": f"{release.get('title', 'Release')} by {artist.get('artist_name', '') if artist else ''} | Kalmori",
        "og_description": f"{release.get('genre', '')} - {len(tracks)} tracks. Available on all platforms.",
    }

@api_router.get("/share/artist/{user_id}")
async def get_artist_share_data(user_id: str):
    """Get shareable data for an artist profile (public, no auth)"""
    user = await db.users.find_one({"id": user_id}, {"_id": 0, "password_hash": 0})
    if not user:
        raise HTTPException(status_code=404, detail="Artist not found")
    release_count = await db.releases.count_documents({"artist_id": user_id})
    stream_count = await db.stream_events.count_documents({"artist_id": user_id})
    return {
        "type": "artist",
        "id": user["id"],
        "artist_name": user.get("artist_name") or user.get("name", ""),
        "release_count": release_count,
        "stream_count": stream_count,
        "og_title": f"{user.get('artist_name', 'Artist')} | Kalmori",
        "og_description": f"{release_count} releases, {stream_count:,} streams on Kalmori.",
    }


# ============= PRE-SAVE CAMPAIGNS =============
class PreSaveCampaign(BaseModel):
    release_id: str
    title: str
    description: str = ""
    release_date: str
    spotify_url: str = ""
    apple_music_url: str = ""
    youtube_url: str = ""
    custom_message: str = ""

@api_router.post("/presave/campaigns")
async def create_presave_campaign(data: PreSaveCampaign, request: Request):
    user = await get_current_user(request)
    release = await db.releases.find_one({"id": data.release_id, "artist_id": user["id"]}, {"_id": 0})
    if not release:
        raise HTTPException(status_code=404, detail="Release not found")
    now = datetime.now(timezone.utc).isoformat()
    campaign_id = f"presave_{uuid.uuid4().hex[:12]}"
    campaign = {
        "id": campaign_id,
        "release_id": data.release_id,
        "artist_id": user["id"],
        "artist_name": user.get("artist_name") or user.get("name", ""),
        "title": data.title,
        "description": data.description,
        "release_date": data.release_date,
        "cover_url": release.get("cover_art_url"),
        "spotify_url": data.spotify_url,
        "apple_music_url": data.apple_music_url,
        "youtube_url": data.youtube_url,
        "custom_message": data.custom_message,
        "subscribers": [],
        "subscriber_count": 0,
        "status": "active",
        "created_at": now,
    }
    await db.presave_campaigns.insert_one(campaign)
    campaign.pop("_id", None)
    return {"message": "Pre-save campaign created", "campaign": campaign}

@api_router.get("/presave/campaigns")
async def get_my_presave_campaigns(request: Request):
    user = await get_current_user(request)
    campaigns = await db.presave_campaigns.find({"artist_id": user["id"]}, {"_id": 0}).sort("created_at", -1).to_list(50)
    return {"campaigns": campaigns}

@api_router.get("/presave/{campaign_id}")
async def get_presave_campaign(campaign_id: str):
    """Public endpoint for pre-save landing page"""
    campaign = await db.presave_campaigns.find_one({"id": campaign_id}, {"_id": 0, "subscribers": 0})
    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")
    return campaign

@api_router.post("/presave/{campaign_id}/subscribe")
async def subscribe_presave(campaign_id: str, request: Request):
    """Public endpoint — anyone can subscribe with email"""
    body = await request.json()
    email = body.get("email")
    name = body.get("name", "")
    if not email:
        raise HTTPException(status_code=400, detail="Email required")
    campaign = await db.presave_campaigns.find_one({"id": campaign_id})
    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")
    existing = [s for s in campaign.get("subscribers", []) if s.get("email") == email]
    if existing:
        raise HTTPException(status_code=400, detail="Already subscribed")
    now = datetime.now(timezone.utc).isoformat()
    await db.presave_campaigns.update_one({"id": campaign_id}, {
        "$push": {"subscribers": {"email": email, "name": name, "subscribed_at": now}},
        "$inc": {"subscriber_count": 1}
    })
    # Send confirmation email
    try:
        from routes.email_routes import send_email
        await send_email(email, f"Pre-Save: {campaign.get('title', '')}",
            f"""<div style="font-family:Arial;max-width:600px;margin:0 auto;background:#000;color:#fff;border-radius:16px;overflow:hidden;">
            <div style="background:linear-gradient(90deg,#7C4DFF,#E040FB);padding:30px;text-align:center;">
            <h1 style="color:white;margin:0;font-size:22px;">You're on the list!</h1></div>
            <div style="padding:30px;">
            <p>Hi{' ' + name if name else ''},</p>
            <p>You've pre-saved <strong>{campaign.get('title', '')}</strong> by <strong>{campaign.get('artist_name', '')}</strong>.</p>
            <p>We'll notify you when it drops on <strong>{campaign.get('release_date', 'TBA')}</strong>!</p>
            </div></div>""")
    except Exception as e:
        logger.warning(f"Pre-save email failed: {e}")
    return {"message": "Subscribed! We'll notify you on release day."}

@api_router.delete("/presave/campaigns/{campaign_id}")
async def delete_presave_campaign(campaign_id: str, request: Request):
    user = await get_current_user(request)
    result = await db.presave_campaigns.delete_one({"id": campaign_id, "artist_id": user["id"]})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Campaign not found")
    return {"message": "Campaign deleted"}


# ============= FAN ANALYTICS =============
@api_router.get("/integrations/spotify/status")
async def get_spotify_status(request: Request):
    user = await get_current_user(request)
    connection = await db.integrations.find_one({"user_id": user["id"], "platform": "spotify"}, {"_id": 0})
    if connection:
        return {"connected": True, "spotify_id": connection.get("spotify_id"), "display_name": connection.get("display_name"), "connected_at": connection.get("connected_at")}
    return {"connected": False}

@api_router.post("/integrations/spotify/connect")
async def connect_spotify(request: Request):
    """Placeholder for Spotify OAuth — stores connection intent"""
    user = await get_current_user(request)
    body = await request.json()
    now = datetime.now(timezone.utc).isoformat()
    await db.integrations.update_one(
        {"user_id": user["id"], "platform": "spotify"},
        {"$set": {"user_id": user["id"], "platform": "spotify", "status": "pending",
                  "spotify_id": body.get("spotify_id", ""), "display_name": body.get("display_name", ""),
                  "connected_at": now}},
        upsert=True
    )
    return {"message": "Spotify connection saved. Full OAuth coming soon."}

@api_router.delete("/integrations/spotify/disconnect")
async def disconnect_spotify(request: Request):
    user = await get_current_user(request)
    await db.integrations.delete_one({"user_id": user["id"], "platform": "spotify"})
    return {"message": "Spotify disconnected"}


# ============= SHARE YOUR STATS =============
@api_router.get("/stats/milestones")
async def get_milestones(request: Request):
    user = await get_current_user(request)
    # Aggregate user stats
    total_pipeline = [{"$match": {"artist_id": user["id"]}}, {"$group": {"_id": None, "total_streams": {"$sum": 1}, "total_revenue": {"$sum": "$revenue"}}}]
    total_result = await db.stream_events.aggregate(total_pipeline).to_list(1)
    total = total_result[0] if total_result else {"total_streams": 0, "total_revenue": 0}
    ts = total["total_streams"]
    rev = total["total_revenue"]
    release_count = await db.releases.count_documents({"artist_id": user["id"]})
    # Top platform
    top_platform_pipeline = [{"$match": {"artist_id": user["id"]}}, {"$group": {"_id": "$platform", "count": {"$sum": 1}}}, {"$sort": {"count": -1}}, {"$limit": 1}]
    top_platform_result = await db.stream_events.aggregate(top_platform_pipeline).to_list(1)
    top_platform = top_platform_result[0]["_id"] if top_platform_result else "N/A"
    # Top country
    top_country_pipeline = [{"$match": {"artist_id": user["id"]}}, {"$group": {"_id": "$country", "count": {"$sum": 1}}}, {"$sort": {"count": -1}}, {"$limit": 1}]
    top_country_result = await db.stream_events.aggregate(top_country_pipeline).to_list(1)
    top_country = top_country_result[0]["_id"] if top_country_result else "N/A"
    # Generate milestones
    milestones = []
    stream_thresholds = [100, 500, 1000, 5000, 10000, 50000, 100000, 500000, 1000000]
    for thresh in stream_thresholds:
        if ts >= thresh:
            milestones.append({"type": "streams", "value": thresh, "label": f"{thresh:,} Streams", "achieved": True})
        else:
            milestones.append({"type": "streams", "value": thresh, "label": f"{thresh:,} Streams", "achieved": False})
            break
    return {
        "stats": {
            "total_streams": ts,
            "total_revenue": round(rev, 2),
            "release_count": release_count,
            "top_platform": top_platform,
            "top_country": top_country,
            "artist_name": user.get("artist_name") or user.get("name", "Artist"),
        },
        "milestones": milestones,
    }


@api_router.get("/stats/share-card")
async def get_share_card_data(request: Request):
    """Generate data for a shareable stats card"""
    user = await get_current_user(request)
    pipeline = [{"$match": {"artist_id": user["id"]}}, {"$group": {"_id": None, "total_streams": {"$sum": 1}, "total_revenue": {"$sum": "$revenue"}}}]
    result = await db.stream_events.aggregate(pipeline).to_list(1)
    totals = result[0] if result else {"total_streams": 0, "total_revenue": 0}
    # Top platforms
    platform_pipeline = [{"$match": {"artist_id": user["id"]}}, {"$group": {"_id": "$platform", "count": {"$sum": 1}}}, {"$sort": {"count": -1}}, {"$limit": 3}]
    top_platforms = await db.stream_events.aggregate(platform_pipeline).to_list(3)
    release_count = await db.releases.count_documents({"artist_id": user["id"]})
    return {
        "artist_name": user.get("artist_name") or user.get("name", "Artist"),
        "total_streams": totals["total_streams"],
        "total_revenue": round(totals["total_revenue"], 2),
        "release_count": release_count,
        "top_platforms": [{"name": p["_id"], "streams": p["count"]} for p in top_platforms],
        "generated_at": datetime.now(timezone.utc).isoformat(),
    }


# ============= NOTIFICATION PREFERENCES =============
@api_router.get("/settings/notification-preferences")
async def get_notification_prefs(request: Request):
    user = await get_current_user(request)
    prefs = await db.notification_preferences.find_one({"user_id": user["id"]}, {"_id": 0})
    defaults = {
        "user_id": user["id"],
        "email_releases": True,
        "email_collaborations": True,
        "email_payments": True,
        "email_marketing": False,
        "push_releases": True,
        "push_collaborations": True,
        "push_payments": True,
        "push_milestones": True,
        "email_weekly_digest": True,
    }
    if not prefs:
        prefs = defaults
        await db.notification_preferences.insert_one({**prefs})
    else:
        # Ensure new fields have defaults for existing users
        for key, val in defaults.items():
            if key not in prefs:
                prefs[key] = val
    prefs.pop("_id", None)
    return prefs

@api_router.put("/settings/notification-preferences")
async def update_notification_prefs(request: Request):
    user = await get_current_user(request)
    body = await request.json()
    allowed_keys = ["email_releases", "email_collaborations", "email_payments", "email_marketing",
                    "push_releases", "push_collaborations", "push_payments", "push_milestones",
                    "email_weekly_digest"]
    updates = {k: v for k, v in body.items() if k in allowed_keys and isinstance(v, bool)}
    if not updates:
        raise HTTPException(status_code=400, detail="No valid preferences provided")
    await db.notification_preferences.update_one(
        {"user_id": user["id"]},
        {"$set": updates},
        upsert=True
    )
    return {"message": "Preferences updated"}


# ============= FILE SERVING =============
@api_router.get("/files/{path:path}")
async def serve_file(path: str, request: Request, auth: Optional[str] = Query(None)):
    token = request.cookies.get("access_token") or auth
    if not token:
        auth_header = request.headers.get("Authorization", "")
        if auth_header.startswith("Bearer "): token = auth_header[7:]
    if not token: raise HTTPException(status_code=401, detail="Not authenticated")
    try:
        data, content_type = get_object(path)
        return Response(content=data, media_type=content_type)
    except Exception as e:
        logger.error(f"File serve error: {e}")
        raise HTTPException(status_code=404, detail="File not found")

# ============= HEALTH =============
# Label routes moved to routes/label_routes.py
# Admin royalty/template/reconciliation routes moved to routes/admin_routes.py

# ============= ARTIST PUBLIC PROFILE =============
import re

def generate_slug(name: str) -> str:
    """Generate URL-safe slug from artist name"""
    slug = name.lower().strip()
    slug = re.sub(r'[^a-z0-9\s-]', '', slug)
    slug = re.sub(r'[\s-]+', '-', slug)
    slug = slug.strip('-')
    return slug or f"artist-{uuid.uuid4().hex[:8]}"

class UpdateSlugInput(BaseModel):
    slug: str

@api_router.put("/artist/profile/slug")
async def set_artist_slug(data: UpdateSlugInput, request: Request):
    """Set a custom slug for the artist's public profile URL"""
    user = await get_current_user(request)
    slug = generate_slug(data.slug)
    if len(slug) < 2:
        raise HTTPException(status_code=400, detail="Slug must be at least 2 characters")
    if len(slug) > 50:
        raise HTTPException(status_code=400, detail="Slug must be under 50 characters")
    existing = await db.artist_profiles.find_one({"slug": slug, "user_id": {"$ne": user["id"]}})
    if existing:
        raise HTTPException(status_code=409, detail="This URL is already taken. Try a different one.")
    await db.artist_profiles.update_one(
        {"user_id": user["id"]},
        {"$set": {"slug": slug, "updated_at": datetime.now(timezone.utc).isoformat()}},
        upsert=True
    )
    return {"message": "Profile URL updated", "slug": slug}

@api_router.get("/artist/profile/slug")
async def get_artist_slug(request: Request):
    """Get the current user's slug"""
    user = await get_current_user(request)
    profile = await db.artist_profiles.find_one({"user_id": user["id"]}, {"_id": 0, "slug": 1})
    slug = profile.get("slug") if profile else None
    if not slug:
        slug = generate_slug(user.get("artist_name", user.get("name", "artist")))
        await db.artist_profiles.update_one(
            {"user_id": user["id"]},
            {"$set": {"slug": slug}},
            upsert=True
        )
    return {"slug": slug}

@api_router.get("/artist/{slug}")
async def get_public_artist_profile(slug: str):
    """Public endpoint - no auth required. Returns artist profile for public display."""
    profile = await db.artist_profiles.find_one({"slug": slug}, {"_id": 0})
    if not profile:
        raise HTTPException(status_code=404, detail="Artist not found")
    user_id = profile["user_id"]
    user = await db.users.find_one({"id": user_id}, {"_id": 0, "password_hash": 0})
    if not user:
        raise HTTPException(status_code=404, detail="Artist not found")

    # Get distributed releases
    releases = await db.releases.find(
        {"artist_id": user_id, "status": {"$in": ["distributed", "pending_review"]}},
        {"_id": 0, "id": 1, "title": 1, "release_type": 1, "genre": 1, "cover_art_url": 1, "release_date": 1, "status": 1, "track_count": 1}
    ).sort("created_at", -1).to_list(20)

    # Get stream counts per release
    stream_pipeline = [
        {"$match": {"artist_id": user_id}},
        {"$group": {"_id": "$release_id", "streams": {"$sum": 1}}}
    ]
    stream_data = {r["_id"]: r["streams"] for r in await db.stream_events.aggregate(stream_pipeline).to_list(200)}

    # Fetch tracks for each release (for audio previews)
    for r in releases:
        r["total_streams"] = stream_data.get(r["id"], 0)
        tracks = await db.tracks.find(
            {"release_id": r["id"], "audio_url": {"$ne": None}},
            {"_id": 0, "id": 1, "title": 1, "duration": 1, "track_number": 1}
        ).sort("track_number", 1).to_list(50)
        r["tracks"] = tracks

    # Get active pre-save campaigns
    presave_campaigns = await db.presave_campaigns.find(
        {"artist_id": user_id, "status": "active"},
        {"_id": 0, "id": 1, "release_title": 1, "release_date": 1, "cover_art_url": 1, "subscriber_count": 1, "platforms": 1}
    ).to_list(10)

    # Total streams
    total_streams_pipeline = [
        {"$match": {"artist_id": user_id}},
        {"$group": {"_id": None, "total": {"$sum": 1}}}
    ]
    total_result = await db.stream_events.aggregate(total_streams_pipeline).to_list(1)
    total_streams = total_result[0]["total"] if total_result else 0

    return {
        "artist_name": profile.get("artist_name", user.get("artist_name", user.get("name", "Artist"))),
        "bio": profile.get("bio"),
        "genre": profile.get("genre"),
        "country": profile.get("country"),
        "avatar_url": user.get("avatar_url"),
        "website": profile.get("website"),
        "spotify_url": profile.get("spotify_url"),
        "apple_music_url": profile.get("apple_music_url"),
        "instagram": profile.get("instagram"),
        "twitter": profile.get("twitter"),
        "slug": slug,
        "theme_color": profile.get("theme_color", "#7C4DFF"),
        "releases": releases,
        "presave_campaigns": presave_campaigns,
        "stats": {
            "total_streams": total_streams,
            "total_releases": len(releases),
        }
    }

@api_router.get("/artist/{slug}/track/{track_id}/preview")
async def stream_public_track_preview(slug: str, track_id: str):
    """Public endpoint - stream a 30s preview of a track for the artist profile."""
    profile = await db.artist_profiles.find_one({"slug": slug}, {"_id": 0, "user_id": 1})
    if not profile:
        raise HTTPException(status_code=404, detail="Artist not found")
    track = await db.tracks.find_one({"id": track_id, "artist_id": profile["user_id"]}, {"_id": 0})
    if not track or not track.get("audio_url"):
        raise HTTPException(status_code=404, detail="Track not found")
    try:
        data, content_type = get_object(track["audio_url"])
        return StreamingResponse(BytesIO(data), media_type=content_type,
            headers={"Content-Disposition": f"inline; filename=preview_{track_id}.mp3"})
    except Exception:
        raise HTTPException(status_code=404, detail="Audio not found")

@api_router.get("/artist/{slug}/qr")
async def get_artist_qr_code(slug: str, request: Request):
    """Generate QR code PNG for the artist's public profile URL."""
    import qrcode
    from io import BytesIO as QRBuf
    profile = await db.artist_profiles.find_one({"slug": slug}, {"_id": 0, "user_id": 1})
    if not profile:
        raise HTTPException(status_code=404, detail="Artist not found")
    frontend_url = os.environ.get("FRONTEND_URL", "")
    profile_url = f"{frontend_url}/artist/{slug}"
    qr = qrcode.QRCode(version=1, error_correction=qrcode.constants.ERROR_CORRECT_H, box_size=10, border=2)
    qr.add_data(profile_url)
    qr.make(fit=True)
    img = qr.make_image(fill_color="#7C4DFF", back_color="#0A0A0A")
    buf = QRBuf()
    img.save(buf, format="PNG")
    buf.seek(0)
    return StreamingResponse(buf, media_type="image/png",
        headers={"Content-Disposition": f"inline; filename={slug}-qr.png"})

class UpdateThemeInput(BaseModel):
    theme_color: str

@api_router.put("/artist/profile/theme")
async def set_artist_theme(data: UpdateThemeInput, request: Request):
    """Set the theme color for the artist's public profile."""
    user = await get_current_user(request)
    color = data.theme_color.strip()
    if not re.match(r'^#[0-9A-Fa-f]{6}$', color):
        raise HTTPException(status_code=400, detail="Invalid hex color")
    await db.artist_profiles.update_one(
        {"user_id": user["id"]},
        {"$set": {"theme_color": color, "updated_at": datetime.now(timezone.utc).isoformat()}},
        upsert=True
    )
    return {"message": "Theme updated", "theme_color": color}

@api_router.get("/artist/profile/theme")
async def get_artist_theme(request: Request):
    """Get the current user's theme color."""
    user = await get_current_user(request)
    profile = await db.artist_profiles.find_one({"user_id": user["id"]}, {"_id": 0, "theme_color": 1})
    return {"theme_color": (profile or {}).get("theme_color", "#7C4DFF")}

@api_router.post("/cookie-consent")
async def log_cookie_consent(request: Request):
    """Log cookie consent for compliance records"""
    body = await request.json()
    ip = request.headers.get("x-forwarded-for", request.client.host if request.client else "unknown")
    user = None
    try:
        user = await get_current_user(request)
    except:
        pass

    await db.cookie_consents.insert_one({
        "id": f"cc_{uuid.uuid4().hex[:12]}",
        "user_id": user["id"] if user else None,
        "level": body.get("level", "unknown"),
        "ip_address": ip.split(",")[0].strip(),
        "user_agent": body.get("userAgent", ""),
        "timestamp": body.get("timestamp", datetime.now(timezone.utc).isoformat()),
        "created_at": datetime.now(timezone.utc).isoformat(),
    })
    return {"message": "Consent recorded"}


@api_router.get("/health")
async def health_check():
    return {"status": "healthy", "timestamp": datetime.now(timezone.utc).isoformat()}

# ============= REGISTER ROUTERS =============
app.include_router(api_router)

from kalmori_routes import kalmori_router, init_cms_content
app.include_router(kalmori_router)

from routes.ai_routes import ai_router
from routes.email_routes import email_router
from routes.paypal_routes import paypal_router
from routes.content_routes import content_router
from routes.beats_routes import beats_router, init_beats_routes
from routes.collab_routes import collab_router
from routes.admin_routes import admin_router
from routes.label_routes import label_router
from routes.messages_routes import messages_router
from routes.royalty_routes import royalty_routes
from routes.payouts_routes import payouts_router
from routes.page_builder_routes import page_builder_router
from routes.spotify_routes import spotify_router
from routes.analytics_routes import analytics_router
from routes.subscription_routes import subscription_router

init_beats_routes(db, put_object, get_object, get_current_user, require_admin)
app.include_router(ai_router)
app.include_router(email_router)
app.include_router(paypal_router)
app.include_router(content_router)
app.include_router(beats_router)
app.include_router(collab_router)
app.include_router(admin_router)
app.include_router(label_router)
app.include_router(messages_router)
app.include_router(royalty_routes)
app.include_router(payouts_router)
app.include_router(page_builder_router)
app.include_router(spotify_router)
app.include_router(analytics_router)
app.include_router(subscription_router)

# CORS
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_credentials=True,
    allow_methods=["*"], allow_headers=["*"], expose_headers=["*"])

# ============= STARTUP =============
@app.on_event("startup")
async def startup():
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
    await db.beats.create_index("id", unique=True)
    await db.beats.create_index("genre")
    await db.beat_purchases.create_index("user_id")
    await db.beat_purchases.create_index("session_id")
    await db.receipts.create_index("user_id")

    try:
        init_storage()
        logger.info("Object storage initialized")
    except Exception as e:
        logger.error(f"Storage init failed: {e}")

    # Generate voice tag if not present
    tag_path = os.path.join(os.path.dirname(__file__), 'kalmori_tag.mp3')
    if not os.path.exists(tag_path):
        try:
            from emergentintegrations.llm.openai import OpenAITextToSpeech
            tts = OpenAITextToSpeech(api_key=os.environ.get("EMERGENT_LLM_KEY"))
            audio_bytes = await tts.generate_speech(text="Kalmori", model="tts-1", voice="onyx", speed=0.9, response_format="mp3")
            with open(tag_path, 'wb') as f:
                f.write(audio_bytes)
            logger.info(f"Voice tag generated: {len(audio_bytes)} bytes")
        except Exception as e:
            logger.warning(f"Voice tag generation failed: {e}")

    # Seed admin — ensures the configured admin exists on every deployment
    admin_email = os.environ.get("ADMIN_EMAIL", "admin@tunedrop.com")
    admin_password = os.environ.get("ADMIN_PASSWORD", "Admin123!")
    existing = await db.users.find_one({"email": admin_email})
    if not existing:
        # Check if there's a stale default admin to migrate
        default_admin = await db.users.find_one({"email": "admin@tunedrop.com"})
        if default_admin and admin_email != "admin@tunedrop.com":
            await db.users.update_one({"email": "admin@tunedrop.com"}, {"$set": {
                "email": admin_email, "password_hash": hash_password(admin_password),
                "updated_at": datetime.now(timezone.utc).isoformat()
            }})
            logger.info(f"Migrated default admin to {admin_email}")
        else:
            admin_id = f"user_{uuid.uuid4().hex[:12]}"
            await db.users.insert_one({
                "id": admin_id, "email": admin_email, "name": "Admin",
                "artist_name": "Kalmori Admin", "password_hash": hash_password(admin_password),
                "role": "admin", "plan": "pro", "avatar_url": None,
                "created_at": datetime.now(timezone.utc).isoformat()
            })
            await db.wallets.insert_one({
                "user_id": admin_id, "balance": 0.0, "pending_balance": 0.0,
                "currency": "USD", "total_earnings": 0.0, "total_withdrawn": 0.0,
                "created_at": datetime.now(timezone.utc).isoformat()
            })
            logger.info(f"Admin user created: {admin_email}")
    else:
        # Ensure existing admin has correct password (in case of env change)
        if not verify_password(admin_password, existing.get("password_hash", "")):
            await db.users.update_one({"email": admin_email}, {"$set": {
                "password_hash": hash_password(admin_password),
                "updated_at": datetime.now(timezone.utc).isoformat()
            }})
            logger.info(f"Admin password synced for {admin_email}")
    # Also ensure the secondary admin (submitkalmori@gmail.com) exists
    secondary_admin_email = "submitkalmori@gmail.com"
    if admin_email != secondary_admin_email:
        sec_existing = await db.users.find_one({"email": secondary_admin_email})
        if not sec_existing:
            sec_id = f"user_{uuid.uuid4().hex[:12]}"
            await db.users.insert_one({
                "id": sec_id, "email": secondary_admin_email, "name": "Admin",
                "artist_name": "Kalmori Admin", "password_hash": hash_password(admin_password),
                "role": "admin", "plan": "pro", "avatar_url": None,
                "created_at": datetime.now(timezone.utc).isoformat()
            })
            await db.wallets.insert_one({
                "user_id": sec_id, "balance": 0.0, "pending_balance": 0.0,
                "currency": "USD", "total_earnings": 0.0, "total_withdrawn": 0.0,
                "created_at": datetime.now(timezone.utc).isoformat()
            })
            logger.info(f"Secondary admin created: {secondary_admin_email}")
        elif not verify_password(admin_password, sec_existing.get("password_hash", "")):
            await db.users.update_one({"email": secondary_admin_email}, {"$set": {
                "password_hash": hash_password(admin_password),
                "updated_at": datetime.now(timezone.utc).isoformat()
            }})
            logger.info(f"Secondary admin password synced")

    # Seed demo beats
    if await db.beats.count_documents({}) == 0:
        demo_beats = [
            {"id": f"beat_{uuid.uuid4().hex[:12]}", "title": "Midnight Drip", "genre": "Trap", "bpm": 140, "key": "Cm", "mood": "Dark", "tags": ["dark","trap","808"], "duration": "3:24"},
            {"id": f"beat_{uuid.uuid4().hex[:12]}", "title": "Golden Hour", "genre": "R&B/Soul", "bpm": 85, "key": "Eb", "mood": "Chill", "tags": ["chill","rnb","smooth"], "duration": "3:45"},
            {"id": f"beat_{uuid.uuid4().hex[:12]}", "title": "City Lights", "genre": "Hip-Hop", "bpm": 92, "key": "Am", "mood": "Energetic", "tags": ["boom bap","hiphop"], "duration": "2:58"},
            {"id": f"beat_{uuid.uuid4().hex[:12]}", "title": "Lagos Nights", "genre": "Afrobeats", "bpm": 105, "key": "F#m", "mood": "Party", "tags": ["afro","dancehall"], "duration": "3:12"},
            {"id": f"beat_{uuid.uuid4().hex[:12]}", "title": "Sunday Morning", "genre": "Gospel", "bpm": 78, "key": "G", "mood": "Uplifting", "tags": ["gospel","uplifting"], "duration": "4:01"},
            {"id": f"beat_{uuid.uuid4().hex[:12]}", "title": "Neon Dreams", "genre": "Pop", "bpm": 120, "key": "Dm", "mood": "Happy", "tags": ["pop","dance"], "duration": "3:33"},
        ]
        for b in demo_beats:
            b.update({"prices": {"basic_lease": 29.99, "premium_lease": 79.99, "unlimited_lease": 149.99, "exclusive": 499.99},
                "audio_url": None, "preview_url": None, "cover_url": None, "status": "active", "plays": 0,
                "created_by": "system", "created_at": datetime.now(timezone.utc).isoformat(), "updated_at": datetime.now(timezone.utc).isoformat()})
        await db.beats.insert_many(demo_beats)
        logger.info(f"Seeded {len(demo_beats)} demo beats")

    # Initialize CMS
    await init_cms_content()

    # Create indexes for stream_events (real data imported by admin only)
    await db.stream_events.create_index("artist_id")
    await db.stream_events.create_index("timestamp")
    await db.stream_events.create_index("platform")

    # Write test credentials
    from pathlib import Path
    memory_dir = Path(__file__).parent / "memory"
    memory_dir.mkdir(exist_ok=True)
    with open(memory_dir / "test_credentials.md", "w") as f:
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
