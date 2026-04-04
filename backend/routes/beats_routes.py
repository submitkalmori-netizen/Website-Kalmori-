from fastapi import APIRouter, HTTPException, Request, UploadFile, File, Form
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime, timezone
import uuid
import logging
import os
from io import BytesIO

logger = logging.getLogger(__name__)

VOICE_TAG_PATH = os.path.join(os.path.dirname(__file__), '..', 'kalmori_tag.mp3')

def _watermark_audio(audio_bytes: bytes, tag_interval_sec: int = 15) -> bytes:
    """Overlay voice tag on audio at regular intervals"""
    try:
        from pydub import AudioSegment
        audio = AudioSegment.from_file(BytesIO(audio_bytes))
        tag = AudioSegment.from_mp3(VOICE_TAG_PATH) - 2  # slightly quieter
        tag_interval_ms = tag_interval_sec * 1000
        watermarked = audio
        position = 3000  # start 3s in
        while position < len(audio) - len(tag):
            watermarked = watermarked.overlay(tag, position=position)
            position += tag_interval_ms
        buf = BytesIO()
        watermarked.export(buf, format="mp3", bitrate="192k")
        return buf.getvalue()
    except Exception as e:
        logger.error(f"Watermark failed: {e}")
        return audio_bytes  # fallback to original if watermarking fails

logger = logging.getLogger(__name__)

beats_router = APIRouter(prefix="/api/beats", tags=["Beats"])

# Will be set from server.py
db = None
put_object = None
get_object = None
get_current_user = None
require_admin = None
APP_NAME = "tunedrop"

def init_beats_routes(database, put_obj_fn, get_obj_fn, get_user_fn, require_admin_fn):
    global db, put_object, get_object, get_current_user, require_admin
    db = database
    put_object = put_obj_fn
    get_object = get_obj_fn
    get_current_user = get_user_fn
    require_admin = require_admin_fn


class BeatCreate(BaseModel):
    title: str
    genre: str
    bpm: int = 120
    key: str = "Cm"
    mood: str = ""
    tags: List[str] = []
    price_basic: float = 29.99
    price_premium: float = 79.99
    price_unlimited: float = 149.99
    price_exclusive: float = 499.99


@beats_router.get("")
async def list_beats(
    genre: Optional[str] = None, mood: Optional[str] = None,
    search: Optional[str] = None, key: Optional[str] = None,
    bpm_min: Optional[int] = None, bpm_max: Optional[int] = None,
    price_min: Optional[float] = None, price_max: Optional[float] = None,
    sort_by: Optional[str] = "newest",
    limit: int = 50
):
    query = {"status": "active"}
    if genre:
        query["genre"] = {"$regex": genre, "$options": "i"}
    if mood:
        query["mood"] = {"$regex": mood, "$options": "i"}
    if key:
        query["key"] = {"$regex": f"^{key}", "$options": "i"}
    if search:
        query["$or"] = [
            {"title": {"$regex": search, "$options": "i"}},
            {"genre": {"$regex": search, "$options": "i"}},
            {"mood": {"$regex": search, "$options": "i"}},
            {"tags": {"$regex": search, "$options": "i"}},
        ]
    if bpm_min is not None or bpm_max is not None:
        bpm_q = {}
        if bpm_min is not None:
            bpm_q["$gte"] = bpm_min
        if bpm_max is not None:
            bpm_q["$lte"] = bpm_max
        query["bpm"] = bpm_q
    if price_min is not None or price_max is not None:
        price_q = {}
        if price_min is not None:
            price_q["$gte"] = price_min
        if price_max is not None:
            price_q["$lte"] = price_max
        query["prices.basic_lease"] = price_q

    sort_field = "created_at"
    sort_dir = -1
    if sort_by == "price_low":
        sort_field = "prices.basic_lease"
        sort_dir = 1
    elif sort_by == "price_high":
        sort_field = "prices.basic_lease"
        sort_dir = -1
    elif sort_by == "bpm_low":
        sort_field = "bpm"
        sort_dir = 1
    elif sort_by == "bpm_high":
        sort_field = "bpm"
        sort_dir = -1

    beats = await db.beats.find(query, {"_id": 0}).sort(sort_field, sort_dir).limit(limit).to_list(limit)
    total = await db.beats.count_documents(query)
    return {"beats": beats, "total": total}


@beats_router.get("/{beat_id}")
async def get_beat(beat_id: str):
    beat = await db.beats.find_one({"id": beat_id}, {"_id": 0})
    if not beat:
        raise HTTPException(status_code=404, detail="Beat not found")
    return beat


@beats_router.post("")
async def create_beat(beat: BeatCreate, request: Request):
    user = await require_admin(request)
    beat_id = f"beat_{uuid.uuid4().hex[:12]}"
    beat_doc = {
        "id": beat_id,
        "title": beat.title,
        "genre": beat.genre,
        "bpm": beat.bpm,
        "key": beat.key,
        "mood": beat.mood,
        "tags": beat.tags,
        "prices": {
            "basic_lease": beat.price_basic,
            "premium_lease": beat.price_premium,
            "unlimited_lease": beat.price_unlimited,
            "exclusive": beat.price_exclusive,
        },
        "audio_url": None,
        "preview_url": None,
        "cover_url": None,
        "duration": None,
        "status": "active",
        "plays": 0,
        "created_by": user["id"],
        "created_at": datetime.now(timezone.utc).isoformat(),
        "updated_at": datetime.now(timezone.utc).isoformat(),
    }
    await db.beats.insert_one(beat_doc)
    beat_doc.pop("_id", None)
    return beat_doc


