"""Label Routes - Dashboard, Roster, Royalty Splits, Payout Export"""
from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import Optional
from datetime import datetime, timezone, timedelta
import uuid
import logging
import csv as csv_module
import io

from core import db, get_current_user

logger = logging.getLogger(__name__)

label_router = APIRouter(prefix="/api/label")


# ============= MODELS =============

class InviteArtistInput(BaseModel):
    email: str

class SetSplitInput(BaseModel):
    artist_split: float
    label_split: float


# ============= DASHBOARD =============

@label_router.get("/dashboard")
async def label_dashboard(request: Request):
    user = await get_current_user(request)
    roster = await db.label_artists.find({"label_id": user["id"], "status": "active"}, {"_id": 0}).to_list(200)
    artist_ids = [r["artist_id"] for r in roster]
    if not artist_ids:
        return {
            "total_artists": 0, "total_streams": 0, "total_revenue": 0, "total_releases": 0,
            "week_streams": 0, "platform_breakdown": [], "country_breakdown": [], "top_artists": [], "recent_releases": []
        }
    now = datetime.now(timezone.utc)
    week_ago = (now - timedelta(days=7)).isoformat()
    total_result = await db.stream_events.aggregate([
        {"$match": {"artist_id": {"$in": artist_ids}}},
        {"$group": {"_id": None, "total": {"$sum": 1}, "revenue": {"$sum": {"$ifNull": ["$revenue", 0]}}}}
    ]).to_list(1)
    total_streams = total_result[0]["total"] if total_result else 0
    total_revenue = round(total_result[0].get("revenue", 0) if total_result else 0, 2)
    week_streams = await db.stream_events.count_documents({"artist_id": {"$in": artist_ids}, "timestamp": {"$gte": week_ago}})
    total_releases = await db.releases.count_documents({"artist_id": {"$in": artist_ids}})
    platform_data = await db.stream_events.aggregate([
        {"$match": {"artist_id": {"$in": artist_ids}}},
        {"$group": {"_id": "$platform", "count": {"$sum": 1}, "revenue": {"$sum": {"$ifNull": ["$revenue", 0]}}}},
        {"$sort": {"count": -1}}, {"$limit": 8}
    ]).to_list(8)
    country_data = await db.stream_events.aggregate([
        {"$match": {"artist_id": {"$in": artist_ids}}},
        {"$group": {"_id": "$country", "count": {"$sum": 1}}},
        {"$sort": {"count": -1}}, {"$limit": 8}
    ]).to_list(8)
    top_artists_raw = await db.stream_events.aggregate([
        {"$match": {"artist_id": {"$in": artist_ids}}},
        {"$group": {"_id": "$artist_id", "streams": {"$sum": 1}, "revenue": {"$sum": {"$ifNull": ["$revenue", 0]}}}},
        {"$sort": {"streams": -1}}, {"$limit": 10}
    ]).to_list(10)
    top_artists = []
    for a in top_artists_raw:
        u = await db.users.find_one({"id": a["_id"]}, {"_id": 0, "id": 1, "name": 1, "artist_name": 1, "plan": 1, "avatar_url": 1})
        if u:
            rel_count = await db.releases.count_documents({"artist_id": a["_id"]})
            top_artists.append({**u, "streams": a["streams"], "revenue": round(a.get("revenue", 0), 2), "releases": rel_count})
    recent_releases = await db.releases.find(
        {"artist_id": {"$in": artist_ids}},
        {"_id": 0, "id": 1, "title": 1, "artist_id": 1, "release_type": 1, "status": 1, "genre": 1, "created_at": 1, "cover_art_url": 1}
    ).sort("created_at", -1).to_list(10)
    for r in recent_releases:
        u = await db.users.find_one({"id": r["artist_id"]}, {"_id": 0, "artist_name": 1})
        r["artist_name"] = u.get("artist_name", "Unknown") if u else "Unknown"
    return {
        "total_artists": len(artist_ids), "total_streams": total_streams,
        "total_revenue": total_revenue, "total_releases": total_releases,
        "week_streams": week_streams,
        "platform_breakdown": [{"platform": p["_id"], "streams": p["count"], "revenue": round(p.get("revenue", 0), 2)} for p in platform_data],
        "country_breakdown": [{"country": c["_id"], "streams": c["count"]} for c in country_data],
        "top_artists": top_artists, "recent_releases": recent_releases,
    }


# ============= ROSTER =============

