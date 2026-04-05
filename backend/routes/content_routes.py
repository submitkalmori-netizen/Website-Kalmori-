"""Spotify Canvas & YouTube Content ID Management"""
from fastapi import APIRouter, HTTPException, Request, UploadFile, File
from pydantic import BaseModel
from motor.motor_asyncio import AsyncIOMotorClient
from datetime import datetime, timezone
from typing import Optional, List
import os
import uuid
import logging
import requests as http_requests

logger = logging.getLogger(__name__)

content_router = APIRouter(prefix="/api")

STORAGE_URL = "https://integrations.emergentagent.com/objstore/api/v1/storage"
EMERGENT_KEY = os.environ.get("EMERGENT_LLM_KEY")

_client = AsyncIOMotorClient(os.environ['MONGO_URL'])
db = _client[os.environ['DB_NAME']]

_storage_key = None

def _init_storage():
    global _storage_key
    if _storage_key:
        return _storage_key
    if not EMERGENT_KEY:
        return None
    try:
        resp = http_requests.post(f"{STORAGE_URL}/init", json={"emergent_key": EMERGENT_KEY}, timeout=30)
        resp.raise_for_status()
        _storage_key = resp.json()["storage_key"]
        return _storage_key
    except Exception as e:
        logger.error(f"Storage init failed: {e}")
        return None

async def _get_user(request: Request):
    from server import get_current_user
    return await get_current_user(request)

# ==================== SPOTIFY CANVAS ====================

class CanvasCreate(BaseModel):
    release_id: str
    track_id: Optional[str] = None

class CanvasResponse(BaseModel):
    id: str
    user_id: str
    release_id: str
    track_id: Optional[str]
    video_url: Optional[str]
    status: str
    specs: dict
    created_at: str
    submitted_at: Optional[str] = None

CANVAS_SPECS = {
    "format": "MP4 (H.264)",
    "aspect_ratio": "9:16 (vertical)",
    "resolution_min": "720x1280",
    "resolution_recommended": "1080x1920",
    "duration": "3-8 seconds",
    "max_size": "20MB",
    "audio": "No audio (video only)",
    "loop": "Must loop seamlessly"
}

@content_router.get("/spotify-canvas/specs")
async def get_canvas_specs():
    return {"specs": CANVAS_SPECS, "tips": [
        "Keep it simple - subtle motion works best",
        "Ensure seamless loop (last frame matches first)",
        "Use 9:16 vertical aspect ratio",
        "No text overlays (Spotify adds its own UI)",
        "Avoid rapid flashing or strobing effects",
        "Test at both 3s and 8s lengths"
    ]}

@content_router.get("/spotify-canvas")
async def get_user_canvases(request: Request):
    user = await _get_user(request)
    canvases = await db.spotify_canvases.find({"user_id": user["id"]}).sort("created_at", -1).to_list(50)
    for c in canvases:
        c.pop("_id", None)
        c["created_at"] = c["created_at"].isoformat() if isinstance(c["created_at"], datetime) else str(c["created_at"])
        if c.get("submitted_at") and isinstance(c["submitted_at"], datetime):
            c["submitted_at"] = c["submitted_at"].isoformat()
    return canvases

@content_router.post("/spotify-canvas")
async def create_canvas(data: CanvasCreate, request: Request):
    user = await _get_user(request)
    release = await db.releases.find_one({"id": data.release_id, "artist_id": user["id"]})
    if not release:
        raise HTTPException(status_code=404, detail="Release not found")
    
    canvas_id = str(uuid.uuid4())
    canvas = {
        "id": canvas_id, "user_id": user["id"], "release_id": data.release_id,
        "track_id": data.track_id, "video_url": None, "video_path": None,
        "status": "draft", "specs": CANVAS_SPECS, "created_at": datetime.now(timezone.utc),
        "submitted_at": None, "release_title": release.get("title", "")
    }
    await db.spotify_canvases.insert_one(canvas)
    canvas.pop("_id", None)
    canvas["created_at"] = canvas["created_at"].isoformat()
    return canvas

@content_router.post("/spotify-canvas/{canvas_id}/upload")
async def upload_canvas_video(canvas_id: str, file: UploadFile = File(...), request: Request = None):
    user = await _get_user(request)
    canvas = await db.spotify_canvases.find_one({"id": canvas_id, "user_id": user["id"]})
    if not canvas:
        raise HTTPException(status_code=404, detail="Canvas not found")
    
    if not file.content_type or not file.content_type.startswith("video/"):
        raise HTTPException(status_code=400, detail="File must be a video (MP4)")
    
    content = await file.read()
    if len(content) > 20 * 1024 * 1024:
        raise HTTPException(status_code=400, detail="File too large. Max 20MB.")
    
    key = _init_storage()
    if not key:
        raise HTTPException(status_code=500, detail="Storage not available")
    
    path = f"kalmori/canvas/{user['id']}/{canvas_id}.mp4"
    try:
        resp = http_requests.put(
            f"{STORAGE_URL}/objects/{path}",
            headers={"X-Storage-Key": key, "Content-Type": "video/mp4"},
            data=content, timeout=60
        )
        resp.raise_for_status()
        video_url = f"{STORAGE_URL}/objects/{path}"
        
        await db.spotify_canvases.update_one(
            {"id": canvas_id},
            {"$set": {"video_url": video_url, "video_path": path, "status": "uploaded"}}
        )
        return {"message": "Canvas video uploaded", "video_url": video_url, "status": "uploaded"}
    except Exception as e:
        logger.error(f"Canvas upload error: {e}")
        raise HTTPException(status_code=500, detail="Failed to upload video")

