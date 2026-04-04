"""In-App Messaging Routes — Conversations, Messages, File sharing, Typing indicators"""
from fastapi import APIRouter, HTTPException, Request, UploadFile, File
from fastapi.responses import StreamingResponse
from datetime import datetime, timezone, timedelta
from io import BytesIO
import uuid
import logging

from core import db, get_current_user, put_object, get_object, APP_NAME

logger = logging.getLogger(__name__)
messages_router = APIRouter(prefix="/api")


@messages_router.get("/messages/conversations")
async def list_conversations(request: Request):
    """List all conversations for the current user (only from accepted collab invites)"""
    user = await get_current_user(request)
    uid = user["id"]
    convos = await db.conversations.find(
        {"participants": uid}, {"_id": 0}
    ).sort("updated_at", -1).to_list(50)
    for c in convos:
        last_msg = await db.messages.find_one(
            {"conversation_id": c["id"]}, {"_id": 0},
            sort=[("created_at", -1)]
        )
        c["last_message"] = last_msg
        unread = await db.messages.count_documents(
            {"conversation_id": c["id"], "sender_id": {"$ne": uid}, "read": False}
        )
        c["unread_count"] = unread
        other_id = [p for p in c["participants"] if p != uid]
        if other_id:
            other_user = await db.users.find_one({"id": other_id[0]}, {"_id": 0, "artist_name": 1, "name": 1, "email": 1})
            c["other_user"] = {"artist_name": (other_user or {}).get("artist_name") or (other_user or {}).get("name", "Unknown"), "email": (other_user or {}).get("email", "")}
        else:
            c["other_user"] = {"artist_name": "Unknown", "email": ""}
    return convos


@messages_router.get("/messages/unread/count")
async def unread_message_count(request: Request):
    """Get total unread message count for the current user"""
    user = await get_current_user(request)
    convos = await db.conversations.find({"participants": user["id"]}, {"id": 1, "_id": 0}).to_list(100)
    convo_ids = [c["id"] for c in convos]
    if not convo_ids:
        return {"unread": 0}
    count = await db.messages.count_documents(
        {"conversation_id": {"$in": convo_ids}, "sender_id": {"$ne": user["id"]}, "read": False}
    )
    return {"unread": count}


@messages_router.get("/messages/{conversation_id}")
async def get_messages(conversation_id: str, request: Request):
    """Get messages for a conversation (only if user is a participant)"""
    user = await get_current_user(request)
    convo = await db.conversations.find_one({"id": conversation_id, "participants": user["id"]})
    if not convo:
        raise HTTPException(status_code=404, detail="Conversation not found")
    messages = await db.messages.find(
        {"conversation_id": conversation_id}, {"_id": 0}
    ).sort("created_at", 1).to_list(200)
    now = datetime.now(timezone.utc).isoformat()
    await db.messages.update_many(
        {"conversation_id": conversation_id, "sender_id": {"$ne": user["id"]}, "read": False},
        {"$set": {"read": True, "read_at": now}}
    )
    for m in messages:
        if m.get("sender_id") != user["id"] and not m.get("read"):
            m["read"] = True
            m["read_at"] = now
    typing_users = []
    cutoff = (datetime.now(timezone.utc) - timedelta(seconds=4)).isoformat()
    other_ids = [p for p in convo["participants"] if p != user["id"]]
    for oid in other_ids:
        ts = await db.typing_status.find_one({"conversation_id": conversation_id, "user_id": oid, "timestamp": {"$gt": cutoff}})
        if ts:
            typing_users.append(oid)
    return {"messages": messages, "typing": typing_users}