@label_router.get("/artists")
async def label_get_artists(request: Request):
    user = await get_current_user(request)
    roster = await db.label_artists.find({"label_id": user["id"]}, {"_id": 0}).to_list(200)
    artists = []
    for entry in roster:
        u = await db.users.find_one({"id": entry["artist_id"]}, {"_id": 0, "password_hash": 0})
        if not u: continue
        stream_result = await db.stream_events.aggregate([
            {"$match": {"artist_id": entry["artist_id"]}},
            {"$group": {"_id": None, "streams": {"$sum": 1}, "revenue": {"$sum": {"$ifNull": ["$revenue", 0]}}}}
        ]).to_list(1)
        rel_count = await db.releases.count_documents({"artist_id": entry["artist_id"]})
        artists.append({
            "id": u["id"], "name": u.get("name"), "artist_name": u.get("artist_name"),
            "email": u.get("email"), "plan": u.get("plan"), "avatar_url": u.get("avatar_url"),
            "status": entry.get("status", "active"), "added_at": entry.get("added_at"),
            "streams": stream_result[0]["streams"] if stream_result else 0,
            "revenue": round(stream_result[0].get("revenue", 0) if stream_result else 0, 2),
            "releases": rel_count,
        })
    return {"artists": artists, "total": len(artists)}

@label_router.post("/artists/invite")
async def label_invite_artist(data: InviteArtistInput, request: Request):
    user = await get_current_user(request)
    artist = await db.users.find_one({"email": data.email}, {"_id": 0, "id": 1, "name": 1, "artist_name": 1})
    if not artist:
        raise HTTPException(status_code=404, detail="No user found with that email. They need to create a Kalmori account first.")
    if artist["id"] == user["id"]:
        raise HTTPException(status_code=400, detail="You cannot add yourself to your roster")
    existing = await db.label_artists.find_one({"label_id": user["id"], "artist_id": artist["id"]})
    if existing:
        raise HTTPException(status_code=409, detail="This artist is already on your roster")
    await db.label_artists.insert_one({
        "id": f"la_{uuid.uuid4().hex[:12]}",
        "label_id": user["id"], "artist_id": artist["id"],
        "status": "active", "added_at": datetime.now(timezone.utc).isoformat()
    })
    return {"message": f"Added {artist.get('artist_name', artist.get('name'))} to your roster", "artist_id": artist["id"]}

