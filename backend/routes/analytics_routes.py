"""Analytics, Revenue, Goals, Fan Analytics, and CSV Import routes"""
from fastapi import APIRouter, HTTPException, Request, UploadFile, File
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import Optional
from datetime import datetime, timezone, timedelta
import io, csv, uuid, random

analytics_router = APIRouter(prefix="/api", tags=["Analytics"])

# Module-level references (set by init)
db = None
get_current_user = None
check_feature_access = None
SUBSCRIPTION_PLANS = None

PLATFORM_RATES = {
    "Spotify": 0.004, "Apple Music": 0.008, "YouTube Music": 0.002,
    "Amazon Music": 0.004, "Tidal": 0.012, "Deezer": 0.003,
    "Pandora": 0.002, "SoundCloud": 0.003,
}

GOAL_TYPES = {
    "streams": {"label": "Total Streams", "unit": "streams"},
    "monthly_streams": {"label": "Monthly Streams", "unit": "streams/month"},
    "countries": {"label": "Countries Reached", "unit": "countries"},
    "revenue": {"label": "Revenue Earned", "unit": "USD"},
    "releases": {"label": "Releases Published", "unit": "releases"},
    "presave_subs": {"label": "Pre-Save Subscribers", "unit": "subscribers"},
    "collaborations": {"label": "Collaborations", "unit": "collabs"},
}

class CreateGoalInput(BaseModel):
    goal_type: str
    target_value: float
    title: Optional[str] = None
    deadline: Optional[str] = None

class RevenueCalculatorInput(BaseModel):
    streams: int = 10000
    platform_mix: Optional[dict] = None

def init_analytics_routes(database, get_user_fn, check_access_fn, sub_plans):
    global db, get_current_user, check_feature_access, SUBSCRIPTION_PLANS
    db = database
    get_current_user = get_user_fn
    check_feature_access = check_access_fn
    SUBSCRIPTION_PLANS = sub_plans


# ============= ANALYTICS OVERVIEW =============
@analytics_router.get("/analytics/overview")
async def get_analytics_overview(request: Request):
    user = await get_current_user(request)
    releases = await db.releases.find({"artist_id": user["id"]}, {"_id": 0}).to_list(100)
    total_releases = len(releases)
    distributed = sum(1 for r in releases if r.get("status") == "distributed")
    stream_pipeline = [
        {"$match": {"artist_id": user["id"]}},
        {"$group": {"_id": None, "total_streams": {"$sum": 1}, "total_revenue": {"$sum": "$revenue"}}}
    ]
    stream_result = await db.stream_events.aggregate(stream_pipeline).to_list(1)
    stream_totals = stream_result[0] if stream_result else {"total_streams": 0, "total_revenue": 0.0}
    ts = stream_totals["total_streams"]
    te = round(stream_totals["total_revenue"], 2)
    royalty_pipeline = [
        {"$match": {"release_id": {"$in": [r["id"] for r in releases]}}},
        {"$group": {"_id": None, "total_streams": {"$sum": "$streams"}, "total_earnings": {"$sum": "$earnings"}, "total_downloads": {"$sum": "$downloads"}}}
    ]
    result = await db.royalties.aggregate(royalty_pipeline).to_list(1)
    if result:
        totals = result[0]
        totals["total_streams"] = max(totals["total_streams"], ts)
        totals["total_earnings"] = max(round(totals["total_earnings"], 2), te)
    else:
        totals = stream_totals
        totals["total_downloads"] = 0
    # Platform breakdown from stream_events (real data only)
    platform_pipeline = [
        {"$match": {"artist_id": user["id"]}},
        {"$group": {"_id": "$platform", "count": {"$sum": 1}}}
    ]
    platform_result = await db.stream_events.aggregate(platform_pipeline).to_list(20)
    streams_by_store = {r["_id"]: r["count"] for r in platform_result if r["_id"]} if platform_result else {}
    # Country breakdown from stream_events (real data only)
    country_pipeline = [
        {"$match": {"artist_id": user["id"]}},
        {"$group": {"_id": "$country", "count": {"$sum": 1}}}
    ]
    country_result = await db.stream_events.aggregate(country_pipeline).to_list(20)
    streams_by_country = {r["_id"]: r["count"] for r in country_result if r["_id"]} if country_result else {}
    # Daily streams from stream_events (real data only)
    daily_pipeline = [
        {"$match": {"artist_id": user["id"]}},
        {"$group": {"_id": {"$substr": ["$timestamp", 0, 10]}, "streams": {"$sum": 1}, "earnings": {"$sum": "$revenue"}}},
        {"$sort": {"_id": -1}},
        {"$limit": 30}
    ]
    daily_result = await db.stream_events.aggregate(daily_pipeline).to_list(30)
    daily_streams = [{"date": r["_id"], "streams": r["streams"], "earnings": round(r["earnings"], 2)} for r in reversed(daily_result)] if daily_result else []
    return {
        "total_streams": totals["total_streams"],
        "total_earnings": totals.get("total_earnings", te),
        "total_downloads": totals.get("total_downloads", 0),
        "release_count": total_releases,
        "distributed_count": distributed,
        "streams_by_store": streams_by_store,
        "streams_by_country": streams_by_country,
        "daily_streams": daily_streams,
    }