@content_router.post("/spotify-canvas/{canvas_id}/submit")
async def submit_canvas(canvas_id: str, request: Request):
    user = await _get_user(request)
    canvas = await db.spotify_canvases.find_one({"id": canvas_id, "user_id": user["id"]})
    if not canvas:
        raise HTTPException(status_code=404, detail="Canvas not found")
    if not canvas.get("video_url"):
        raise HTTPException(status_code=400, detail="Upload a video first")
    
    await db.spotify_canvases.update_one(
        {"id": canvas_id},
        {"$set": {"status": "submitted", "submitted_at": datetime.now(timezone.utc)}}
    )
    await db.notifications.insert_one({
        "id": str(uuid.uuid4()), "user_id": user["id"], "type": "canvas",
        "message": f"Canvas for '{canvas.get('release_title', 'your release')}' has been submitted for review. Expected approval: 24-48 hours.",
        "read": False, "action_url": "/spotify-canvas", "created_at": datetime.now(timezone.utc).isoformat()
    })
    return {"message": "Canvas submitted for Spotify review", "status": "submitted"}

@content_router.delete("/spotify-canvas/{canvas_id}")
async def delete_canvas(canvas_id: str, request: Request):
    user = await _get_user(request)
    result = await db.spotify_canvases.delete_one({"id": canvas_id, "user_id": user["id"]})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Canvas not found")
    return {"message": "Canvas deleted"}

# ==================== YOUTUBE CONTENT ID ====================

class ContentIdRegistration(BaseModel):
    release_id: str
    track_id: Optional[str] = None
    ownership_type: str = "composition_and_recording"

@content_router.get("/youtube-content-id")
async def get_content_id_registrations(request: Request):
    user = await _get_user(request)
    registrations = await db.content_id.find({"user_id": user["id"]}).sort("created_at", -1).to_list(50)
    for r in registrations:
        r.pop("_id", None)
        if isinstance(r.get("created_at"), datetime):
            r["created_at"] = r["created_at"].isoformat()
    return registrations

@content_router.post("/youtube-content-id")
async def register_content_id(data: ContentIdRegistration, request: Request):
    user = await _get_user(request)
    release = await db.releases.find_one({"id": data.release_id, "artist_id": user["id"]})
    if not release:
        raise HTTPException(status_code=404, detail="Release not found")
    
    existing = await db.content_id.find_one({"release_id": data.release_id, "user_id": user["id"]})
    if existing:
        raise HTTPException(status_code=400, detail="This release is already registered for Content ID")
    
    reg_id = str(uuid.uuid4())
    registration = {
        "id": reg_id, "user_id": user["id"], "release_id": data.release_id,
        "track_id": data.track_id, "release_title": release.get("title", ""),
        "ownership_type": data.ownership_type, "status": "pending",
        "asset_id": f"A{uuid.uuid4().hex[:12].upper()}", "policy": "monetize",
        "territories": ["worldwide"], "match_policy": "monetize_in_all_countries",
        "created_at": datetime.now(timezone.utc)
    }
    await db.content_id.insert_one(registration)
    
    await db.notifications.insert_one({
        "id": str(uuid.uuid4()), "user_id": user["id"], "type": "content_id",
        "message": f"Content ID registration for '{release.get('title', '')}' is being processed. Asset ID: {registration['asset_id']}",
        "read": False, "action_url": "/content-id", "created_at": datetime.now(timezone.utc).isoformat()
    })
    
    registration.pop("_id", None)
    registration["created_at"] = registration["created_at"].isoformat()
    return registration

@content_router.get("/youtube-content-id/{registration_id}")
async def get_content_id_status(registration_id: str, request: Request):
    user = await _get_user(request)
    reg = await db.content_id.find_one({"id": registration_id, "user_id": user["id"]})
    if not reg:
        raise HTTPException(status_code=404, detail="Registration not found")
    reg.pop("_id", None)
    if isinstance(reg.get("created_at"), datetime):
        reg["created_at"] = reg["created_at"].isoformat()
    return reg

@content_router.put("/youtube-content-id/{registration_id}/policy")
async def update_content_id_policy(registration_id: str, request: Request):
    user = await _get_user(request)
    body = await request.json()
    policy = body.get("policy", "monetize")
    
    if policy not in ["monetize", "track", "block"]:
        raise HTTPException(status_code=400, detail="Invalid policy. Use: monetize, track, or block")
    
    result = await db.content_id.update_one(
        {"id": registration_id, "user_id": user["id"]},
        {"$set": {"policy": policy}}
    )
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Registration not found")
    return {"message": f"Policy updated to '{policy}'"}
