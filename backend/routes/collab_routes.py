"""Collaboration routes — Invite collaborators, manage splits, accept/decline invitations"""
from fastapi import APIRouter, HTTPException, Request
from datetime import datetime, timezone
from typing import Optional
from pydantic import BaseModel, EmailStr
import uuid
import logging

from core import db, get_current_user

logger = logging.getLogger(__name__)
collab_router = APIRouter(prefix="/api")


class CollaborationInvite(BaseModel):
    release_id: str
    collaborator_email: str
    collaborator_name: str
    role: str = "Featured Artist"
    split_percentage: float = 0.0


class SplitUpdate(BaseModel):
    split_percentage: float


@collab_router.post("/collaborations/invite")
async def invite_collaborator(data: CollaborationInvite, request: Request):
    user = await get_current_user(request)
    release = await db.releases.find_one({"id": data.release_id, "artist_id": user["id"]}, {"_id": 0})
    if not release:
        raise HTTPException(status_code=404, detail="Release not found or not owned by you")
    if data.collaborator_email == user["email"]:
        raise HTTPException(status_code=400, detail="Cannot invite yourself")
    existing = await db.collaborations.find_one({
        "release_id": data.release_id,
        "collaborator_email": data.collaborator_email,
        "status": {"$ne": "declined"}
    })
    if existing:
        raise HTTPException(status_code=400, detail="Collaborator already invited for this release")
    # Check total splits don't exceed 100%
    existing_collabs = await db.collaborations.find({
        "release_id": data.release_id, "status": {"$in": ["pending", "accepted"]}
    }, {"_id": 0}).to_list(50)
    total_split = sum(c.get("split_percentage", 0) for c in existing_collabs)
    if total_split + data.split_percentage > 100:
        raise HTTPException(status_code=400, detail=f"Total splits would exceed 100% (current: {total_split}%)")

    now = datetime.now(timezone.utc).isoformat()
    collab_id = f"collab_{uuid.uuid4().hex[:12]}"
    collab_doc = {
        "id": collab_id,
        "release_id": data.release_id,
        "release_title": release.get("title", ""),
        "owner_id": user["id"],
        "owner_name": user.get("artist_name") or user.get("name", ""),
        "owner_email": user["email"],
        "collaborator_email": data.collaborator_email,
        "collaborator_name": data.collaborator_name,
        "collaborator_id": None,
        "role": data.role,
        "split_percentage": data.split_percentage,
        "status": "pending",
        "created_at": now,
        "updated_at": now,
    }
    await db.collaborations.insert_one(collab_doc)
    # Create notification for collaborator if they have an account
    collab_user = await db.users.find_one({"email": data.collaborator_email}, {"_id": 0, "id": 1})
    if collab_user:
        await db.notifications.insert_one({
            "id": f"notif_{uuid.uuid4().hex[:12]}",
            "user_id": collab_user["id"],
            "type": "collaboration_invite",
            "message": f"{user.get('artist_name', user.get('name', 'An artist'))} invited you to collaborate on \"{release.get('title', 'a release')}\" as {data.role} ({data.split_percentage}% split)",
            "metadata": {"collaboration_id": collab_id, "release_id": data.release_id},
            "read": False,
            "action_url": "/collaborations",
            "created_at": now,
        })
    # Send invitation email
    try:
        from routes.email_routes import send_email
        import os
        frontend_url = os.environ.get("FRONTEND_URL", "")
        await send_email(data.collaborator_email, f"Collaboration Invite: {release.get('title', '')}",
            f"""<div style="font-family:Arial;max-width:600px;margin:0 auto;background:#000;color:#fff;border-radius:16px;overflow:hidden;">
            <div style="background:linear-gradient(90deg,#7C4DFF,#E040FB);padding:30px;text-align:center;">
            <h1 style="color:white;margin:0;font-size:22px;">Collaboration Invite</h1></div>
            <div style="padding:30px;">
            <p>Hi {data.collaborator_name},</p>
            <p><strong>{user.get('artist_name', user.get('name', 'An artist'))}</strong> has invited you to collaborate on
            <strong>"{release.get('title', '')}"</strong> as <strong>{data.role}</strong> with a <strong>{data.split_percentage}%</strong> royalty split.</p>
            <div style="text-align:center;margin:30px 0;">
            <a href="{frontend_url}/collaborations" style="background:#7C4DFF;color:white;padding:14px 32px;border-radius:8px;text-decoration:none;font-weight:bold;">View Invitation</a></div>
            </div></div>""")
    except Exception as e:
        logger.warning(f"Collab invite email failed: {e}")

    collab_doc.pop("_id", None)
    return {"message": "Invitation sent", "collaboration": collab_doc}


@collab_router.get("/collaborations")
async def get_collaborations(request: Request):
    user = await get_current_user(request)
    # Get collaborations where user is owner or collaborator
    owned = await db.collaborations.find({"owner_id": user["id"]}, {"_id": 0}).sort("created_at", -1).to_list(100)
    collab_on = await db.collaborations.find({
        "$or": [{"collaborator_email": user["email"]}, {"collaborator_id": user["id"]}]
    }, {"_id": 0}).sort("created_at", -1).to_list(100)
    return {"owned": owned, "collaborating_on": collab_on}


