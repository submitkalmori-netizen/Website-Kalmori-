"""Producer Royalty Split Routes — Split management, earnings, admin controls"""
from fastapi import APIRouter, HTTPException, Request
from datetime import datetime, timezone
import uuid
import logging

from core import db, get_current_user, require_admin

logger = logging.getLogger(__name__)
royalty_routes = APIRouter(prefix="/api")

DEFAULT_SPLITS = {
    "basic_lease": {"producer": 50, "artist": 50},
    "premium_lease": {"producer": 40, "artist": 60},
    "unlimited_lease": {"producer": 30, "artist": 70},
    "exclusive": {"producer": 0, "artist": 100},
}


@royalty_routes.get("/royalty-splits")
async def get_royalty_splits(request: Request):
    """Get all active royalty splits for the current user (as producer or artist)"""
    user = await get_current_user(request)
    uid = user["id"]
    splits = await db.royalty_splits.find(
        {"$or": [{"producer_id": uid}, {"artist_id": uid}]}, {"_id": 0}
    ).sort("created_at", -1).to_list(100)
    for s in splits:
        earnings = await db.split_earnings.find(
            {"split_id": s["id"]}, {"_id": 0}
        ).sort("period", -1).to_list(12)
        s["earnings_history"] = earnings
        s["total_earned"] = round(sum(e.get("amount", 0) for e in earnings if e.get("recipient_id") == uid), 2)
        s["is_producer"] = s["producer_id"] == uid
    return {"splits": splits}


@royalty_routes.get("/royalty-splits/summary")
async def get_splits_summary(request: Request):
    """Dashboard summary of royalty split earnings"""
    user = await get_current_user(request)
    uid = user["id"]
    splits = await db.royalty_splits.find(
        {"$or": [{"producer_id": uid}, {"artist_id": uid}]}, {"_id": 0}
    ).to_list(100)
    total_as_producer = 0.0
    total_as_artist = 0.0
    active_splits = 0
    for s in splits:
        if s.get("status") == "active":
            active_splits += 1
        all_earnings = await db.split_earnings.find({"split_id": s["id"], "recipient_id": uid}, {"_id": 0}).to_list(100)
        earned = sum(e.get("amount", 0) for e in all_earnings)
        if s["producer_id"] == uid:
            total_as_producer += earned
        else:
            total_as_artist += earned
    return {
        "active_splits": active_splits,
        "total_as_producer": round(total_as_producer, 2),
        "total_as_artist": round(total_as_artist, 2),
        "total_earned": round(total_as_producer + total_as_artist, 2),
    }


@royalty_routes.post("/royalty-splits/calculate")
async def calculate_and_distribute(request: Request):
    """Admin: Calculate and distribute royalty splits for all active beat licenses"""
    await require_admin(request)
    now = datetime.now(timezone.utc)
    period = now.strftime("%Y-%m")
    active_splits = await db.royalty_splits.find({"status": "active"}, {"_id": 0}).to_list(500)
    distributions = []
    for split in active_splits:
        beat_id = split.get("beat_id")
        artist_id = split.get("artist_id")
        if not beat_id or not artist_id:
            continue
        month_prefix = period
        pipeline = [
            {"$match": {"artist_id": artist_id, "timestamp": {"$regex": f"^{month_prefix}"}}},
            {"$group": {"_id": None, "streams": {"$sum": 1}, "revenue": {"$sum": "$revenue"}}}
        ]
        result = await db.stream_events.aggregate(pipeline).to_list(1)
        if not result:
            continue
        total_revenue = result[0].get("revenue", 0)
        total_streams = result[0].get("streams", 0)
        if total_revenue <= 0:
            continue
        producer_pct = split.get("producer_split", 50)
        artist_pct = split.get("artist_split", 50)
        producer_amount = round(total_revenue * producer_pct / 100, 2)
        artist_amount = round(total_revenue * artist_pct / 100, 2)
        existing = await db.split_earnings.find_one({"split_id": split["id"], "period": period})
        if existing:
            continue
        for recipient_id, amount, role in [
            (split["producer_id"], producer_amount, "producer"),
            (split["artist_id"], artist_amount, "artist"),
        ]:
            earning = {
                "id": f"se_{uuid.uuid4().hex[:12]}",
                "split_id": split["id"],
                "recipient_id": recipient_id,
                "beat_id": beat_id,
                "role": role,
                "period": period,
                "streams": total_streams,
                "gross_revenue": total_revenue,
                "split_percentage": producer_pct if role == "producer" else artist_pct,
                "amount": amount,
                "status": "calculated",
                "created_at": now.isoformat(),
            }
            await db.split_earnings.insert_one(earning)
            earning.pop("_id", None)
            await db.wallets.update_one(
                {"user_id": recipient_id},
                {"$inc": {"balance": amount, "total_earnings": amount}},
                upsert=True
            )
        distributions.append({
            "split_id": split["id"], "beat": split.get("beat_title", ""),
            "period": period, "revenue": total_revenue, "streams": total_streams,
            "producer_payout": producer_amount, "artist_payout": artist_amount,
        })
    return {"period": period, "distributions": distributions, "total_processed": len(distributions)}


@royalty_routes.get("/admin/royalty-splits")
async def admin_list_splits(request: Request):
    """Admin: View all royalty splits"""
    await require_admin(request)
    splits = await db.royalty_splits.find({}, {"_id": 0}).sort("created_at", -1).to_list(200)
    for s in splits:
        earnings = await db.split_earnings.find({"split_id": s["id"]}, {"_id": 0}).to_list(50)
        s["total_distributed"] = round(sum(e.get("amount", 0) for e in earnings), 2)
        s["periods_distributed"] = len(set(e.get("period") for e in earnings))
    return {"splits": splits}


@royalty_routes.put("/admin/royalty-splits/{split_id}")
async def admin_update_split(split_id: str, request: Request):
    """Admin: Update a royalty split configuration"""
    await require_admin(request)
    body = await request.json()
    update = {}
    if "producer_split" in body:
        update["producer_split"] = body["producer_split"]
        update["artist_split"] = 100 - body["producer_split"]
    if "status" in body:
        update["status"] = body["status"]
    if update:
        update["updated_at"] = datetime.now(timezone.utc).isoformat()
        await db.royalty_splits.update_one({"id": split_id}, {"$set": update})
    split = await db.royalty_splits.find_one({"id": split_id}, {"_id": 0})
    return split