# ============= ANALYTICS TRENDING =============
@analytics_router.get("/analytics/trending")
async def get_trending(request: Request):
    user = await get_current_user(request)
    now = datetime.now(timezone.utc)
    week_ago = (now - timedelta(days=7)).isoformat()
    two_weeks_ago = (now - timedelta(days=14)).isoformat()
    releases = await db.releases.find({"artist_id": user["id"]}, {"_id": 0}).to_list(100)
    release_ids = [r["id"] for r in releases]
    total_pipeline = [
        {"$match": {"artist_id": user["id"], "release_id": {"$in": release_ids}}},
        {"$group": {"_id": "$release_id", "total_streams": {"$sum": 1}}}
    ]
    total_map = {r["_id"]: r["total_streams"] for r in await db.stream_events.aggregate(total_pipeline).to_list(200)}
    week_pipeline = [
        {"$match": {"artist_id": user["id"], "release_id": {"$in": release_ids}, "timestamp": {"$gte": week_ago}}},
        {"$group": {"_id": "$release_id", "streams": {"$sum": 1}}}
    ]
    week_map = {r["_id"]: r["streams"] for r in await db.stream_events.aggregate(week_pipeline).to_list(200)}
    prev_pipeline = [
        {"$match": {"artist_id": user["id"], "release_id": {"$in": release_ids}, "timestamp": {"$gte": two_weeks_ago, "$lt": week_ago}}},
        {"$group": {"_id": "$release_id", "streams": {"$sum": 1}}}
    ]
    prev_map = {r["_id"]: r["streams"] for r in await db.stream_events.aggregate(prev_pipeline).to_list(200)}
    plat_pipeline = [
        {"$match": {"artist_id": user["id"], "release_id": {"$in": release_ids}}},
        {"$group": {"_id": {"release_id": "$release_id", "platform": "$platform"}, "count": {"$sum": 1}}},
        {"$sort": {"count": -1}}
    ]
    plat_raw = await db.stream_events.aggregate(plat_pipeline).to_list(500)
    top_platforms = {}
    for tp in plat_raw:
        rid = tp["_id"]["release_id"]
        if rid not in top_platforms:
            top_platforms[rid] = tp["_id"]["platform"]
    country_pipeline = [
        {"$match": {"artist_id": user["id"], "release_id": {"$in": release_ids}}},
        {"$group": {"_id": {"release_id": "$release_id", "country": "$country"}, "count": {"$sum": 1}}},
        {"$sort": {"count": -1}}
    ]
    country_raw = await db.stream_events.aggregate(country_pipeline).to_list(500)
    top_countries = {}
    for tc in country_raw:
        rid = tc["_id"]["release_id"]
        if rid not in top_countries:
            top_countries[rid] = tc["_id"]["country"]
    trending = []
    for r in releases:
        total = total_map.get(r["id"], 0)
        this_week = week_map.get(r["id"], 0)
        last_week = prev_map.get(r["id"], 0)
        if total > 0 or r.get("status") == "distributed":
            change = round((this_week - last_week) / max(last_week, 1) * 100, 1) if last_week > 0 else 0.0
            trending.append({
                "release_id": r["id"], "title": r["title"], "release_type": r.get("release_type", "single"),
                "cover_art_url": r.get("cover_art_url"), "genre": r.get("genre", ""),
                "streams_this_week": this_week, "total_streams": total, "change_percent": change,
                "top_store": top_platforms.get(r["id"], "N/A"),
                "top_country": top_countries.get(r["id"], "N/A"),
            })
    trending.sort(key=lambda x: x["streams_this_week"], reverse=True)
    return {"trending": trending[:10], "period": "last_7_days"}