@label_router.delete("/artists/{artist_id}")
async def label_remove_artist(artist_id: str, request: Request):
    user = await get_current_user(request)
    result = await db.label_artists.delete_one({"label_id": user["id"], "artist_id": artist_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Artist not found on your roster")
    return {"message": "Artist removed from roster"}


# ============= ROYALTY SPLITS =============

@label_router.put("/artists/{artist_id}/split")
async def label_set_royalty_split(artist_id: str, data: SetSplitInput, request: Request):
    user = await get_current_user(request)
    if abs((data.artist_split + data.label_split) - 100) > 0.01:
        raise HTTPException(status_code=400, detail="Splits must add up to 100%")
    if data.artist_split < 0 or data.label_split < 0:
        raise HTTPException(status_code=400, detail="Splits cannot be negative")
    result = await db.label_artists.update_one(
        {"label_id": user["id"], "artist_id": artist_id, "status": "active"},
        {"$set": {"artist_split": data.artist_split, "label_split": data.label_split, "split_updated_at": datetime.now(timezone.utc).isoformat()}}
    )
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Artist not found on your roster")
    return {"message": "Royalty split updated", "artist_split": data.artist_split, "label_split": data.label_split}

@label_router.get("/royalties")
async def label_get_royalties(request: Request):
    user = await get_current_user(request)
    roster = await db.label_artists.find({"label_id": user["id"], "status": "active"}, {"_id": 0}).to_list(200)
    total_label_earnings = 0
    total_artist_payouts = 0
    total_revenue = 0
    artists_data = []
    for entry in roster:
        a_id = entry["artist_id"]
        artist_split = entry.get("artist_split", 70)
        label_split = entry.get("label_split", 30)
        rev_result = await db.stream_events.aggregate([
            {"$match": {"artist_id": a_id, "revenue": {"$exists": True}}},
            {"$group": {"_id": None, "total": {"$sum": "$revenue"}, "streams": {"$sum": 1}}}
        ]).to_list(1)
        gross_revenue = round(rev_result[0]["total"] if rev_result else 0, 2)
        streams = rev_result[0]["streams"] if rev_result else 0
        now = datetime.now(timezone.utc)
        monthly = []
        for m in range(6):
            end = now - timedelta(days=30 * m)
            start = end - timedelta(days=30)
            m_result = await db.stream_events.aggregate([
                {"$match": {"artist_id": a_id, "revenue": {"$exists": True}, "timestamp": {"$gte": start.isoformat(), "$lt": end.isoformat()}}},
                {"$group": {"_id": None, "total": {"$sum": "$revenue"}}}
            ]).to_list(1)
            m_rev = round(m_result[0]["total"] if m_result else 0, 2)
            monthly.append({"month": end.strftime("%b"), "revenue": m_rev, "artist_share": round(m_rev * artist_split / 100, 2), "label_share": round(m_rev * label_split / 100, 2)})
        monthly.reverse()
        artist_earnings = round(gross_revenue * artist_split / 100, 2)
        label_earnings = round(gross_revenue * label_split / 100, 2)
        total_label_earnings += label_earnings
        total_artist_payouts += artist_earnings
        total_revenue += gross_revenue
        u = await db.users.find_one({"id": a_id}, {"_id": 0, "id": 1, "name": 1, "artist_name": 1, "avatar_url": 1, "plan": 1})
        if u:
            artists_data.append({
                **u, "streams": streams, "gross_revenue": gross_revenue,
                "artist_split": artist_split, "label_split": label_split,
                "artist_earnings": artist_earnings, "label_earnings": label_earnings, "monthly": monthly,
            })
    return {
        "summary": {
            "total_revenue": round(total_revenue, 2),
            "total_artist_payouts": round(total_artist_payouts, 2),
            "total_label_earnings": round(total_label_earnings, 2),
            "artist_count": len(artists_data),
        },
        "artists": artists_data,
    }


# ============= PAYOUT EXPORT =============

@label_router.get("/royalties/export/csv")
async def label_export_csv(request: Request):
    user = await get_current_user(request)
    roster = await db.label_artists.find({"label_id": user["id"], "status": "active"}, {"_id": 0}).to_list(200)
    artist_ids = [r["artist_id"] for r in roster]
    splits = {r["artist_id"]: {"a": r.get("artist_split", 70), "l": r.get("label_split", 30)} for r in roster}
    output = io.StringIO()
    writer = csv_module.writer(output)
    writer.writerow(["Kalmori Distribution — Payout Report"])
    writer.writerow([f"Generated: {datetime.now(timezone.utc).strftime('%B %d, %Y')}"])
    writer.writerow([])
    writer.writerow(["Artist", "Platform", "Country", "Streams", "Gross Revenue", "Artist %", "Artist Earnings", "Label %", "Label Earnings", "Period"])
    for a_id in artist_ids:
        u = await db.users.find_one({"id": a_id}, {"_id": 0, "artist_name": 1, "name": 1})
        name = u.get("artist_name", u.get("name", "Unknown")) if u else "Unknown"
        sp = splits.get(a_id, {"a": 70, "l": 30})
        pipeline = [
            {"$match": {"artist_id": a_id}},
            {"$group": {"_id": {"platform": "$platform", "country": "$country"}, "streams": {"$sum": 1}, "revenue": {"$sum": {"$ifNull": ["$revenue", 0]}}}}
        ]
        data = await db.stream_events.aggregate(pipeline).to_list(500)
        for d in data:
            rev = round(d.get("revenue", 0), 4)
            writer.writerow([name, d["_id"].get("platform", ""), d["_id"].get("country", ""), d["streams"], f"{rev:.4f}", f"{sp['a']}%", f"{round(rev * sp['a']/100, 4):.4f}", f"{sp['l']}%", f"{round(rev * sp['l']/100, 4):.4f}", datetime.now(timezone.utc).strftime("%Y-%m")])
        imported = await db.imported_royalties.find({"matched_artist_id": a_id}, {"_id": 0}).to_list(500)
        for imp in imported:
            rev = imp.get("revenue", 0)
            writer.writerow([name, imp.get("platform", ""), imp.get("country", ""), imp.get("streams", 0), f"{rev:.4f}", f"{sp['a']}%", f"{round(rev * sp['a']/100, 4):.4f}", f"{sp['l']}%", f"{round(rev * sp['l']/100, 4):.4f}", imp.get("period", "")])
    output.seek(0)
    return StreamingResponse(
        iter([output.getvalue()]), media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename=kalmori_payout_report_{datetime.now(timezone.utc).strftime('%Y%m%d')}.csv"}
    )

@label_router.get("/royalties/export/pdf")
async def label_export_pdf(request: Request):
    from reportlab.lib.pagesizes import letter, landscape
    from reportlab.lib import colors
    from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle

    user = await get_current_user(request)
    roster = await db.label_artists.find({"label_id": user["id"], "status": "active"}, {"_id": 0}).to_list(200)
    splits = {r["artist_id"]: {"a": r.get("artist_split", 70), "l": r.get("label_split", 30)} for r in roster}
    buf = io.BytesIO()
    doc = SimpleDocTemplate(buf, pagesize=landscape(letter), topMargin=30, bottomMargin=30)
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle("Title", parent=styles["Title"], fontSize=18, textColor=colors.HexColor("#7C4DFF"))
    elements = []
    elements.append(Paragraph("KALMORI DISTRIBUTION", title_style))
    elements.append(Paragraph("Official Royalty Payout Statement", styles["Heading3"]))
    elements.append(Paragraph(f"Statement Date: {datetime.now(timezone.utc).strftime('%B %d, %Y')}", styles["Normal"]))
    elements.append(Spacer(1, 20))
    total_gross = 0
    total_artist = 0
    total_label = 0
    for entry in roster:
        a_id = entry["artist_id"]
        sp = splits.get(a_id, {"a": 70, "l": 30})
        u = await db.users.find_one({"id": a_id}, {"_id": 0, "artist_name": 1, "name": 1})
        name = u.get("artist_name", u.get("name", "Unknown")) if u else "Unknown"
        rev_result = await db.stream_events.aggregate([
            {"$match": {"artist_id": a_id, "revenue": {"$exists": True}}},
            {"$group": {"_id": None, "total": {"$sum": "$revenue"}, "streams": {"$sum": 1}}}
        ]).to_list(1)
        gross = round(rev_result[0]["total"] if rev_result else 0, 2)
        streams = rev_result[0]["streams"] if rev_result else 0
        imp_result = await db.imported_royalties.aggregate([
            {"$match": {"matched_artist_id": a_id}},
            {"$group": {"_id": None, "total": {"$sum": "$revenue"}, "streams": {"$sum": "$streams"}}}
        ]).to_list(1)
        gross += round(imp_result[0]["total"] if imp_result else 0, 2)
        streams += imp_result[0]["streams"] if imp_result else 0
        artist_earn = round(gross * sp["a"] / 100, 2)
        label_earn = round(gross * sp["l"] / 100, 2)
        total_gross += gross
        total_artist += artist_earn
        total_label += label_earn
        elements.append(Paragraph(f"<b>{name}</b> — Split: {sp['a']}% Artist / {sp['l']}% Label", styles["Heading3"]))
        data = [["Metric", "Value"], ["Total Streams", f"{streams:,}"], ["Gross Revenue", f"${gross:.2f}"], ["Artist Earnings", f"${artist_earn:.2f}"], ["Label Earnings", f"${label_earn:.2f}"]]
        t = Table(data, colWidths=[200, 200])
        t.setStyle(TableStyle([("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#7C4DFF")), ("TEXTCOLOR", (0, 0), (-1, 0), colors.white), ("GRID", (0, 0), (-1, -1), 0.5, colors.grey), ("FONTSIZE", (0, 0), (-1, -1), 10)]))
        elements.append(t)
        elements.append(Spacer(1, 15))
    elements.append(Spacer(1, 10))
    elements.append(Paragraph("<b>Summary</b>", styles["Heading2"]))
    summary = [["", "Amount"], ["Total Gross Revenue", f"${total_gross:.2f}"], ["Total Artist Payouts", f"${total_artist:.2f}"], ["Total Label Earnings", f"${total_label:.2f}"]]
    st = Table(summary, colWidths=[200, 200])
    st.setStyle(TableStyle([("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#FFD700")), ("TEXTCOLOR", (0, 0), (-1, 0), colors.black), ("GRID", (0, 0), (-1, -1), 0.5, colors.grey), ("FONTSIZE", (0, 0), (-1, -1), 11), ("FONTNAME", (0, 1), (-1, -1), "Helvetica-Bold")]))
    elements.append(st)
    elements.append(Spacer(1, 30))
    footer_style = ParagraphStyle("Footer", parent=styles["Normal"], fontSize=9, textColor=colors.grey)
    elements.append(Paragraph("This statement was generated by Kalmori Distribution. All earnings are calculated based on verified streaming data and agreed royalty split terms.", footer_style))
    doc.build(elements)
    buf.seek(0)
    return StreamingResponse(
        buf, media_type="application/pdf",
        headers={"Content-Disposition": f"attachment; filename=kalmori_payout_report_{datetime.now(timezone.utc).strftime('%Y%m%d')}.pdf"}
    )