@beats_router.post("/{beat_id}/audio")
async def upload_beat_audio(beat_id: str, request: Request, file: UploadFile = File(...)):
    await require_admin(request)
    beat = await db.beats.find_one({"id": beat_id})
    if not beat:
        raise HTTPException(status_code=404, detail="Beat not found")
    
    allowed = ["audio/mpeg", "audio/wav", "audio/mp3", "audio/x-wav", "audio/wave", "audio/x-m4a", "audio/mp4"]
    content_type = file.content_type or "audio/mpeg"
    if content_type not in allowed:
        raise HTTPException(status_code=400, detail=f"Unsupported audio type: {content_type}")
    
    ext = file.filename.split(".")[-1] if "." in file.filename else "mp3"
    file_id = uuid.uuid4().hex
    path = f"{APP_NAME}/beats/{beat_id}/{file_id}.{ext}"
    data = await file.read()
    
    # Upload original (clean) audio
    put_object(path, data, content_type)
    
    # Generate and upload watermarked preview
    preview_path = f"{APP_NAME}/beats/{beat_id}/{file_id}_preview.mp3"
    try:
        watermarked = _watermark_audio(data)
        put_object(preview_path, watermarked, "audio/mpeg")
        logger.info(f"Watermarked preview generated for beat {beat_id}")
    except Exception as e:
        logger.warning(f"Preview generation failed for {beat_id}: {e}")
        preview_path = path  # fallback to original
    
    await db.beats.update_one(
        {"id": beat_id},
        {"$set": {
            "audio_url": path,
            "preview_url": preview_path,
            "updated_at": datetime.now(timezone.utc).isoformat()
        }}
    )
    return {"audio_url": path, "preview_url": preview_path, "message": "Audio uploaded with watermarked preview"}


@beats_router.post("/{beat_id}/cover")
async def upload_beat_cover(beat_id: str, request: Request, file: UploadFile = File(...)):
    await require_admin(request)
    beat = await db.beats.find_one({"id": beat_id})
    if not beat:
        raise HTTPException(status_code=404, detail="Beat not found")
    
    ext = file.filename.split(".")[-1] if "." in file.filename else "jpg"
    path = f"{APP_NAME}/beats/{beat_id}/cover.{ext}"
    data = await file.read()
    content_type = file.content_type or "image/jpeg"
    
    put_object(path, data, content_type)
    
    await db.beats.update_one(
        {"id": beat_id},
        {"$set": {"cover_url": path, "updated_at": datetime.now(timezone.utc).isoformat()}}
    )
    return {"cover_url": path}


@beats_router.get("/{beat_id}/stream")
async def stream_beat(beat_id: str):
    beat = await db.beats.find_one({"id": beat_id}, {"_id": 0})
    if not beat or not beat.get("audio_url"):
        raise HTTPException(status_code=404, detail="Audio not found")
    
    from fastapi.responses import StreamingResponse
    # Serve watermarked preview if available, otherwise original
    stream_url = beat.get("preview_url") or beat["audio_url"]
    data, content_type = get_object(stream_url)
    
    # Increment play count
    await db.beats.update_one({"id": beat_id}, {"$inc": {"plays": 1}})
    
    return StreamingResponse(BytesIO(data), media_type=content_type, headers={
        "Content-Disposition": f'inline; filename="{beat.get("title", "beat")}_preview.mp3"',
        "Accept-Ranges": "bytes"
    })


@beats_router.put("/{beat_id}")
async def update_beat(beat_id: str, update: dict, request: Request):
    await require_admin(request)
    beat = await db.beats.find_one({"id": beat_id})
    if not beat:
        raise HTTPException(status_code=404, detail="Beat not found")
    
    allowed_fields = {"title", "genre", "bpm", "key", "mood", "tags", "prices", "status", "duration"}
    update_data = {k: v for k, v in update.items() if k in allowed_fields}
    update_data["updated_at"] = datetime.now(timezone.utc).isoformat()
    
    await db.beats.update_one({"id": beat_id}, {"$set": update_data})
    updated = await db.beats.find_one({"id": beat_id}, {"_id": 0})
    return updated


@beats_router.delete("/{beat_id}")
async def delete_beat(beat_id: str, request: Request):
    await require_admin(request)
    result = await db.beats.delete_one({"id": beat_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Beat not found")
    return {"message": "Beat deleted"}


@beats_router.post("/{beat_id}/watermark")
async def regenerate_watermark(beat_id: str, request: Request):
    """Admin: Regenerate watermarked preview for an existing beat"""
    await require_admin(request)
    beat = await db.beats.find_one({"id": beat_id}, {"_id": 0})
    if not beat or not beat.get("audio_url"):
        raise HTTPException(status_code=404, detail="Beat audio not found")
    data, _ = get_object(beat["audio_url"])
    preview_path = beat["audio_url"].rsplit(".", 1)[0] + "_preview.mp3"
    watermarked = _watermark_audio(data)
    put_object(preview_path, watermarked, "audio/mpeg")
    await db.beats.update_one(
        {"id": beat_id},
        {"$set": {"preview_url": preview_path, "updated_at": datetime.now(timezone.utc).isoformat()}}
    )
    return {"preview_url": preview_path, "message": "Watermark preview regenerated"}