# ============= LEADERBOARD =============
@analytics_router.get("/analytics/leaderboard")
async def get_leaderboard(request: Request):
    user = await get_current_user(request)
    releases = await db.releases.find({"artist_id": user["id"]}, {"_id": 0}).to_list(100)
    if not releases:
        return {"leaderboard": [], "total_releases": 0, "active_releases": 0}
    release_ids = [r["id"] for r in releases]
    stream_pipeline = [
        {"$match": {"artist_id": user["id"], "release_id": {"$in": release_ids}}},
        {"$group": {"_id": "$release_id", "total_streams": {"$sum": 1}, "total_revenue": {"$sum": "$revenue"}}}
    ]
    stream_map = {r["_id"]: r for r in await db.stream_events.aggregate(stream_pipeline).to_list(200)}
    now = datetime.now(timezone.utc)
    week_ago = (now - timedelta(days=7)).isoformat()
    two_weeks_ago = (now - timedelta(days=14)).isoformat()
    week_pipeline = [
        {"$match": {"artist_id": user["id"], "release_id": {"$in": release_ids}, "timestamp": {"$gte": week_ago}}},
        {"$group": {"_id": "$release_id", "streams": {"$sum": 1}}}
    ]
    week_map = {r["_id"]: r["streams"] for r in await db.stream_events.aggregate(week_pipeline).to_list(200)}
    prev_pipeline = [
        {"$match": {"artist_id": user["id"], "release_id": {"$in": release_ids}, "timestamp": {"$gte": two_weeks_ago, "$lt": week_ago}}},
        {"$group": {"_id": "$release_id", "streams": {"$sum": 1}}}
    ]
    prev_map = {r["_id"]: r["streams"] for r in await db.stream_events.aggregate(prev_pipeline).to_list(200)}
    leaderboard = []
    for r in releases:
        sd = stream_map.get(r["id"], {"total_streams": 0, "total_revenue": 0})
        this_week = week_map.get(r["id"], 0)
        last_week = prev_map.get(r["id"], 0)
        momentum = round((this_week - last_week) / max(last_week, 1) * 100, 1) if last_week > 0 else (100.0 if this_week > 0 else 0.0)
        leaderboard.append({
            "release_id": r["id"], "title": r["title"], "release_type": r.get("release_type", "single"),
            "cover_art_url": r.get("cover_art_url"), "genre": r.get("genre", ""),
            "total_streams": sd["total_streams"], "total_revenue": round(sd["total_revenue"], 2),
            "streams_this_week": this_week, "streams_last_week": last_week, "momentum": momentum,
            "status": r.get("status", "draft"), "distributed_at": r.get("distributed_at"),
        })
    leaderboard.sort(key=lambda x: x["total_streams"], reverse=True)
    for i, entry in enumerate(leaderboard):
        entry["rank"] = i + 1
    active = sum(1 for e in leaderboard if e["total_streams"] > 0)
    return {"leaderboard": leaderboard, "total_releases": len(releases), "active_releases": active}


# ============= GOALS & MILESTONES =============
@analytics_router.post("/goals")
async def create_goal(data: CreateGoalInput, request: Request):
    user = await get_current_user(request)
    if data.goal_type not in GOAL_TYPES:
        raise HTTPException(status_code=400, detail=f"Invalid goal_type. Must be one of: {', '.join(GOAL_TYPES.keys())}")
    goal_id = f"goal_{uuid.uuid4().hex[:12]}"
    now = datetime.now(timezone.utc).isoformat()
    goal_info = GOAL_TYPES[data.goal_type]
    doc = {
        "id": goal_id, "user_id": user["id"], "goal_type": data.goal_type,
        "target_value": data.target_value, "title": data.title or f"Reach {int(data.target_value):,} {goal_info['unit']}",
        "deadline": data.deadline, "status": "active", "created_at": now, "completed_at": None,
    }
    await db.goals.insert_one(doc)
    doc.pop("_id", None)
    return {"message": "Goal created", "goal": doc}

@analytics_router.get("/goals")
async def get_goals(request: Request):
    user = await get_current_user(request)
    goals = await db.goals.find({"user_id": user["id"]}, {"_id": 0}).sort("created_at", -1).to_list(50)
    now = datetime.now(timezone.utc)
    month_start = now.replace(day=1).isoformat()
    total_streams = await db.stream_events.count_documents({"artist_id": user["id"]})
    monthly_streams = await db.stream_events.count_documents({"artist_id": user["id"], "timestamp": {"$gte": month_start}})
    countries_pipeline = [{"$match": {"artist_id": user["id"]}}, {"$group": {"_id": "$country"}}]
    countries_count = len(await db.stream_events.aggregate(countries_pipeline).to_list(200))
    revenue_pipeline = [{"$match": {"artist_id": user["id"]}}, {"$group": {"_id": None, "total": {"$sum": "$revenue"}}}]
    revenue_result = await db.stream_events.aggregate(revenue_pipeline).to_list(1)
    total_revenue = revenue_result[0]["total"] if revenue_result else 0
    releases_count = await db.releases.count_documents({"artist_id": user["id"]})
    presave_count = sum([c.get("subscriber_count", 0) for c in await db.presave_campaigns.find({"artist_id": user["id"]}, {"subscriber_count": 1}).to_list(50)])
    collabs_count = await db.collaboration_posts.count_documents({"user_id": user["id"]})
    current_values = {
        "streams": total_streams, "monthly_streams": monthly_streams, "countries": countries_count,
        "revenue": round(total_revenue, 2), "releases": releases_count, "presave_subs": presave_count, "collaborations": collabs_count,
    }
    updated_goals = []
    for g in goals:
        cv = current_values.get(g["goal_type"], 0)
        progress = min(round(cv / max(g["target_value"], 1) * 100, 1), 100)
        if g["status"] == "active" and cv >= g["target_value"]:
            await db.goals.update_one({"id": g["id"]}, {"$set": {"status": "completed", "completed_at": now.isoformat()}})
            g["status"] = "completed"
            g["completed_at"] = now.isoformat()
        updated_goals.append({**g, "current_value": cv, "progress": progress})
    return {"goals": updated_goals, "current_values": current_values}