@collab_router.get("/collaborations/invitations")
async def get_pending_invitations(request: Request):
    user = await get_current_user(request)
    invitations = await db.collaborations.find({
        "collaborator_email": user["email"], "status": "pending"
    }, {"_id": 0}).sort("created_at", -1).to_list(50)
    return {"invitations": invitations}


@collab_router.put("/collaborations/{collab_id}/accept")
async def accept_invitation(collab_id: str, request: Request):
    user = await get_current_user(request)
    collab = await db.collaborations.find_one({"id": collab_id, "collaborator_email": user["email"]}, {"_id": 0})
    if not collab:
        raise HTTPException(status_code=404, detail="Invitation not found")
    if collab["status"] != "pending":
        raise HTTPException(status_code=400, detail=f"Invitation is already {collab['status']}")
    now = datetime.now(timezone.utc).isoformat()
    await db.collaborations.update_one({"id": collab_id}, {"$set": {
        "status": "accepted", "collaborator_id": user["id"], "updated_at": now
    }})
    # Notify owner
    await db.notifications.insert_one({
        "id": f"notif_{uuid.uuid4().hex[:12]}",
        "user_id": collab["owner_id"],
        "type": "collaboration_accepted",
        "message": f"{user.get('artist_name', user.get('name', 'A collaborator'))} accepted your collaboration invite for \"{collab.get('release_title', '')}\"",
        "read": False, "action_url": "/collaborations", "created_at": now,
    })
    return {"message": "Invitation accepted"}


@collab_router.put("/collaborations/{collab_id}/decline")
async def decline_invitation(collab_id: str, request: Request):
    user = await get_current_user(request)
    collab = await db.collaborations.find_one({"id": collab_id, "collaborator_email": user["email"]}, {"_id": 0})
    if not collab:
        raise HTTPException(status_code=404, detail="Invitation not found")
    if collab["status"] != "pending":
        raise HTTPException(status_code=400, detail=f"Invitation is already {collab['status']}")
    now = datetime.now(timezone.utc).isoformat()
    await db.collaborations.update_one({"id": collab_id}, {"$set": {"status": "declined", "updated_at": now}})
    # Notify owner
    await db.notifications.insert_one({
        "id": f"notif_{uuid.uuid4().hex[:12]}",
        "user_id": collab["owner_id"],
        "type": "collaboration_declined",
        "message": f"{user.get('artist_name', user.get('name', 'A collaborator'))} declined your collaboration invite for \"{collab.get('release_title', '')}\"",
        "read": False, "action_url": "/collaborations", "created_at": now,
    })
    return {"message": "Invitation declined"}


@collab_router.put("/collaborations/{collab_id}/split")
async def update_split(collab_id: str, data: SplitUpdate, request: Request):
    user = await get_current_user(request)
    collab = await db.collaborations.find_one({"id": collab_id}, {"_id": 0})
    if not collab:
        raise HTTPException(status_code=404, detail="Collaboration not found")
    if collab["owner_id"] != user["id"]:
        raise HTTPException(status_code=403, detail="Only the release owner can update splits")
    # Check total splits
    other_collabs = await db.collaborations.find({
        "release_id": collab["release_id"], "status": {"$in": ["pending", "accepted"]}, "id": {"$ne": collab_id}
    }, {"_id": 0}).to_list(50)
    total_split = sum(c.get("split_percentage", 0) for c in other_collabs)
    if total_split + data.split_percentage > 100:
        raise HTTPException(status_code=400, detail=f"Total splits would exceed 100% (other: {total_split}%)")
    await db.collaborations.update_one({"id": collab_id}, {"$set": {
        "split_percentage": data.split_percentage, "updated_at": datetime.now(timezone.utc).isoformat()
    }})
    return {"message": "Split updated"}


@collab_router.delete("/collaborations/{collab_id}")
async def remove_collaborator(collab_id: str, request: Request):
    user = await get_current_user(request)
    collab = await db.collaborations.find_one({"id": collab_id}, {"_id": 0})
    if not collab:
        raise HTTPException(status_code=404, detail="Collaboration not found")
    if collab["owner_id"] != user["id"] and collab.get("collaborator_email") != user["email"]:
        raise HTTPException(status_code=403, detail="Not authorized")
    await db.collaborations.delete_one({"id": collab_id})
    return {"message": "Collaboration removed"}


@collab_router.get("/collaborations/release/{release_id}")
async def get_release_collaborators(release_id: str, request: Request):
    user = await get_current_user(request)
    collabs = await db.collaborations.find({
        "release_id": release_id, "status": {"$in": ["pending", "accepted"]}
    }, {"_id": 0}).to_list(50)
    total_split = sum(c.get("split_percentage", 0) for c in collabs)
    owner_split = 100 - total_split
    return {"collaborators": collabs, "total_split": total_split, "owner_split": owner_split}