@messages_router.post("/messages/{conversation_id}")
async def send_message(conversation_id: str, request: Request):
    """Send a message in a conversation (only if user is a participant)"""
    user = await get_current_user(request)
    convo = await db.conversations.find_one({"id": conversation_id, "participants": user["id"]})
    if not convo:
        raise HTTPException(status_code=404, detail="Conversation not found")
    body = await request.json()
    text = body.get("text", "").strip()
    if not text:
        raise HTTPException(status_code=400, detail="Message cannot be empty")
    msg = {
        "id": f"msg_{uuid.uuid4().hex[:12]}",
        "conversation_id": conversation_id,
        "sender_id": user["id"],
        "sender_name": user.get("artist_name") or user.get("name", ""),
        "text": text,
        "read": False,
        "created_at": datetime.now(timezone.utc).isoformat(),
    }
    await db.messages.insert_one(msg)
    msg.pop("_id", None)
    await db.conversations.update_one(
        {"id": conversation_id},
        {"$set": {"updated_at": datetime.now(timezone.utc).isoformat()}}
    )
    other_ids = [p for p in convo["participants"] if p != user["id"]]
    for oid in other_ids:
        await db.notifications.insert_one({
            "id": f"notif_{uuid.uuid4().hex[:12]}", "user_id": oid,
            "type": "new_message",
            "message": f"New message from {user.get('artist_name', 'Someone')}",
            "read": False, "created_at": datetime.now(timezone.utc).isoformat(),
        })
    return msg


@messages_router.post("/messages/{conversation_id}/upload")
async def upload_chat_file(conversation_id: str, request: Request, file: UploadFile = File(...)):
    """Upload a file/audio in a chat conversation"""
    user = await get_current_user(request)
    convo = await db.conversations.find_one({"id": conversation_id, "participants": user["id"]})
    if not convo:
        raise HTTPException(status_code=404, detail="Conversation not found")
    content = await file.read()
    max_size = 50 * 1024 * 1024
    if len(content) > max_size:
        raise HTTPException(status_code=400, detail="File too large. Max 50MB.")
    ext = file.filename.split(".")[-1].lower() if "." in file.filename else "bin"
    ct = file.content_type or "application/octet-stream"
    file_type = "audio" if ct.startswith("audio/") else "image" if ct.startswith("image/") else "file"
    path = f"{APP_NAME}/chat/{conversation_id}/{uuid.uuid4().hex[:12]}.{ext}"
    result = put_object(path, content, ct)
    file_url = result.get("path") or result.get("url") or path
    msg = {
        "id": f"msg_{uuid.uuid4().hex[:12]}",
        "conversation_id": conversation_id,
        "sender_id": user["id"],
        "sender_name": user.get("artist_name") or user.get("name", ""),
        "text": file.filename,
        "file_url": file_url,
        "file_name": file.filename,
        "file_type": file_type,
        "file_size": len(content),
        "read": False,
        "created_at": datetime.now(timezone.utc).isoformat(),
    }
    await db.messages.insert_one(msg)
    msg.pop("_id", None)
    await db.conversations.update_one(
        {"id": conversation_id},
        {"$set": {"updated_at": datetime.now(timezone.utc).isoformat()}}
    )
    other_ids = [p for p in convo["participants"] if p != user["id"]]
    for oid in other_ids:
        await db.notifications.insert_one({
            "id": f"notif_{uuid.uuid4().hex[:12]}", "user_id": oid,
            "type": "new_message",
            "message": f"{user.get('artist_name', 'Someone')} shared a file",
            "read": False, "created_at": datetime.now(timezone.utc).isoformat(),
        })
    return msg


@messages_router.get("/messages/file/{file_path:path}")
async def get_chat_file(file_path: str, request: Request):
    """Download a chat file (validates user is a participant)"""
    user = await get_current_user(request)
    parts = file_path.split("/")
    convo_id = None
    for i, p in enumerate(parts):
        if p == "chat" and i + 1 < len(parts):
            convo_id = parts[i + 1]
            break
    if convo_id:
        convo = await db.conversations.find_one({"id": convo_id, "participants": user["id"]})
        if not convo:
            raise HTTPException(status_code=403, detail="Access denied")
    data, content_type = get_object(file_path)
    fname = parts[-1] if parts else "file"
    return StreamingResponse(BytesIO(data), media_type=content_type,
        headers={"Content-Disposition": f'inline; filename="{fname}"'})


@messages_router.post("/messages/{conversation_id}/typing")
async def set_typing(conversation_id: str, request: Request):
    """Signal that the user is typing in a conversation"""
    user = await get_current_user(request)
    convo = await db.conversations.find_one({"id": conversation_id, "participants": user["id"]})
    if not convo:
        raise HTTPException(status_code=404, detail="Conversation not found")
    await db.typing_status.update_one(
        {"conversation_id": conversation_id, "user_id": user["id"]},
        {"$set": {"timestamp": datetime.now(timezone.utc).isoformat()}},
        upsert=True
    )
    return {"ok": True}