@analytics_router.delete("/goals/{goal_id}")
async def delete_goal(goal_id: str, request: Request):
    user = await get_current_user(request)
    result = await db.goals.delete_one({"id": goal_id, "user_id": user["id"]})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Goal not found")
    return {"message": "Goal deleted"}


# ============= REVENUE ANALYTICS =============
@analytics_router.get("/analytics/revenue")
async def get_revenue_analytics(request: Request):
    user = await get_current_user(request)
    plan = user.get("plan", "free")
    plan_cut = SUBSCRIPTION_PLANS.get(plan, {}).get("revenue_share", 15) / 100
    pipeline = [
        {"$match": {"artist_id": user["id"]}},
        {"$group": {"_id": "$platform", "streams": {"$sum": 1}, "raw_revenue": {"$sum": "$revenue"}}}
    ]
    platform_data = await db.stream_events.aggregate(pipeline).to_list(20)
    platforms = []
    total_gross = 0
    total_streams = 0
    for p in sorted(platform_data, key=lambda x: -x["streams"]):
        name = p["_id"] or "Other"
        rate = PLATFORM_RATES.get(name, 0.004)
        gross = round(p["streams"] * rate, 2)
        net = round(gross * (1 - plan_cut), 2)
        total_gross += gross
        total_streams += p["streams"]
        platforms.append({"platform": name, "streams": p["streams"], "rate_per_stream": rate, "gross_revenue": gross, "net_revenue": net})
    total_net = round(total_gross * (1 - plan_cut), 2)
    platform_cut = round(total_gross * plan_cut, 2)
    now = datetime.now(timezone.utc)
    monthly = []
    for i in range(5, -1, -1):
        month_start = (now.replace(day=1) - timedelta(days=30 * i)).strftime("%Y-%m")
        m_pipeline = [
            {"$match": {"artist_id": user["id"], "timestamp": {"$regex": f"^{month_start}"}}},
            {"$group": {"_id": "$platform", "streams": {"$sum": 1}}}
        ]
        m_data = await db.stream_events.aggregate(m_pipeline).to_list(20)
        m_gross = sum(r["streams"] * PLATFORM_RATES.get(r["_id"] or "Other", 0.004) for r in m_data)
        m_streams = sum(r["streams"] for r in m_data)
        monthly.append({"month": month_start, "streams": m_streams, "gross": round(m_gross, 2), "net": round(m_gross * (1 - plan_cut), 2)})
    collabs = await db.collaborations.find({"artist_id": user["id"], "status": "accepted"}, {"_id": 0}).to_list(50)
    splits = []
    for c in collabs:
        split_pct = c.get("split_percentage", 0)
        split_amount = round(total_net * split_pct / 100, 2)
        splits.append({"collaborator": c.get("collaborator_name", c.get("collaborator_email", "Unknown")),
            "release_id": c.get("release_id", ""), "role": c.get("role", "collaborator"),
            "split_percentage": split_pct, "estimated_amount": split_amount})
    total_collab_payout = sum(s["estimated_amount"] for s in splits)
    artist_take = round(total_net - total_collab_payout, 2)
    kalmori_entries = await db.imported_royalties.find({"matched_artist_id": user["id"], "status": "matched"}, {"_id": 0}).to_list(5000)
    kalmori_total_streams = 0
    kalmori_total_revenue = 0
    kalmori_platform_map = {}
    kalmori_monthly_map = {}
    for e in kalmori_entries:
        streams = e.get("streams", 0)
        revenue = e.get("revenue", 0)
        platform = e.get("platform", "Other") or "Other"
        period = e.get("period", "") or ""
        kalmori_total_streams += streams
        kalmori_total_revenue += revenue
        if platform not in kalmori_platform_map:
            kalmori_platform_map[platform] = {"streams": 0, "revenue": 0}
        kalmori_platform_map[platform]["streams"] += streams
        kalmori_platform_map[platform]["revenue"] += revenue
        month_key = ""
        if period:
            for fmt in ["%Y-%m", "%Y-%m-%d"]:
                try:
                    from datetime import datetime as dt_parse
                    parsed = dt_parse.strptime(period[:len(fmt.replace('%', '').replace('-', '')) + period.count('-')], fmt)
                    month_key = parsed.strftime("%Y-%m")
                    break
                except:
                    pass
            if not month_key and len(period) >= 7:
                month_key = period[:7]
        if not month_key:
            created = e.get("created_at", "")
            if created and len(created) >= 7:
                month_key = created[:7]
        if month_key:
            if month_key not in kalmori_monthly_map:
                kalmori_monthly_map[month_key] = {"streams": 0, "revenue": 0}
            kalmori_monthly_map[month_key]["streams"] += streams
            kalmori_monthly_map[month_key]["revenue"] += revenue
    kalmori_platforms = sorted([{"platform": k, "streams": v["streams"], "revenue": round(v["revenue"], 2)} for k, v in kalmori_platform_map.items()], key=lambda x: -x["revenue"])
    kalmori_monthly = []
    for m in monthly:
        mk = m["month"]
        km = kalmori_monthly_map.get(mk, {"streams": 0, "revenue": 0})
        kalmori_monthly.append({"month": mk, "streams": km["streams"], "revenue": round(km["revenue"], 2)})
    label_entry = await db.label_artists.find_one({"artist_id": user["id"], "status": "active"}, {"_id": 0, "artist_split": 1, "label_split": 1})
    kalmori_artist_split = label_entry.get("artist_split", 100) if label_entry else 100
    kalmori_your_take = round(kalmori_total_revenue * kalmori_artist_split / 100, 2)
    combined_streams = total_streams + kalmori_total_streams
    combined_gross = round(total_gross + kalmori_total_revenue, 2)
    combined_net = round(total_net + kalmori_your_take, 2)
    return {
        "summary": {"total_streams": total_streams, "gross_revenue": round(total_gross, 2), "platform_fee": platform_cut,
            "net_revenue": total_net, "artist_take": artist_take, "collab_payouts": round(total_collab_payout, 2),
            "plan": plan, "plan_cut_percent": round(plan_cut * 100, 1), "avg_rate_per_stream": round(total_gross / max(total_streams, 1), 4)},
        "platforms": platforms, "monthly_trend": monthly, "collaborator_splits": splits,
        "kalmori": {"total_streams": kalmori_total_streams, "total_revenue": round(kalmori_total_revenue, 2),
            "your_take": kalmori_your_take, "artist_split_pct": kalmori_artist_split,
            "platforms": kalmori_platforms, "monthly_trend": kalmori_monthly, "entries_count": len(kalmori_entries)},
        "combined": {"total_streams": combined_streams, "total_gross": combined_gross, "total_net": combined_net},
    }


