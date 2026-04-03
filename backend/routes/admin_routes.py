"""Admin Routes - Dashboard, Users, Analytics, Royalty Import, Templates, Reconciliation"""
from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import Optional
from datetime import datetime, timezone, timedelta
from difflib import SequenceMatcher
import os
import uuid
import logging
import csv as csv_module
import io

from core import db, require_admin, AdminUserUpdate, AdminReviewAction

logger = logging.getLogger(__name__)

admin_router = APIRouter(prefix="/api/admin")

DEFAULT_PER_STREAM_RATE = 0.004  # $0.004 per stream (industry average)


# ============= MODELS =============

class AdminProfileUpdate(BaseModel):
    name: Optional[str] = None
    artist_name: Optional[str] = None
    bio: Optional[str] = None
    genre: Optional[str] = None
    country: Optional[str] = None
    website: Optional[str] = None
    spotify_url: Optional[str] = None
    apple_music_url: Optional[str] = None
    instagram: Optional[str] = None
    twitter: Optional[str] = None
    role: Optional[str] = None
    plan: Optional[str] = None
    status: Optional[str] = None

class AssignEntryInput(BaseModel):
    artist_id: str

class DistributorTemplateInput(BaseModel):
    name: str
    column_mapping: dict
    notes: Optional[str] = ""


# ============= HELPERS =============

COMMON_CSV_COLUMNS = {
    "artist": ["artist", "artist name", "artist_name", "performer", "primary artist"],
    "track": ["track", "track name", "track_name", "title", "song", "song title", "song_title"],
    "platform": ["platform", "store", "store name", "dsp", "service", "streaming service"],
    "country": ["country", "territory", "region", "market", "country/territory"],
    "streams": ["streams", "quantity", "plays", "units", "stream count", "total streams"],
    "revenue": ["revenue", "earnings", "royalties", "amount", "net revenue", "total revenue", "payout", "total"],
    "period": ["period", "date", "month", "reporting period", "sale month", "statement period", "reporting_period"],
}

def detect_columns(headers: list) -> dict:
    mapping = {}
    headers_lower = [h.strip().lower() for h in headers]
    for field, aliases in COMMON_CSV_COLUMNS.items():
        for alias in aliases:
            for i, h in enumerate(headers_lower):
                if alias == h or alias in h:
                    mapping[field] = i
                    break
            if field in mapping:
                break
    return mapping

def fuzzy_match_artist(name: str, roster_names: dict, threshold: float = 0.7) -> str:
    name_lower = name.strip().lower()
    best_match = None
    best_score = 0
    for artist_id, artist_name in roster_names.items():
        score = SequenceMatcher(None, name_lower, artist_name.lower()).ratio()
        if score > best_score and score >= threshold:
            best_score = score
            best_match = artist_id
    return best_match


# ============= DASHBOARD =============

@admin_router.get("/dashboard")
async def admin_dashboard(request: Request):
    await require_admin(request)
    total_users = await db.users.count_documents({})
    total_releases = await db.releases.count_documents({})
    total_tracks = await db.tracks.count_documents({})
    pending = await db.submissions.count_documents({"status": "pending_review"})
    approved = await db.submissions.count_documents({"status": "approved"})
    rejected = await db.submissions.count_documents({"status": "rejected"})
    pipeline = [{"$group": {"_id": None, "total": {"$sum": "$amount"}}}]
    rev = await db.payment_transactions.aggregate(pipeline).to_list(1)
    plan_pipeline = [{"$group": {"_id": "$plan", "count": {"$sum": 1}}}]
    plan_result = await db.users.aggregate(plan_pipeline).to_list(10)
    week_ago = (datetime.now(timezone.utc) - timedelta(days=7)).isoformat()
    return {"total_users": total_users, "total_releases": total_releases, "total_tracks": total_tracks,
        "pending_submissions": pending, "approved_submissions": approved, "rejected_submissions": rejected,
        "total_revenue": round(rev[0]["total"] if rev else 0, 2),
        "users_by_plan": {r["_id"]: r["count"] for r in plan_result},
        "new_users_week": await db.users.count_documents({"created_at": {"$gte": week_ago}}),
        "new_releases_week": await db.releases.count_documents({"created_at": {"$gte": week_ago}})}


# ============= SUBMISSIONS =============