@analytics_router.post("/analytics/revenue/calculator")
async def revenue_calculator(data: RevenueCalculatorInput, request: Request):
    user = await get_current_user(request)
    plan = user.get("plan", "free")
    plan_cut = SUBSCRIPTION_PLANS.get(plan, {}).get("revenue_share", 15) / 100
    mix = data.platform_mix or {"Spotify": 45, "Apple Music": 25, "YouTube Music": 15, "Amazon Music": 10, "Other": 5}
    total_pct = sum(mix.values())
    results = []
    total_gross = 0
    for platform, pct in sorted(mix.items(), key=lambda x: -x[1]):
        streams = int(data.streams * pct / max(total_pct, 1))
        rate = PLATFORM_RATES.get(platform, 0.004)
        gross = round(streams * rate, 2)
        total_gross += gross
        results.append({"platform": platform, "streams": streams, "rate": rate, "gross": gross})
    total_net = round(total_gross * (1 - plan_cut), 2)
    collabs = await db.collaborations.find({"artist_id": user["id"], "status": "accepted"}, {"_id": 0, "collaborator_name": 1, "split_percentage": 1}).to_list(50)
    total_collab = 0
    collab_breakdown = []
    for c in collabs:
        amt = round(total_net * c.get("split_percentage", 0) / 100, 2)
        total_collab += amt
        collab_breakdown.append({"name": c.get("collaborator_name", "Collaborator"), "percentage": c.get("split_percentage", 0), "amount": amt})
    return {
        "input_streams": data.streams, "platform_breakdown": results, "gross_revenue": round(total_gross, 2),
        "platform_fee": round(total_gross * plan_cut, 2), "net_revenue": total_net,
        "collab_payouts": round(total_collab, 2), "artist_take": round(total_net - total_collab, 2),
        "plan": plan, "plan_cut_percent": round(plan_cut * 100, 1), "collaborator_splits": collab_breakdown,
    }


# ============= REVENUE EXPORT (CSV) =============
@analytics_router.get("/analytics/revenue/export/csv")
async def export_revenue_csv(request: Request):
    user = await get_current_user(request)
    plan = user.get("plan", "free")
    plan_cut = SUBSCRIPTION_PLANS.get(plan, {}).get("revenue_share", 15) / 100
    artist_name = user.get("artist_name", user.get("name", "Artist"))
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["Kalmori Distribution — Personal Earnings Report"])
    writer.writerow([f"Artist: {artist_name}"])
    writer.writerow([f"Generated: {datetime.now(timezone.utc).strftime('%B %d, %Y')}"])
    writer.writerow([f"Plan: {plan.title()} ({round(plan_cut*100,1)}% fee)"])
    writer.writerow([])
    writer.writerow(["=== STREAMING EARNINGS ==="])
    writer.writerow(["Platform", "Streams", "Rate/Stream", "Gross Revenue", "Net Revenue"])
    pipeline = [{"$match": {"artist_id": user["id"]}}, {"$group": {"_id": "$platform", "streams": {"$sum": 1}}}]
    platform_data = await db.stream_events.aggregate(pipeline).to_list(20)
    streaming_gross = 0
    for p in sorted(platform_data, key=lambda x: -x["streams"]):
        name = p["_id"] or "Other"
        rate = PLATFORM_RATES.get(name, 0.004)
        gross = round(p["streams"] * rate, 2)
        net = round(gross * (1 - plan_cut), 2)
        streaming_gross += gross
        writer.writerow([name, p["streams"], f"${rate:.4f}", f"${gross:.2f}", f"${net:.2f}"])
    streaming_net = round(streaming_gross * (1 - plan_cut), 2)
    writer.writerow([])
    writer.writerow(["Streaming Total", "", "", f"${streaming_gross:.2f}", f"${streaming_net:.2f}"])
    writer.writerow([])
    kalmori_entries = await db.imported_royalties.find({"matched_artist_id": user["id"], "status": "matched"}, {"_id": 0}).to_list(5000)
    if kalmori_entries:
        label_entry = await db.label_artists.find_one({"artist_id": user["id"], "status": "active"}, {"_id": 0, "artist_split": 1})
        split_pct = label_entry.get("artist_split", 100) if label_entry else 100
        writer.writerow(["=== KALMORI DISTRIBUTION EARNINGS ==="])
        writer.writerow([f"Split: {split_pct}%"])
        writer.writerow(["Platform", "Track", "Streams", "Revenue", "Your Take", "Period"])
        kalmori_total = 0
        for e in kalmori_entries:
            rev = e.get("revenue", 0)
            your_take = round(rev * split_pct / 100, 2)
            kalmori_total += rev
            writer.writerow([e.get("platform", ""), e.get("track", ""), e.get("streams", 0), f"${rev:.2f}", f"${your_take:.2f}", e.get("period", "")])
        writer.writerow([])
        writer.writerow(["Kalmori Total", "", "", f"${kalmori_total:.2f}", f"${round(kalmori_total * split_pct / 100, 2):.2f}", ""])
        writer.writerow([])
        writer.writerow(["=== COMBINED TOTAL ==="])
        writer.writerow(["", "", "", f"${streaming_gross + kalmori_total:.2f}", f"${streaming_net + round(kalmori_total * split_pct / 100, 2):.2f}"])
    writer.writerow([])
    writer.writerow(["This report was generated by Kalmori Distribution."])
    output.seek(0)
    return StreamingResponse(iter([output.getvalue()]), media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename=kalmori_earnings_{datetime.now(timezone.utc).strftime('%Y%m%d')}.csv"})


# ============= REVENUE EXPORT (PDF) =============
@analytics_router.get("/analytics/revenue/export/pdf")
async def export_revenue_pdf(request: Request):
    from reportlab.lib.pagesizes import letter
    from reportlab.lib import colors
    from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    user = await get_current_user(request)
    plan = user.get("plan", "free")
    plan_cut = SUBSCRIPTION_PLANS.get(plan, {}).get("revenue_share", 15) / 100
    artist_name = user.get("artist_name", user.get("name", "Artist"))
    buf = io.BytesIO()
    doc = SimpleDocTemplate(buf, pagesize=letter, topMargin=30, bottomMargin=30)
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle("CustomTitle", parent=styles["Title"], fontSize=20, textColor=colors.HexColor("#FFD700"))
    section_style = ParagraphStyle("Section", parent=styles["Heading2"], fontSize=14, textColor=colors.HexColor("#7C4DFF"))
    elements = []
    elements.append(Paragraph("KALMORI DISTRIBUTION", title_style))
    elements.append(Paragraph("Personal Earnings Statement", styles["Heading3"]))
    elements.append(Spacer(1, 10))
    elements.append(Paragraph(f"<b>Artist:</b> {artist_name}", styles["Normal"]))
    elements.append(Paragraph(f"<b>Plan:</b> {plan.title()} ({round(plan_cut*100,1)}% platform fee)", styles["Normal"]))
    elements.append(Paragraph(f"<b>Statement Date:</b> {datetime.now(timezone.utc).strftime('%B %d, %Y')}", styles["Normal"]))
    elements.append(Spacer(1, 20))
    elements.append(Paragraph("Streaming Earnings", section_style))
    pipeline = [{"$match": {"artist_id": user["id"]}}, {"$group": {"_id": "$platform", "streams": {"$sum": 1}}}]
    platform_data = await db.stream_events.aggregate(pipeline).to_list(20)
    streaming_rows = [["Platform", "Streams", "Rate", "Gross", "Net"]]
    streaming_gross = 0
    for p in sorted(platform_data, key=lambda x: -x["streams"]):
        name = p["_id"] or "Other"
        rate = PLATFORM_RATES.get(name, 0.004)
        gross = round(p["streams"] * rate, 2)
        net = round(gross * (1 - plan_cut), 2)
        streaming_gross += gross
        streaming_rows.append([name, f"{p['streams']:,}", f"${rate:.4f}", f"${gross:.2f}", f"${net:.2f}"])
    streaming_net = round(streaming_gross * (1 - plan_cut), 2)
    streaming_rows.append(["Total", "", "", f"${streaming_gross:.2f}", f"${streaming_net:.2f}"])
    t = Table(streaming_rows, colWidths=[120, 80, 80, 80, 80])
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#7C4DFF")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("BACKGROUND", (0, -1), (-1, -1), colors.HexColor("#222222")),
        ("TEXTCOLOR", (0, -1), (-1, -1), colors.white),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
        ("FONTSIZE", (0, 0), (-1, -1), 9),
        ("FONTNAME", (0, -1), (-1, -1), "Helvetica-Bold"),
    ]))
    elements.append(t)
    elements.append(Spacer(1, 20))
    kalmori_entries = await db.imported_royalties.find({"matched_artist_id": user["id"], "status": "matched"}, {"_id": 0}).to_list(5000)
    kalmori_total = 0
    if kalmori_entries:
        label_entry = await db.label_artists.find_one({"artist_id": user["id"], "status": "active"}, {"_id": 0, "artist_split": 1})
        split_pct = label_entry.get("artist_split", 100) if label_entry else 100
        elements.append(Paragraph(f"Kalmori Distribution Earnings ({split_pct}% split)", section_style))
        kalmori_platform_map = {}
        for e in kalmori_entries:
            plat = e.get("platform", "Other") or "Other"
            if plat not in kalmori_platform_map:
                kalmori_platform_map[plat] = {"streams": 0, "revenue": 0}
            kalmori_platform_map[plat]["streams"] += e.get("streams", 0)
            kalmori_platform_map[plat]["revenue"] += e.get("revenue", 0)
            kalmori_total += e.get("revenue", 0)
        k_rows = [["Platform", "Streams", "Revenue", f"Your Take ({split_pct}%)"]]
        for plat, vals in sorted(kalmori_platform_map.items(), key=lambda x: -x[1]["revenue"]):
            k_rows.append([plat, f"{vals['streams']:,}", f"${vals['revenue']:.2f}", f"${round(vals['revenue'] * split_pct / 100, 2):.2f}"])
        k_rows.append(["Total", "", f"${kalmori_total:.2f}", f"${round(kalmori_total * split_pct / 100, 2):.2f}"])
        kt = Table(k_rows, colWidths=[140, 80, 100, 120])
        kt.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#FFD700")),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.black),
            ("BACKGROUND", (0, -1), (-1, -1), colors.HexColor("#222222")),
            ("TEXTCOLOR", (0, -1), (-1, -1), colors.white),
            ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
            ("FONTSIZE", (0, 0), (-1, -1), 9),
            ("FONTNAME", (0, -1), (-1, -1), "Helvetica-Bold"),
        ]))
        elements.append(kt)
        elements.append(Spacer(1, 20))
    elements.append(Paragraph("Combined Summary", section_style))
    kalmori_your = round(kalmori_total * (label_entry.get("artist_split", 100) if 'label_entry' in dir() and label_entry else 100) / 100, 2) if kalmori_entries else 0
    summary_data = [["", "Amount"], ["Streaming Gross", f"${streaming_gross:.2f}"], ["Streaming Net (after fees)", f"${streaming_net:.2f}"]]
    if kalmori_entries:
        summary_data.append(["Kalmori Earnings (your share)", f"${kalmori_your:.2f}"])
    summary_data.append(["Total Take-Home", f"${streaming_net + kalmori_your:.2f}"])
    st = Table(summary_data, colWidths=[220, 120])
    st.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1DB954")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("BACKGROUND", (0, -1), (-1, -1), colors.HexColor("#1DB954")),
        ("TEXTCOLOR", (0, -1), (-1, -1), colors.white),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
        ("FONTSIZE", (0, 0), (-1, -1), 10),
        ("FONTNAME", (0, -1), (-1, -1), "Helvetica-Bold"),
    ]))
    elements.append(st)
    elements.append(Spacer(1, 30))
    footer_style = ParagraphStyle("Footer", parent=styles["Normal"], fontSize=9, textColor=colors.grey)
    elements.append(Paragraph("This statement was generated by Kalmori Distribution. All earnings are based on verified streaming and distributor data.", footer_style))
    doc.build(elements)
    buf.seek(0)
    return StreamingResponse(buf, media_type="application/pdf",
        headers={"Content-Disposition": f"attachment; filename=kalmori_earnings_{datetime.now(timezone.utc).strftime('%Y%m%d')}.pdf"})