@admin_router.get("/submissions")
async def get_submissions(request: Request, status: Optional[str] = None, page: int = 1, limit: int = 20):
    await require_admin(request)
    query = {"status": status} if status else {}
    skip = (page - 1) * limit
    total = await db.submissions.count_documents(query)
    subs = await db.submissions.find(query, {"_id": 0}).sort("submitted_at", -1).skip(skip).limit(limit).to_list(limit)
    return {"submissions": subs, "total": total, "page": page, "pages": (total + limit - 1) // limit}

@admin_router.get("/submissions/{release_id}")
async def get_submission_detail(release_id: str, request: Request):
    await require_admin(request)
    submission = await db.submissions.find_one({"release_id": release_id}, {"_id": 0})
    if not submission: raise HTTPException(status_code=404, detail="Submission not found")
    release = await db.releases.find_one({"id": release_id}, {"_id": 0})
    tracks = await db.tracks.find({"release_id": release_id}, {"_id": 0}).sort("track_number", 1).to_list(50)
    artist = await db.users.find_one({"id": submission["artist_id"]}, {"_id": 0, "password_hash": 0})
    return {"submission": submission, "release": release, "tracks": tracks, "artist": artist}

@admin_router.put("/submissions/{release_id}/review")
async def review_submission(release_id: str, review: AdminReviewAction, request: Request):
    admin = await require_admin(request)
    submission = await db.submissions.find_one({"release_id": release_id})
    if not submission: raise HTTPException(status_code=404, detail="Submission not found")
    if submission["status"] != "pending_review": raise HTTPException(status_code=400, detail="Submission already reviewed")
    new_status = "approved" if review.action == "approve" else "rejected"
    now = datetime.now(timezone.utc).isoformat()
    await db.submissions.update_one({"release_id": release_id},
        {"$set": {"status": new_status, "reviewed_at": now, "reviewed_by": admin["id"], "review_notes": review.notes}})
    if review.action == "approve":
        await db.releases.update_one({"id": release_id}, {"$set": {"status": "distributed"}})
        await db.distributions.update_many({"release_id": release_id}, {"$set": {"status": "live", "approved_at": now}})
        notify_msg = "Your release has been approved and is now live on all selected stores!"
    else:
        await db.releases.update_one({"id": release_id}, {"$set": {"status": "rejected", "rejection_reason": review.notes}})
        await db.distributions.update_many({"release_id": release_id}, {"$set": {"status": "rejected"}})
        notify_msg = f"Your release was not approved. Reason: {review.notes or 'Does not meet guidelines.'}"
    await db.notifications.insert_one({"id": f"notif_{uuid.uuid4().hex[:12]}", "user_id": submission["artist_id"],
        "type": "review_result", "message": notify_msg, "release_id": release_id, "read": False, "created_at": now})
    await db.admin_actions.insert_one({"id": f"act_{uuid.uuid4().hex[:12]}", "admin_id": admin["id"],
        "action": f"review_{review.action}", "target_type": "release", "target_id": release_id,
        "notes": review.notes, "created_at": now})
    return {"message": f"Submission {new_status}", "status": new_status}


# ============= USERS =============

@admin_router.get("/users")
async def admin_get_users(request: Request, page: int = 1, limit: int = 20, search: Optional[str] = None):
    await require_admin(request)
    query = {}
    if search:
        query["$or"] = [{"name": {"$regex": search, "$options": "i"}}, {"email": {"$regex": search, "$options": "i"}}, {"artist_name": {"$regex": search, "$options": "i"}}]
    skip = (page - 1) * limit
    total = await db.users.count_documents(query)
    users = await db.users.find(query, {"_id": 0, "password_hash": 0}).sort("created_at", -1).skip(skip).limit(limit).to_list(limit)
    for u in users: u["release_count"] = await db.releases.count_documents({"artist_id": u["id"]})
    return {"users": users, "total": total, "page": page, "pages": (total + limit - 1) // limit}

@admin_router.put("/users/{user_id}")
async def admin_update_user(user_id: str, update: AdminUserUpdate, request: Request):
    admin = await require_admin(request)
    user = await db.users.find_one({"id": user_id})
    if not user: raise HTTPException(status_code=404, detail="User not found")
    update_doc = {}
    if update.role: update_doc["role"] = update.role
    if update.plan: update_doc["plan"] = update.plan
    if update.status: update_doc["status"] = update.status
    if update_doc:
        update_doc["updated_at"] = datetime.now(timezone.utc).isoformat()
        await db.users.update_one({"id": user_id}, {"$set": update_doc})
    await db.admin_actions.insert_one({"id": f"act_{uuid.uuid4().hex[:12]}", "admin_id": admin["id"],
        "action": "update_user", "target_type": "user", "target_id": user_id,
        "notes": str(update_doc), "created_at": datetime.now(timezone.utc).isoformat()})
    return {"message": "User updated"}

@admin_router.get("/users/{user_id}/detail")
async def admin_get_user_detail(user_id: str, request: Request):
    await require_admin(request)
    user = await db.users.find_one({"id": user_id}, {"_id": 0, "password_hash": 0})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    profile = await db.artist_profiles.find_one({"user_id": user_id}, {"_id": 0}) or {}
    releases = await db.releases.find(
        {"artist_id": user_id}, {"_id": 0, "id": 1, "title": 1, "release_type": 1, "genre": 1, "status": 1, "created_at": 1, "track_count": 1, "cover_art_url": 1}
    ).sort("created_at", -1).to_list(50)
    total_streams_result = await db.stream_events.aggregate([
        {"$match": {"artist_id": user_id}}, {"$group": {"_id": None, "total": {"$sum": 1}}}
    ]).to_list(1)
    total_streams = total_streams_result[0]["total"] if total_streams_result else 0
    rev_result = await db.stream_events.aggregate([
        {"$match": {"artist_id": user_id, "revenue": {"$exists": True}}},
        {"$group": {"_id": None, "total": {"$sum": "$revenue"}}}
    ]).to_list(1)
    total_revenue = round(rev_result[0]["total"] if rev_result else 0, 2)
    platform_breakdown = await db.stream_events.aggregate([
        {"$match": {"artist_id": user_id}},
        {"$group": {"_id": "$platform", "count": {"$sum": 1}, "revenue": {"$sum": {"$ifNull": ["$revenue", 0]}}}},
        {"$sort": {"count": -1}}, {"$limit": 10}
    ]).to_list(10)
    country_breakdown = await db.stream_events.aggregate([
        {"$match": {"artist_id": user_id}},
        {"$group": {"_id": "$country", "count": {"$sum": 1}}},
        {"$sort": {"count": -1}}, {"$limit": 10}
    ]).to_list(10)
    weekly_trends = []
    now = datetime.now(timezone.utc)
    for w in range(8):
        end = now - timedelta(weeks=w)
        start = end - timedelta(weeks=1)
        count = await db.stream_events.count_documents({
            "artist_id": user_id, "timestamp": {"$gte": start.isoformat(), "$lt": end.isoformat()}
        })
        weekly_trends.append({"week": f"W-{w}", "streams": count})
    weekly_trends.reverse()
    goals = await db.goals.find({"user_id": user_id}, {"_id": 0}).sort("created_at", -1).to_list(20)
    collab_count = await db.collaborations.count_documents({"$or": [{"from_user_id": user_id}, {"to_user_id": user_id}]})
    presave_count = await db.presave_campaigns.count_documents({"artist_id": user_id})
    presave_subs = await db.presave_campaigns.aggregate([
        {"$match": {"artist_id": user_id}}, {"$group": {"_id": None, "total": {"$sum": "$subscriber_count"}}}
    ]).to_list(1)
    return {
        "user": {**user, **{k: profile.get(k) for k in ["bio", "genre", "country", "website", "spotify_url", "apple_music_url", "instagram", "twitter", "slug"] if profile.get(k)}},
        "stats": {
            "total_streams": total_streams, "total_revenue": total_revenue,
            "total_releases": len(releases),
            "total_tracks": sum(r.get("track_count", 0) for r in releases),
            "collaborations": collab_count, "presave_campaigns": presave_count,
            "presave_subscribers": presave_subs[0]["total"] if presave_subs else 0,
            "goals_active": len([g for g in goals if g.get("status") == "active"]),
            "goals_completed": len([g for g in goals if g.get("status") == "completed"]),
        },
        "releases": releases,
        "platform_breakdown": [{"platform": p["_id"], "streams": p["count"], "revenue": round(p.get("revenue", 0), 2)} for p in platform_breakdown],
        "country_breakdown": [{"country": c["_id"], "streams": c["count"]} for c in country_breakdown],
        "weekly_trends": weekly_trends, "goals": goals[:10],
    }

@admin_router.put("/users/{user_id}/profile")
async def admin_update_user_profile(user_id: str, update: AdminProfileUpdate, request: Request):
    admin = await require_admin(request)
    user = await db.users.find_one({"id": user_id})
    if not user: raise HTTPException(status_code=404, detail="User not found")
    now = datetime.now(timezone.utc).isoformat()
    user_updates = {}
    profile_updates = {}
    for field in ["name", "artist_name", "role", "plan", "status"]:
        val = getattr(update, field, None)
        if val is not None: user_updates[field] = val
    for field in ["bio", "genre", "country", "website", "spotify_url", "apple_music_url", "instagram", "twitter"]:
        val = getattr(update, field, None)
        if val is not None: profile_updates[field] = val
    if user_updates:
        user_updates["updated_at"] = now
        await db.users.update_one({"id": user_id}, {"$set": user_updates})
    if profile_updates:
        profile_updates["updated_at"] = now
        profile_updates["artist_name"] = update.artist_name or user.get("artist_name", "")
        await db.artist_profiles.update_one({"user_id": user_id}, {"$set": profile_updates}, upsert=True)
    await db.admin_actions.insert_one({
        "id": f"act_{uuid.uuid4().hex[:12]}", "admin_id": admin["id"],
        "action": "update_profile", "target_type": "user", "target_id": user_id,
        "notes": str({**user_updates, **profile_updates}), "created_at": now
    })
    return {"message": "Profile updated successfully"}


# ============= PLATFORM ANALYTICS =============

@admin_router.get("/analytics")
async def admin_platform_analytics(request: Request):
    await require_admin(request)
    now = datetime.now(timezone.utc)
    week_ago = (now - timedelta(days=7)).isoformat()
    month_ago = (now - timedelta(days=30)).isoformat()
    total_streams_result = await db.stream_events.aggregate([{"$group": {"_id": None, "total": {"$sum": 1}}}]).to_list(1)
    total_streams = total_streams_result[0]["total"] if total_streams_result else 0
    week_streams = await db.stream_events.count_documents({"timestamp": {"$gte": week_ago}})
    rev_result = await db.stream_events.aggregate([
        {"$match": {"revenue": {"$exists": True}}}, {"$group": {"_id": None, "total": {"$sum": "$revenue"}}}
    ]).to_list(1)
    total_stream_rev = round(rev_result[0]["total"] if rev_result else 0, 2)
    platform_breakdown = await db.stream_events.aggregate([
        {"$group": {"_id": "$platform", "count": {"$sum": 1}, "revenue": {"$sum": {"$ifNull": ["$revenue", 0]}}}},
        {"$sort": {"count": -1}}, {"$limit": 10}
    ]).to_list(10)
    country_breakdown = await db.stream_events.aggregate([
        {"$group": {"_id": "$country", "count": {"$sum": 1}}}, {"$sort": {"count": -1}}, {"$limit": 10}
    ]).to_list(10)
    top_artists_raw = await db.stream_events.aggregate([
        {"$group": {"_id": "$artist_id", "streams": {"$sum": 1}, "revenue": {"$sum": {"$ifNull": ["$revenue", 0]}}}},
        {"$sort": {"streams": -1}}, {"$limit": 10}
    ]).to_list(10)
    top_artists = []
    for a in top_artists_raw:
        user = await db.users.find_one({"id": a["_id"]}, {"_id": 0, "id": 1, "name": 1, "artist_name": 1, "plan": 1, "avatar_url": 1})
        if user: top_artists.append({**user, "streams": a["streams"], "revenue": round(a.get("revenue", 0), 2)})
    monthly_trend = []
    for m in range(6):
        end = now.replace(day=1) - timedelta(days=30 * m)
        start = end - timedelta(days=30)
        count = await db.stream_events.count_documents({"timestamp": {"$gte": start.isoformat(), "$lt": end.isoformat()}})
        monthly_trend.append({"month": end.strftime("%b %Y"), "streams": count})
    monthly_trend.reverse()
    active_artists_result = await db.stream_events.aggregate([
        {"$match": {"timestamp": {"$gte": month_ago}}}, {"$group": {"_id": "$artist_id"}}, {"$count": "total"}
    ]).to_list(1)
    return {
        "total_streams": total_streams, "week_streams": week_streams,
        "total_stream_revenue": total_stream_rev,
        "platform_breakdown": [{"platform": p["_id"], "streams": p["count"], "revenue": round(p.get("revenue", 0), 2)} for p in platform_breakdown],
        "country_breakdown": [{"country": c["_id"], "streams": c["count"]} for c in country_breakdown],
        "top_artists": top_artists, "monthly_trend": monthly_trend,
        "active_artists": active_artists_result[0]["total"] if active_artists_result else 0,
    }


# ============= FILE PARSERS =============

def parse_csv_to_rows(content: bytes):
    """Parse CSV bytes into header + data rows"""
    try:
        text = content.decode("utf-8-sig")
    except:
        text = content.decode("latin-1")
    reader = csv_module.reader(io.StringIO(text))
    rows = list(reader)
    if len(rows) < 2:
        raise HTTPException(status_code=400, detail="CSV must have a header row and at least one data row")
    return rows[0], rows[1:]

def parse_xlsx_to_rows(content: bytes):
    """Parse Excel bytes into header + data rows"""
    import openpyxl
    wb = openpyxl.load_workbook(io.BytesIO(content), data_only=True)
    ws = wb.active
    all_rows = []
    for row in ws.iter_rows(values_only=True):
        all_rows.append([str(cell) if cell is not None else "" for cell in row])
    if len(all_rows) < 2:
        raise HTTPException(status_code=400, detail="Excel file must have a header row and at least one data row")
    return all_rows[0], all_rows[1:]

def parse_pdf_to_rows(content: bytes):
    """Parse PDF bytes — extract tables from all pages"""
    import pdfplumber
    pdf = pdfplumber.open(io.BytesIO(content))
    all_tables = []
    for page in pdf.pages:
        tables = page.extract_tables()
        for table in tables:
            if table and len(table) >= 2:
                all_tables.extend(table)
    pdf.close()
    if not all_tables or len(all_tables) < 2:
        raise HTTPException(status_code=400, detail="Could not extract table data from PDF. Make sure the PDF contains tabular data.")
    headers = [str(cell).strip() if cell else "" for cell in all_tables[0]]
    data = []
    for row in all_tables[1:]:
        data.append([str(cell).strip() if cell else "" for cell in row])
    return headers, data

def detect_file_format(rows_header: list, data_rows: list):
    """Detect if this is a standard multi-artist report or a single-artist retail/platform report"""
    headers_lower = [h.strip().lower() for h in rows_header]
    # Check for standard format (has artist column)
    artist_aliases = ["artist", "artist name", "artist_name", "performer", "primary artist"]
    has_artist = any(a in h for h in headers_lower for a in artist_aliases)

    # Check for retail/platform daily format (Zojak Evolution style): Retail, date1, date2, ...
    is_retail_daily = ("retail" in headers_lower or "platform" in headers_lower) and len(rows_header) > 3

    # Check for retail ranking format: retail, proportion, streams
    is_retail_ranking = ("retail" in headers_lower or "platform" in headers_lower) and any(
        w in headers_lower for w in ["streams", "proportion", "plays", "units"]
    )

    if has_artist:
        return "standard"
    elif is_retail_daily:
        return "retail_daily"
    elif is_retail_ranking:
        return "retail_ranking"
    else:
        return "unknown"

def normalize_retail_daily(headers: list, data_rows: list, artist_id: str, artist_name: str):
    """Convert Zojak Evolution daily format into standard import entries"""
    entries = []
    date_cols = headers[1:]  # Skip "Retail" column
    for row in data_rows:
        if not row or not row[0]:
            continue
        platform = row[0].strip()
        total_streams = 0
        for i, date_col in enumerate(date_cols, 1):
            if i < len(row):
                try:
                    total_streams += int(float(str(row[i]).strip().replace(",", "") or "0"))
                except:
                    pass
        period = f"{date_cols[0].strip()} - {date_cols[-1].strip()}" if date_cols else ""
        entries.append({
            "artist_name_raw": artist_name,
            "matched_artist_id": artist_id,
            "platform": platform,
            "country": "",
            "track": "",
            "streams": total_streams,
            "revenue": round(total_streams * DEFAULT_PER_STREAM_RATE, 4),
            "period": period,
            "status": "matched" if artist_id else "unmatched",
        })
    return entries

def normalize_retail_ranking(headers: list, data_rows: list, artist_id: str, artist_name: str):
    """Convert Zojak Ranking format into standard import entries"""
    headers_lower = [h.strip().lower() for h in headers]
    stream_col = None
    for i, h in enumerate(headers_lower):
        if h in ["streams", "plays", "units", "quantity"]:
            stream_col = i
            break
    entries = []
    for row in data_rows:
        if not row or not row[0]:
            continue
        platform = row[0].strip()
        streams = 0
        if stream_col and stream_col < len(row):
            try:
                streams = int(float(str(row[stream_col]).strip().replace(",", "") or "0"))
            except:
                pass
        entries.append({
            "artist_name_raw": artist_name,
            "matched_artist_id": artist_id,
            "platform": platform,
            "country": "",
            "track": "",
            "streams": streams,
            "revenue": round(streams * DEFAULT_PER_STREAM_RATE, 4),
            "period": "",
            "status": "matched" if artist_id else "unmatched",
        })
    return entries


# ============= ROYALTY IMPORT =============

@admin_router.post("/royalties/import")
async def admin_import_royalties(request: Request):
    """Admin: Import royalty file (CSV, XLSX, PDF) — matches against ALL platform users"""
    user = await require_admin(request)
    form = await request.form()
    file = form.get("file")
    template_id = form.get("template_id", "")
    assign_artist_id = form.get("artist_id", "")  # For single-artist reports
    if not file:
        raise HTTPException(status_code=400, detail="No file uploaded")

    filename = file.filename.lower()
    content = await file.read()

    # Parse based on file extension
    if filename.endswith(".csv"):
        headers, data_rows = parse_csv_to_rows(content)
    elif filename.endswith(".xlsx") or filename.endswith(".xls"):
        headers, data_rows = parse_xlsx_to_rows(content)
    elif filename.endswith(".pdf"):
        headers, data_rows = parse_pdf_to_rows(content)
    else:
        raise HTTPException(status_code=400, detail="Unsupported file format. Please upload CSV, XLSX, or PDF.")

    # Detect format type
    file_format = detect_file_format(headers, data_rows)

    # Resolve artist for single-artist reports
    assigned_artist_name = ""
    if assign_artist_id:
        au = await db.users.find_one({"id": assign_artist_id}, {"_id": 0, "artist_name": 1, "name": 1})
        assigned_artist_name = au.get("artist_name", au.get("name", "")) if au else ""

    import_id = f"imp_{uuid.uuid4().hex[:12]}"
    now = datetime.now(timezone.utc).isoformat()

    # Handle special formats (Zojak/PaymentHub style)
    if file_format in ("retail_daily", "retail_ranking"):
        if not assign_artist_id:
            raise HTTPException(status_code=400, detail="This file is a single-artist platform report. Please select which artist it belongs to.")
        if file_format == "retail_daily":
            raw_entries = normalize_retail_daily(headers, data_rows, assign_artist_id, assigned_artist_name)
        else:
            raw_entries = normalize_retail_ranking(headers, data_rows, assign_artist_id, assigned_artist_name)

        entries = []
        total_revenue = 0
        matched = 0
        for e in raw_entries:
            entry = {**e, "id": f"ir_{uuid.uuid4().hex[:12]}", "import_id": import_id, "admin_id": user["id"], "created_at": now}
            entries.append(entry)
            total_revenue += e["revenue"]
            if e["status"] == "matched":
                matched += 1

        if entries:
            await db.imported_royalties.insert_many(entries)

        await db.royalty_imports.insert_one({
            "id": import_id, "admin_id": user["id"],
            "filename": file.filename, "total_rows": len(entries),
            "matched": matched, "unmatched": len(entries) - matched,
            "total_revenue": round(total_revenue, 2),
            "column_mapping": {"format": file_format, "assigned_artist": assigned_artist_name},
            "template_used": f"Auto ({file_format})",
            "created_at": now,
        })

        # In-app notification + email for matched artist
        if assign_artist_id and total_revenue > 0:
            await db.notifications.insert_one({
                "id": f"notif_{uuid.uuid4().hex[:12]}",
                "user_id": assign_artist_id,
                "type": "royalty_update",
                "message": f"New earnings of ${total_revenue:.2f} have been added to your account via Kalmori Distribution.",
                "read": False,
                "created_at": now,
            })
            try:
                au_email = await db.users.find_one({"id": assign_artist_id}, {"_id": 0, "email": 1})
                if au_email and au_email.get("email"):
                    from routes.email_routes import send_email, email_base
                    body = f"""<p style="color:#ccc;font-size:15px;margin:0 0 16px;">Hey {assigned_artist_name}!</p>
                    <p style="color:#999;font-size:14px;line-height:1.7;margin:0 0 20px;">New earnings data has been processed by Kalmori Distribution. Here's your update:</p>
                    <div style="background:#111;border:1px solid #222;border-radius:12px;padding:20px;margin:20px 0;text-align:center;">
                    <p style="color:#1DB954;font-size:36px;font-weight:bold;margin:0;">${total_revenue:.2f}</p>
                    <p style="color:#999;font-size:13px;margin:4px 0 0;">New earnings added to your account</p>
                    </div>
                    <p style="color:#999;font-size:13px;margin:16px 0 0;">Log in to your dashboard to view your full earnings breakdown.</p>"""
                    html = email_base("linear-gradient(135deg,#FFD700 0%,#FFA000 100%)", "New Kalmori Earnings!", body, "Kalmori Distribution")
                    import asyncio
                    asyncio.ensure_future(send_email(au_email["email"], f"Kalmori Distribution: New earnings of ${total_revenue:.2f}", html))
            except Exception as e:
                logger.warning(f"Notification email failed: {e}")

        return {
            "message": f"Import complete. {matched} matched, {len(entries) - matched} unmatched.",
            "import_id": import_id, "total_rows": len(entries),
            "matched": matched, "unmatched": len(entries) - matched,
            "total_revenue": round(total_revenue, 2),
            "column_mapping": {"format": file_format, "assigned_artist": assigned_artist_name},
            "file_format": file_format,
        }

    # Standard multi-artist format
    headers_lower = [h.strip().lower() for h in headers]
    template_name = ""
    if template_id:
        tpl = await db.distributor_templates.find_one({"id": template_id}, {"_id": 0})
        if tpl and tpl.get("column_mapping"):
            template_name = tpl.get("name", "")
            col_map = {}
            for field, header_name in tpl["column_mapping"].items():
                hn = header_name.strip().lower()
                for i, h in enumerate(headers_lower):
                    if hn == h or hn in h:
                        col_map[field] = i
                        break
        else:
            col_map = detect_columns(headers)
    else:
        col_map = detect_columns(headers)

    if "artist" not in col_map:
        # If no artist column but an artist is selected, treat all rows as that artist
        if assign_artist_id:
            col_map_no_artist = col_map
            entries = []
            total_revenue = 0
            for row in data_rows:
                if not row:
                    continue
                track = row[col_map_no_artist["track"]].strip() if "track" in col_map_no_artist and col_map_no_artist["track"] < len(row) else ""
                platform = row[col_map_no_artist["platform"]].strip() if "platform" in col_map_no_artist and col_map_no_artist["platform"] < len(row) else ""
                country = row[col_map_no_artist["country"]].strip() if "country" in col_map_no_artist and col_map_no_artist["country"] < len(row) else ""
                period = row[col_map_no_artist["period"]].strip() if "period" in col_map_no_artist and col_map_no_artist["period"] < len(row) else ""
                try:
                    streams_val = int(float(str(row[col_map_no_artist["streams"]]).strip().replace(",", ""))) if "streams" in col_map_no_artist and col_map_no_artist["streams"] < len(row) else 0
                except:
                    streams_val = 0
                try:
                    rev_val = float(str(row[col_map_no_artist["revenue"]]).strip().replace(",", "").replace("$", "")) if "revenue" in col_map_no_artist and col_map_no_artist["revenue"] < len(row) else 0
                except:
                    rev_val = 0
                if rev_val == 0 and streams_val > 0:
                    rev_val = round(streams_val * DEFAULT_PER_STREAM_RATE, 4)
                entry = {
                    "id": f"ir_{uuid.uuid4().hex[:12]}", "import_id": import_id,
                    "admin_id": user["id"], "artist_name_raw": assigned_artist_name,
                    "matched_artist_id": assign_artist_id, "track": track,
                    "platform": platform, "country": country, "streams": streams_val,
                    "revenue": round(rev_val, 4), "period": period,
                    "status": "matched", "created_at": now,
                }
                entries.append(entry)
                total_revenue += rev_val
            if entries:
                await db.imported_royalties.insert_many(entries)
            await db.royalty_imports.insert_one({
                "id": import_id, "admin_id": user["id"],
                "filename": file.filename, "total_rows": len(entries),
                "matched": len(entries), "unmatched": 0,
                "total_revenue": round(total_revenue, 2),
                "column_mapping": {k: headers[v] for k, v in col_map_no_artist.items()},
                "template_used": template_name or "Auto-detected",
                "created_at": now,
            })
            return {
                "message": f"Import complete. {len(entries)} rows assigned to {assigned_artist_name}.",
                "import_id": import_id, "total_rows": len(entries),
                "matched": len(entries), "unmatched": 0,
                "total_revenue": round(total_revenue, 2),
                "column_mapping": {k: headers[v] for k, v in col_map_no_artist.items()},
            }
        raise HTTPException(status_code=400, detail=f"Could not detect 'Artist' column. Headers found: {headers}. For single-artist reports, please select an artist from the dropdown.")

    all_users = {}
    async for u in db.users.find({}, {"_id": 0, "id": 1, "artist_name": 1, "name": 1, "email": 1}):
        all_users[u["id"]] = u.get("artist_name", u.get("name", ""))

    all_splits = {}
    async for r in db.label_artists.find({"status": "active"}, {"_id": 0}):
        all_splits[r["artist_id"]] = {"a": r.get("artist_split", 70), "l": r.get("label_split", 30)}

    matched = 0
    unmatched = 0
    total_revenue = 0
    entries = []
    notifications = {}

    for row in data_rows:
        if not row or len(row) <= max(col_map.values(), default=0):
            continue
        artist_name_raw = row[col_map["artist"]].strip() if "artist" in col_map else ""
        track = row[col_map["track"]].strip() if "track" in col_map and col_map["track"] < len(row) else ""
        platform = row[col_map["platform"]].strip() if "platform" in col_map and col_map["platform"] < len(row) else ""
        country = row[col_map["country"]].strip() if "country" in col_map and col_map["country"] < len(row) else ""
        period = row[col_map["period"]].strip() if "period" in col_map and col_map["period"] < len(row) else ""
        try:
            streams_val = int(float(str(row[col_map["streams"]]).strip().replace(",", ""))) if "streams" in col_map and col_map["streams"] < len(row) else 0
        except:
            streams_val = 0
        try:
            rev_val = float(str(row[col_map["revenue"]]).strip().replace(",", "").replace("$", "")) if "revenue" in col_map and col_map["revenue"] < len(row) else 0
        except:
            rev_val = 0
        if rev_val == 0 and streams_val > 0:
            rev_val = round(streams_val * DEFAULT_PER_STREAM_RATE, 4)

        matched_id = fuzzy_match_artist(artist_name_raw, all_users, 0.7)
        entry = {
            "id": f"ir_{uuid.uuid4().hex[:12]}", "import_id": import_id,
            "admin_id": user["id"], "artist_name_raw": artist_name_raw,
            "matched_artist_id": matched_id, "track": track,
            "platform": platform, "country": country, "streams": streams_val,
            "revenue": round(rev_val, 4), "period": period,
            "status": "matched" if matched_id else "unmatched", "created_at": now,
        }
        entries.append(entry)
        total_revenue += rev_val

        if matched_id:
            matched += 1
            sp = all_splits.get(matched_id, {"a": 100, "l": 0})
            artist_earn = round(rev_val * sp["a"] / 100, 2)
            if matched_id not in notifications:
                notifications[matched_id] = {"total": 0, "name": ""}
            notifications[matched_id]["total"] += artist_earn
            u = await db.users.find_one({"id": matched_id}, {"_id": 0, "artist_name": 1, "name": 1, "email": 1})
            if u:
                notifications[matched_id]["name"] = u.get("artist_name", u.get("name", ""))
                notifications[matched_id]["email"] = u.get("email", "")
        else:
            unmatched += 1

    if entries:
        await db.imported_royalties.insert_many(entries)

    await db.royalty_imports.insert_one({
        "id": import_id, "admin_id": user["id"],
        "filename": file.filename, "total_rows": len(entries),
        "matched": matched, "unmatched": unmatched,
        "total_revenue": round(total_revenue, 2),
        "column_mapping": {k: headers[v] for k, v in col_map.items()},
        "template_used": template_name or "Auto-detected",
        "created_at": now,
    })

    # In-app notifications + emails for ALL matched artists
    for a_id, notif in notifications.items():
        if notif["total"] > 0:
            # Always create in-app notification
            await db.notifications.insert_one({
                "id": f"notif_{uuid.uuid4().hex[:12]}",
                "user_id": a_id,
                "type": "royalty_update",
                "message": f"New earnings of ${notif['total']:.2f} have been added to your account via Kalmori Distribution.",
                "read": False,
                "created_at": now,
            })
            # Send email if they have one on file
            if notif.get("email"):
                try:
                    from routes.email_routes import send_email, email_base
                    body = f"""<p style="color:#ccc;font-size:15px;margin:0 0 16px;">Hey {notif['name']}!</p>
                    <p style="color:#999;font-size:14px;line-height:1.7;margin:0 0 20px;">New earnings data has been processed by Kalmori Distribution. Here's your update:</p>
                    <div style="background:#111;border:1px solid #222;border-radius:12px;padding:20px;margin:20px 0;text-align:center;">
                    <p style="color:#1DB954;font-size:36px;font-weight:bold;margin:0;">${notif['total']:.2f}</p>
                    <p style="color:#999;font-size:13px;margin:4px 0 0;">New earnings added to your account</p>
                    </div>
                    <p style="color:#999;font-size:13px;margin:16px 0 0;">Log in to your dashboard to view your full earnings breakdown.</p>"""
                    html = email_base("linear-gradient(135deg,#FFD700 0%,#FFA000 100%)", "New Kalmori Earnings!", body, "Kalmori Distribution")
                    import asyncio
                    asyncio.ensure_future(send_email(notif["email"], f"Kalmori Distribution: New earnings of ${notif['total']:.2f}", html))
                except Exception as e:
                    logger.warning(f"Royalty notification email failed for {a_id}: {e}")

    return {
        "message": f"Import complete. {matched} matched, {unmatched} unmatched.",
        "import_id": import_id, "total_rows": len(entries),
        "matched": matched, "unmatched": unmatched,
        "total_revenue": round(total_revenue, 2),
        "column_mapping": {k: headers[v] for k, v in col_map.items()},
    }

@admin_router.get("/royalties/imports")
async def admin_list_imports(request: Request):
    await require_admin(request)
    imports = await db.royalty_imports.find({}, {"_id": 0}).sort("created_at", -1).to_list(100)
    return {"imports": imports}

@admin_router.get("/royalties/imports/{import_id}")
async def admin_get_import_detail(import_id: str, request: Request):
    await require_admin(request)
    imp = await db.royalty_imports.find_one({"id": import_id}, {"_id": 0})
    if not imp: raise HTTPException(status_code=404, detail="Import not found")
    entries = await db.imported_royalties.find({"import_id": import_id}, {"_id": 0}).to_list(1000)
    for e in entries:
        if e.get("matched_artist_id"):
            u = await db.users.find_one({"id": e["matched_artist_id"]}, {"_id": 0, "artist_name": 1, "name": 1})
            e["matched_artist_name"] = u.get("artist_name", u.get("name", "Unknown")) if u else "Unknown"
    return {"import": imp, "entries": entries}

@admin_router.put("/royalties/entries/{entry_id}/assign")
async def admin_assign_unmatched(entry_id: str, data: AssignEntryInput, request: Request):
    await require_admin(request)
    entry = await db.imported_royalties.find_one({"id": entry_id})
    if not entry: raise HTTPException(status_code=404, detail="Entry not found")
    await db.imported_royalties.update_one({"id": entry_id}, {"$set": {"matched_artist_id": data.artist_id, "status": "matched"}})
    imp = await db.royalty_imports.find_one({"id": entry.get("import_id")})
    if imp:
        await db.royalty_imports.update_one({"id": entry["import_id"]}, {"$inc": {"matched": 1, "unmatched": -1}})
    return {"message": "Entry assigned successfully"}

@admin_router.get("/royalties/users")
async def admin_get_all_users_for_assign(request: Request):
    await require_admin(request)
    users = await db.users.find({}, {"_id": 0, "id": 1, "artist_name": 1, "name": 1, "email": 1}).to_list(500)
    return {"users": users}


# ============= DISTRIBUTOR TEMPLATES =============

@admin_router.post("/distributor-templates")
async def create_distributor_template(data: DistributorTemplateInput, request: Request):
    user = await require_admin(request)
    now = datetime.now(timezone.utc).isoformat()
    template = {
        "id": f"tpl_{uuid.uuid4().hex[:12]}", "name": data.name.strip(),
        "admin_id": user["id"], "column_mapping": data.column_mapping,
        "notes": data.notes or "", "created_at": now, "updated_at": now,
    }
    await db.distributor_templates.insert_one(template)
    template.pop("_id", None)
    return template

@admin_router.get("/distributor-templates")
async def list_distributor_templates(request: Request):
    await require_admin(request)
    templates = await db.distributor_templates.find({}, {"_id": 0}).sort("name", 1).to_list(100)
    return {"templates": templates}

@admin_router.put("/distributor-templates/{template_id}")
async def update_distributor_template(template_id: str, data: DistributorTemplateInput, request: Request):
    await require_admin(request)
    result = await db.distributor_templates.update_one(
        {"id": template_id},
        {"$set": {"name": data.name.strip(), "column_mapping": data.column_mapping, "notes": data.notes or "", "updated_at": datetime.now(timezone.utc).isoformat()}}
    )
    if result.matched_count == 0: raise HTTPException(status_code=404, detail="Template not found")
    return {"message": "Template updated"}

@admin_router.delete("/distributor-templates/{template_id}")
async def delete_distributor_template(template_id: str, request: Request):
    await require_admin(request)
    result = await db.distributor_templates.delete_one({"id": template_id})
    if result.deleted_count == 0: raise HTTPException(status_code=404, detail="Template not found")
    return {"message": "Template deleted"}


# ============= RECONCILIATION =============

@admin_router.get("/royalties/reconciliation")
async def admin_royalty_reconciliation(request: Request):
    await require_admin(request)
    entries = await db.imported_royalties.find({}, {"_id": 0}).to_list(10000)
    groups = {}
    for e in entries:
        key = (e.get("artist_name_raw", "").strip().lower(), e.get("track", "").strip().lower(),
               e.get("platform", "").strip().lower(), e.get("period", "").strip().lower())
        if not key[0]: continue
        groups.setdefault(key, []).append(e)

    duplicates = []
    discrepancies = []
    total_duplicate_revenue = 0
    total_discrepancy_amount = 0

    for key, group_entries in groups.items():
        if len(group_entries) <= 1: continue
        import_ids = set(e.get("import_id") for e in group_entries)
        if len(import_ids) <= 1: continue
        revenues = [e.get("revenue", 0) for e in group_entries]
        if len(set(revenues)) == 1:
            dup_rev = revenues[0] * (len(group_entries) - 1)
            total_duplicate_revenue += dup_rev
            duplicates.append({
                "artist": group_entries[0].get("artist_name_raw", ""),
                "track": group_entries[0].get("track", ""),
                "platform": group_entries[0].get("platform", ""),
                "period": group_entries[0].get("period", ""),
                "count": len(group_entries), "revenue_per_entry": revenues[0],
                "excess_revenue": round(dup_rev, 4),
                "import_ids": list(import_ids), "entry_ids": [e["id"] for e in group_entries],
            })
        else:
            min_rev, max_rev = min(revenues), max(revenues)
            diff = round(max_rev - min_rev, 4)
            total_discrepancy_amount += diff
            discrepancies.append({
                "artist": group_entries[0].get("artist_name_raw", ""),
                "track": group_entries[0].get("track", ""),
                "platform": group_entries[0].get("platform", ""),
                "period": group_entries[0].get("period", ""),
                "count": len(group_entries), "revenues": revenues,
                "min_revenue": min_rev, "max_revenue": max_rev,
                "discrepancy_amount": diff,
                "import_ids": list(import_ids), "entry_ids": [e["id"] for e in group_entries],
            })

    total_imports = await db.royalty_imports.count_documents({})
    total_entries = len(entries)
    total_revenue = sum(e.get("revenue", 0) for e in entries)
    matched_count = sum(1 for e in entries if e.get("status") == "matched")
    unmatched_count = sum(1 for e in entries if e.get("status") == "unmatched")

    return {
        "summary": {
            "total_imports": total_imports, "total_entries": total_entries,
            "total_revenue": round(total_revenue, 2),
            "matched_entries": matched_count, "unmatched_entries": unmatched_count,
            "duplicate_groups": len(duplicates), "discrepancy_groups": len(discrepancies),
            "total_duplicate_revenue": round(total_duplicate_revenue, 2),
            "total_discrepancy_amount": round(total_discrepancy_amount, 2),
        },
        "duplicates": duplicates[:50], "discrepancies": discrepancies[:50],
    }