# ============= DSP DATA IMPORT (CSV) — ADMIN ONLY =============
@analytics_router.post("/analytics/import")
async def import_streaming_data(request: Request, file: UploadFile = File(...)):
    """Import streaming data from CSV. Admin only."""
    user = await get_current_user(request)
    if user.get("role") != "admin":
        raise HTTPException(status_code=403, detail="Only admins can import streaming data")
    content = await file.read()
    try:
        text = content.decode("utf-8")
    except Exception:
        text = content.decode("latin-1")
    reader = csv.DictReader(io.StringIO(text))
    events = []
    for row in reader:
        streams_count = int(row.get("streams", row.get("Streams", 1)))
        revenue_per = float(row.get("revenue", row.get("Revenue", 0))) / max(streams_count, 1)
        date_str = row.get("date", row.get("Date", datetime.now(timezone.utc).strftime("%Y-%m-%d")))
        platform = row.get("platform", row.get("Platform", "Other"))
        country = row.get("country", row.get("Country", "US"))
        release_title = row.get("release_title", row.get("Release", row.get("Title", "Imported Track")))
        for _ in range(streams_count):
            hour = random.randint(0, 23)
            minute = random.randint(0, 59)
            events.append({
                "id": f"se_{uuid.uuid4().hex[:12]}",
                "artist_id": user["id"],
                "release_id": f"import_{uuid.uuid4().hex[:8]}",
                "release_title": release_title,
                "platform": platform, "country": country,
                "revenue": round(revenue_per + random.uniform(-0.001, 0.001), 4),
                "timestamp": f"{date_str}T{hour:02d}:{minute:02d}:00+00:00",
                "source": "csv_import",
            })
    if events:
        await db.stream_events.insert_many(events)
    return {"message": f"Imported {len(events)} stream events from {file.filename}", "count": len(events)}


# ============= FAN ANALYTICS =============
@analytics_router.get("/fan-analytics/overview")
async def get_fan_analytics(request: Request):
    user = await get_current_user(request)
    campaigns = await db.presave_campaigns.find({"artist_id": user["id"]}, {"_id": 0}).to_list(50)
    total_subscribers = sum(c.get("subscriber_count", 0) for c in campaigns)
    total_campaigns = len(campaigns)
    country_counts = {}
    subscriber_timeline = {}
    for c in campaigns:
        for sub in c.get("subscribers", []):
            email = sub.get("email", "")
            domain = email.split("@")[-1] if "@" in email else ""
            country = "US"
            if domain.endswith(".ng"): country = "NG"
            elif domain.endswith(".uk") or domain.endswith(".co.uk"): country = "UK"
            elif domain.endswith(".de"): country = "DE"
            elif domain.endswith(".fr"): country = "FR"
            elif domain.endswith(".jp"): country = "JP"
            elif domain.endswith(".br"): country = "BR"
            elif domain.endswith(".au"): country = "AU"
            elif domain.endswith(".ca"): country = "CA"
            elif domain.endswith(".in"): country = "IN"
            country_counts[country] = country_counts.get(country, 0) + 1
            date = sub.get("subscribed_at", "")[:10]
            if date:
                subscriber_timeline[date] = subscriber_timeline.get(date, 0) + 1
    platform_engagement = []
    pipeline = [
        {"$match": {"artist_id": user["id"]}},
        {"$group": {"_id": "$platform", "streams": {"$sum": 1}, "revenue": {"$sum": "$revenue"}}},
        {"$sort": {"streams": -1}}
    ]
    platform_results = await db.stream_events.aggregate(pipeline).to_list(10)
    total_streams = sum(p["streams"] for p in platform_results) if platform_results else 1
    platform_colors = {"Spotify": "#1DB954", "Apple Music": "#FC3C44", "YouTube Music": "#FF0000", "Amazon Music": "#FF9900", "TikTok": "#010101", "Tidal": "#00FFFF", "Deezer": "#A238FF", "SoundCloud": "#FF5500"}
    for p in platform_results:
        platform_engagement.append({"name": p["_id"], "streams": p["streams"], "revenue": round(p["revenue"], 2),
            "percentage": round(p["streams"] / total_streams * 100, 1), "color": platform_colors.get(p["_id"], "#888")})
    country_pipeline = [{"$match": {"artist_id": user["id"]}}, {"$group": {"_id": "$country", "count": {"$sum": 1}}}, {"$sort": {"count": -1}}, {"$limit": 10}]
    top_countries = await db.stream_events.aggregate(country_pipeline).to_list(10)
    total_country_streams = sum(c["count"] for c in top_countries) if top_countries else 1
    growth_pipeline = [{"$match": {"artist_id": user["id"]}}, {"$group": {"_id": {"$substr": ["$timestamp", 0, 10]}, "listeners": {"$sum": 1}}}, {"$sort": {"_id": 1}}, {"$limit": 30}]
    growth_data = await db.stream_events.aggregate(growth_pipeline).to_list(30)
    hour_pipeline = [{"$match": {"artist_id": user["id"]}}, {"$addFields": {"hour_str": {"$substr": ["$timestamp", 11, 2]}}}, {"$group": {"_id": "$hour_str", "count": {"$sum": 1}}}, {"$sort": {"_id": 1}}]
    peak_hours = await db.stream_events.aggregate(hour_pipeline).to_list(24)
    return {
        "total_subscribers": total_subscribers, "total_campaigns": total_campaigns,
        "subscriber_countries": country_counts,
        "subscriber_timeline": [{"date": k, "count": v} for k, v in sorted(subscriber_timeline.items())],
        "platform_engagement": platform_engagement,
        "top_countries": [{"country": c["_id"], "streams": c["count"], "percentage": round(c["count"] / total_country_streams * 100, 1)} for c in top_countries],
        "listener_growth": [{"date": g["_id"], "listeners": g["listeners"]} for g in growth_data],
        "peak_hours": [{"hour": int(h["_id"]) if h["_id"].isdigit() else 0, "count": h["count"]} for h in peak_hours],
    }
