"""AI Features - Metadata suggestions, descriptions, analytics insights, release strategy"""
from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime, timezone, timedelta
import os
import uuid
import logging
import json

logger = logging.getLogger(__name__)

ai_router = APIRouter(prefix="/api/ai")

EMERGENT_KEY = os.environ.get("EMERGENT_LLM_KEY")

async def _get_user_from_request(request: Request):
    from server import get_current_user
    return await get_current_user(request)

class MetadataSuggestRequest(BaseModel):
    title: str
    genre: Optional[str] = None
    mood: Optional[str] = None

class DescriptionRequest(BaseModel):
    title: str
    artist_name: str
    genre: Optional[str] = None
    track_count: Optional[int] = 1

@ai_router.get("/analytics-insights")
async def get_analytics_insights(request: Request):
    user = await _get_user_from_request(request)
    try:
        from emergentintegrations.llm.chat import LlmChat, UserMessage
        chat = LlmChat(
            api_key=EMERGENT_KEY,
            session_id=f"insights_{user['id']}_{uuid.uuid4().hex[:8]}",
            system_message="You are a music industry analytics expert. Provide concise, actionable insights for independent artists based on their streaming data. Keep responses under 200 words. Use bullet points."
        ).with_model("openai", "gpt-4o")
        
        from motor.motor_asyncio import AsyncIOMotorClient
        db_client = AsyncIOMotorClient(os.environ['MONGO_URL'])
        db = db_client[os.environ['DB_NAME']]
        
        releases = await db.releases.find({"artist_id": user["id"]}).to_list(50)
        release_count = len(releases)
        genres = list(set(r.get("genre", "Unknown") for r in releases))
        
        prompt = f"""Analyze this artist's profile and provide strategic insights:
- Releases: {release_count}
- Genres: {', '.join(genres) if genres else 'Not specified'}
- Plan: {user.get('plan', 'free')}

Provide insights on:
1. Release strategy recommendations
2. Potential audience growth tactics
3. Revenue optimization tips
4. Platform-specific strategies (Spotify, Apple Music, TikTok)"""
        
        msg = UserMessage(text=prompt)
        response = await chat.send_message(msg)
        db_client.close()
        return {"insights": response}
    except Exception as e:
        logger.error(f"AI insights error: {e}")
        return {"insights": "AI insights are temporarily unavailable. Here are general tips:\n\n- Release consistently (every 4-6 weeks)\n- Optimize metadata for discoverability\n- Engage with playlists on Spotify and Apple Music\n- Use TikTok to promote snippets before release\n- Collaborate with other artists in your genre"}

@ai_router.post("/metadata-suggestions")
async def get_metadata_suggestions(data: MetadataSuggestRequest, request: Request):
    await _get_user_from_request(request)
    try:
        from emergentintegrations.llm.chat import LlmChat, UserMessage
        chat = LlmChat(
            api_key=EMERGENT_KEY,
            session_id=f"metadata_{uuid.uuid4().hex[:8]}",
            system_message="You are a music metadata expert. Return JSON only, no markdown. Suggest optimal metadata for music releases to maximize discoverability on streaming platforms."
        ).with_model("openai", "gpt-4o")
        
        prompt = f"""Suggest metadata for a music release:
Title: {data.title}
Genre: {data.genre or 'Not specified'}
Mood: {data.mood or 'Not specified'}

Return a JSON object with these fields:
{{"suggested_genres": ["primary genre", "sub-genre"], "suggested_moods": ["mood1", "mood2", "mood3"], "suggested_tags": ["tag1", "tag2", "tag3", "tag4", "tag5"], "suggested_description": "A 1-2 sentence description", "suggested_language": "language code", "suggested_bpm_range": "e.g. 120-130"}}"""
        
        msg = UserMessage(text=prompt)
        response = await chat.send_message(msg)
        
        import json
        try:
            clean = response.strip()
            if clean.startswith("```"):
                clean = clean.split("\n", 1)[1].rsplit("```", 1)[0]
            suggestions = json.loads(clean)
        except Exception:
            suggestions = {
                "suggested_genres": [data.genre or "Pop"], "suggested_moods": [data.mood or "Energetic"],
                "suggested_tags": [data.title.lower()], "suggested_description": f"A {data.genre or 'new'} release: {data.title}",
                "suggested_language": "en", "suggested_bpm_range": "100-140", "raw_response": response
            }
        return suggestions
    except Exception as e:
        logger.error(f"AI metadata error: {e}")
        return {"suggested_genres": [data.genre or "Pop"], "suggested_moods": [data.mood or "Energetic"],
                "suggested_tags": [data.title.lower(), "new release", "indie"], "suggested_description": f"{data.title} - a fresh release",
                "suggested_language": "en", "suggested_bpm_range": "100-140"}

@ai_router.post("/generate-description")
async def generate_description(data: DescriptionRequest, request: Request):
    await _get_user_from_request(request)
    try:
        from emergentintegrations.llm.chat import LlmChat, UserMessage
        chat = LlmChat(
            api_key=EMERGENT_KEY,
            session_id=f"desc_{uuid.uuid4().hex[:8]}",
            system_message="You are a music marketing copywriter. Write compelling, concise descriptions for music releases. Keep it under 100 words."
        ).with_model("openai", "gpt-4o")
        
        prompt = f"Write a compelling release description for:\nTitle: {data.title}\nArtist: {data.artist_name}\nGenre: {data.genre or 'Various'}\nTracks: {data.track_count}"
        msg = UserMessage(text=prompt)
        response = await chat.send_message(msg)
        return {"description": response}
    except Exception as e:
        logger.error(f"AI description error: {e}")
        return {"description": f"{data.title} by {data.artist_name} - an exciting new {data.genre or ''} release."}


class ReleaseStrategyRequest(BaseModel):
    release_title: Optional[str] = None
    genre: Optional[str] = None

class SaveStrategyRequest(BaseModel):
    strategy: dict
    data_summary: dict
    release_title: Optional[str] = None
    genre: Optional[str] = None
    label: Optional[str] = None

@ai_router.post("/release-strategy")
async def get_release_strategy(data: ReleaseStrategyRequest, request: Request):
    """Generate AI-powered release strategy based on fan analytics data"""
    user = await _get_user_from_request(request)
    
    from motor.motor_asyncio import AsyncIOMotorClient
    db_client = AsyncIOMotorClient(os.environ['MONGO_URL'])
    db = db_client[os.environ['DB_NAME']]
    
    try:
        # Gather fan analytics data
        # 1. Platform engagement
        platform_pipeline = [
            {"$match": {"artist_id": user["id"]}},
            {"$group": {"_id": "$platform", "streams": {"$sum": 1}, "revenue": {"$sum": "$revenue"}}},
            {"$sort": {"streams": -1}}
        ]
        platform_results = await db.stream_events.aggregate(platform_pipeline).to_list(10)
        total_streams = sum(p["streams"] for p in platform_results) if platform_results else 0
        platforms_data = []
        for p in platform_results:
            pct = round(p["streams"] / max(total_streams, 1) * 100, 1)
            platforms_data.append(f"{p['_id']}: {p['streams']} streams ({pct}%)")
        
        # 2. Top countries
        country_pipeline = [
            {"$match": {"artist_id": user["id"]}},
            {"$group": {"_id": "$country", "count": {"$sum": 1}}},
            {"$sort": {"count": -1}}, {"$limit": 8}
        ]
        country_results = await db.stream_events.aggregate(country_pipeline).to_list(8)
        total_country = sum(c["count"] for c in country_results) if country_results else 1
        countries_data = []
        country_names = {"US": "United States", "UK": "United Kingdom", "NG": "Nigeria", "DE": "Germany", "CA": "Canada", "AU": "Australia", "BR": "Brazil", "JP": "Japan", "FR": "France", "IN": "India", "JM": "Jamaica", "KE": "Kenya", "GH": "Ghana", "ZA": "South Africa"}
        for c in country_results:
            name = country_names.get(c["_id"], c["_id"])
            pct = round(c["count"] / total_country * 100, 1)
            countries_data.append(f"{name} ({c['_id']}): {pct}%")
        
        # 3. Peak listening hours
        hour_pipeline = [
            {"$match": {"artist_id": user["id"]}},
            {"$addFields": {"hour_str": {"$substr": ["$timestamp", 11, 2]}}},
            {"$group": {"_id": "$hour_str", "count": {"$sum": 1}}},
            {"$sort": {"count": -1}}, {"$limit": 5}
        ]
        peak_hours_results = await db.stream_events.aggregate(hour_pipeline).to_list(5)
        peak_hours_data = []
        for h in peak_hours_results:
            hr = int(h["_id"]) if h["_id"].isdigit() else 0
            peak_hours_data.append(f"{hr}:00 UTC ({h['count']} streams)")

        # 4. Releases info
        releases = await db.releases.find({"artist_id": user["id"]}, {"_id": 0, "title": 1, "genre": 1, "release_type": 1, "status": 1}).to_list(50)
        release_count = len(releases)
        genres = list(set(r.get("genre", "") for r in releases if r.get("genre")))

        # 5. Pre-save campaigns
        campaigns = await db.presave_campaigns.find({"artist_id": user["id"]}, {"_id": 0, "subscriber_count": 1}).to_list(20)
        total_presave_subs = sum(c.get("subscriber_count", 0) for c in campaigns)

        db_client.close()

        # Build the AI prompt
        prompt = f"""You are a music industry strategist specializing in digital distribution and audience growth. Analyze this artist's data and provide a comprehensive, personalized release strategy.

ARTIST PROFILE:
- Total Streams: {total_streams:,}
- Releases: {release_count}
- Genres: {', '.join(genres) if genres else data.genre or 'Not specified'}
- Plan: {user.get('plan', 'free')}
- Pre-Save Subscribers: {total_presave_subs}
{f'- Upcoming Release: {data.release_title}' if data.release_title else ''}
{f'- Target Genre: {data.genre}' if data.genre else ''}

TOP PLATFORMS (by streams):
{chr(10).join(platforms_data) if platforms_data else 'No streaming data yet'}

TOP LISTENER COUNTRIES:
{chr(10).join(countries_data) if countries_data else 'No geographic data yet'}

PEAK LISTENING HOURS (UTC):
{chr(10).join(peak_hours_data) if peak_hours_data else 'No hourly data yet'}

Based on this data, provide your strategy as a valid JSON object with this exact structure:
{{
  "optimal_release_day": "e.g. Friday",
  "optimal_release_time": "e.g. 00:00 UTC (midnight)",
  "release_day_reasoning": "Why this day/time based on the data",
  "target_platforms": [
    {{"platform": "Spotify", "priority": "high", "tactic": "Submit to editorial playlists 2-3 weeks before release"}}
  ],
  "geographic_strategy": [
    {{"region": "United States", "tactic": "Focus paid promotion during US peak hours (evening EST)"}}
  ],
  "pre_release_timeline": [
    {{"days_before": 28, "action": "Submit to Spotify editorial playlists"}},
    {{"days_before": 14, "action": "Launch pre-save campaign"}}
  ],
  "promotion_tips": ["Tip 1", "Tip 2", "Tip 3"],
  "estimated_first_week_range": "e.g. 500-2,000 streams",
  "confidence_note": "Brief note on data quality and confidence level"
}}

Return ONLY the JSON. No markdown, no explanation outside the JSON."""

        try:
            from emergentintegrations.llm.chat import LlmChat, UserMessage
            chat = LlmChat(
                api_key=EMERGENT_KEY,
                session_id=f"strategy_{user['id']}_{uuid.uuid4().hex[:8]}",
                system_message="You are an expert music industry strategist. Always respond with valid JSON only. No markdown formatting."
            ).with_model("openai", "gpt-4o")
            
            msg = UserMessage(text=prompt)
            response = await chat.send_message(msg)
            
            # Parse the JSON response
            clean = response.strip()
            if clean.startswith("```"):
                clean = clean.split("\n", 1)[1].rsplit("```", 1)[0].strip()
            
            strategy = json.loads(clean)
            return {
                "strategy": strategy,
                "generated_at": datetime.now(timezone.utc).isoformat(),
                "data_summary": {
                    "total_streams": total_streams,
                    "top_platform": platform_results[0]["_id"] if platform_results else None,
                    "top_country": country_results[0]["_id"] if country_results else None,
                    "peak_hour": int(peak_hours_results[0]["_id"]) if peak_hours_results and peak_hours_results[0]["_id"].isdigit() else None,
                    "release_count": release_count,
                    "presave_subscribers": total_presave_subs,
                }
            }
        except json.JSONDecodeError:
            # Return raw text if JSON parsing fails
            return {
                "strategy": {
                    "optimal_release_day": "Friday",
                    "optimal_release_time": "00:00 UTC",
                    "release_day_reasoning": response if response else "Friday releases align with New Music Friday playlists on major platforms.",
                    "target_platforms": [],
                    "geographic_strategy": [],
                    "pre_release_timeline": [],
                    "promotion_tips": [response] if response else ["Engage fans consistently on social media before release"],
                    "estimated_first_week_range": "Varies",
                    "confidence_note": "AI response was not structured. Raw insights included above."
                },
                "generated_at": datetime.now(timezone.utc).isoformat(),
                "data_summary": {
                    "total_streams": total_streams,
                    "top_platform": platform_results[0]["_id"] if platform_results else None,
                    "top_country": country_results[0]["_id"] if country_results else None,
                    "peak_hour": int(peak_hours_results[0]["_id"]) if peak_hours_results and peak_hours_results[0]["_id"].isdigit() else None,
                    "release_count": release_count,
                    "presave_subscribers": total_presave_subs,
                }
            }
        except Exception as e:
            logger.error(f"AI release strategy LLM error: {e}")
            raise
    except HTTPException:
        db_client.close()
        raise
    except Exception as e:
        db_client.close()
        logger.error(f"AI release strategy error: {e}")
        # Fallback strategy
        return {
            "strategy": {
                "optimal_release_day": "Friday",
                "optimal_release_time": "00:00 UTC (midnight)",
                "release_day_reasoning": "Friday is the industry standard for new releases, aligning with 'New Music Friday' playlists across all major platforms.",
                "target_platforms": [
                    {"platform": "Spotify", "priority": "high", "tactic": "Submit to editorial playlists via Spotify for Artists 2-3 weeks before release date."},
                    {"platform": "Apple Music", "priority": "high", "tactic": "Ensure pre-add is enabled and submit for Apple Music editorial consideration."},
                    {"platform": "TikTok", "priority": "medium", "tactic": "Create short-form teaser content using catchy hooks from the release."},
                ],
                "geographic_strategy": [
                    {"region": "Primary Markets", "tactic": "Focus initial promotion on your top streaming countries during their prime evening hours."}
                ],
                "pre_release_timeline": [
                    {"days_before": 28, "action": "Submit to Spotify editorial playlists"},
                    {"days_before": 21, "action": "Announce release on social media with teaser content"},
                    {"days_before": 14, "action": "Launch pre-save campaign"},
                    {"days_before": 7, "action": "Release snippet/preview on TikTok and Instagram Reels"},
                    {"days_before": 3, "action": "Send email blast to mailing list subscribers"},
                    {"days_before": 0, "action": "Release day — coordinate social posts across all platforms"},
                ],
                "promotion_tips": [
                    "Engage with fans in comments and DMs during release week.",
                    "Create platform-specific content (Spotify Canvas, Apple Music Animated Art).",
                    "Collaborate with playlist curators and music blogs in your genre.",
                ],
                "estimated_first_week_range": "Varies based on existing audience",
                "confidence_note": "This is a general strategy. Connect streaming analytics for personalized recommendations."
            },
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "data_summary": {
                "total_streams": 0,
                "top_platform": None,
                "top_country": None,
                "peak_hour": None,
                "release_count": 0,
                "presave_subscribers": 0,
            },
            "fallback": True
        }


@ai_router.post("/strategies/save")
async def save_strategy(data: SaveStrategyRequest, request: Request):
    """Save an AI-generated release strategy for later comparison"""
    user = await _get_user_from_request(request)
    from motor.motor_asyncio import AsyncIOMotorClient
    db_client = AsyncIOMotorClient(os.environ['MONGO_URL'])
    db = db_client[os.environ['DB_NAME']]
    try:
        strategy_id = f"strat_{uuid.uuid4().hex[:12]}"
        now = datetime.now(timezone.utc).isoformat()
        doc = {
            "id": strategy_id,
            "user_id": user["id"],
            "strategy": data.strategy,
            "data_summary": data.data_summary,
            "release_title": data.release_title or "",
            "genre": data.genre or "",
            "label": data.label or f"Strategy - {now[:10]}",
            "created_at": now,
        }
        await db.saved_strategies.insert_one(doc)
        doc.pop("_id", None)
        return {"message": "Strategy saved", "saved_strategy": doc}
    finally:
        db_client.close()

@ai_router.get("/strategies")
async def get_saved_strategies(request: Request):
    """Get all saved strategies for the current user"""
    user = await _get_user_from_request(request)
    from motor.motor_asyncio import AsyncIOMotorClient
    db_client = AsyncIOMotorClient(os.environ['MONGO_URL'])
    db = db_client[os.environ['DB_NAME']]
    try:
        strategies = await db.saved_strategies.find(
            {"user_id": user["id"]}, {"_id": 0}
        ).sort("created_at", -1).to_list(50)
        return {"strategies": strategies, "total": len(strategies)}
    finally:
        db_client.close()

@ai_router.delete("/strategies/{strategy_id}")
async def delete_saved_strategy(strategy_id: str, request: Request):
    """Delete a saved strategy"""
    user = await _get_user_from_request(request)
    from motor.motor_asyncio import AsyncIOMotorClient
    db_client = AsyncIOMotorClient(os.environ['MONGO_URL'])
    db = db_client[os.environ['DB_NAME']]
    try:
        result = await db.saved_strategies.delete_one({"id": strategy_id, "user_id": user["id"]})
        if result.deleted_count == 0:
            raise HTTPException(status_code=404, detail="Strategy not found")
        return {"message": "Strategy deleted"}
    finally:
        db_client.close()


class ExportStrategyRequest(BaseModel):
    strategy: dict
    data_summary: dict
    release_title: Optional[str] = None
    genre: Optional[str] = None
    label: Optional[str] = None

@ai_router.post("/strategies/export-pdf")
async def export_strategy_pdf(data: ExportStrategyRequest, request: Request):
    """Generate a branded Kalmori PDF one-pager for a release strategy"""
    user = await _get_user_from_request(request)
    from fastapi.responses import Response
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.colors import HexColor, white, black
    from reportlab.lib.units import mm
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.enums import TA_LEFT, TA_CENTER
    from io import BytesIO

    buf = BytesIO()
    doc = SimpleDocTemplate(buf, pagesize=A4, topMargin=20*mm, bottomMargin=15*mm, leftMargin=18*mm, rightMargin=18*mm)

    # Colors
    purple = HexColor("#7C4DFF")
    gray_text = HexColor("#999999")
    light_text = HexColor("#333333")

    # Styles
    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle('KTitle', parent=styles['Title'], fontSize=22, textColor=purple, spaceAfter=2*mm, fontName='Helvetica-Bold'))
    styles.add(ParagraphStyle('KSubtitle', parent=styles['Normal'], fontSize=10, textColor=gray_text, spaceAfter=6*mm))
    styles.add(ParagraphStyle('KHeading', parent=styles['Heading2'], fontSize=13, textColor=purple, spaceBefore=5*mm, spaceAfter=3*mm, fontName='Helvetica-Bold'))
    styles.add(ParagraphStyle('KBody', parent=styles['Normal'], fontSize=9.5, textColor=light_text, spaceAfter=2*mm, leading=13))
    styles.add(ParagraphStyle('KSmall', parent=styles['Normal'], fontSize=8, textColor=gray_text, spaceAfter=1*mm))
    styles.add(ParagraphStyle('KBold', parent=styles['Normal'], fontSize=10, textColor=black, fontName='Helvetica-Bold', spaceAfter=2*mm))
    styles.add(ParagraphStyle('KCenter', parent=styles['Normal'], fontSize=8, textColor=gray_text, alignment=TA_CENTER))

    s = data.strategy
    summary = data.data_summary or {}
    elements = []

    # Header
    elements.append(Paragraph("KALMORI", styles['KTitle']))
    title_label = data.label or data.release_title or "AI Release Strategy"
    elements.append(Paragraph(f"{title_label} &mdash; Generated {datetime.now(timezone.utc).strftime('%B %d, %Y')}", styles['KSubtitle']))

    # Artist info line
    artist_name = user.get("artist_name") or user.get("name", "Artist")
    info_parts = [f"Artist: {artist_name}"]
    if data.genre:
        info_parts.append(f"Genre: {data.genre}")
    if summary.get("total_streams"):
        info_parts.append(f"Streams Analyzed: {summary['total_streams']:,}")
    elements.append(Paragraph(" | ".join(info_parts), styles['KSmall']))
    elements.append(Spacer(1, 3*mm))

    # Optimal Release Window
    elements.append(Paragraph("Optimal Release Window", styles['KHeading']))
    window_data = [
        ["Best Day", s.get("optimal_release_day", "Friday")],
        ["Best Time", s.get("optimal_release_time", "00:00 UTC")],
    ]
    if summary.get("top_platform"):
        window_data.append(["Top Platform", summary["top_platform"]])
    if summary.get("top_country"):
        window_data.append(["Top Market", summary["top_country"]])
    if s.get("estimated_first_week_range"):
        window_data.append(["Est. First Week", s["estimated_first_week_range"]])

    t = Table(window_data, colWidths=[45*mm, 120*mm])
    t.setStyle(TableStyle([
        ('TEXTCOLOR', (0, 0), (0, -1), gray_text),
        ('TEXTCOLOR', (1, 0), (1, -1), black),
        ('FONTNAME', (1, 0), (1, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 9.5),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
        ('LINEBELOW', (0, 0), (-1, -2), 0.5, HexColor("#EEEEEE")),
    ]))
    elements.append(t)

    if s.get("release_day_reasoning"):
        elements.append(Spacer(1, 2*mm))
        elements.append(Paragraph(s["release_day_reasoning"], styles['KBody']))

    # Platform Strategy
    if s.get("target_platforms"):
        elements.append(Paragraph("Platform Strategy", styles['KHeading']))
        for p in s["target_platforms"]:
            priority = p.get("priority", "medium").upper()
            elements.append(Paragraph(
                f"<b>[{priority}] {p.get('platform', '')}</b> &mdash; {p.get('tactic', '')}",
                styles['KBody']
            ))

    # Geographic Targeting
    if s.get("geographic_strategy"):
        elements.append(Paragraph("Geographic Targeting", styles['KHeading']))
        for g in s["geographic_strategy"]:
            elements.append(Paragraph(
                f"<b>{g.get('region', '')}</b>: {g.get('tactic', '')}",
                styles['KBody']
            ))

    # Pre-Release Timeline
    if s.get("pre_release_timeline"):
        elements.append(Paragraph("Pre-Release Timeline", styles['KHeading']))
        timeline = sorted(s["pre_release_timeline"], key=lambda x: x.get("days_before", 0), reverse=True)
        tl_data = []
        for t_item in timeline:
            days = t_item.get("days_before", 0)
            label_text = "Release Day" if days == 0 else f"-{days} days"
            tl_data.append([label_text, t_item.get("action", "")])
        tl_table = Table(tl_data, colWidths=[22*mm, 143*mm])
        tl_table.setStyle(TableStyle([
            ('TEXTCOLOR', (0, 0), (0, -1), purple),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
            ('TOPPADDING', (0, 0), (-1, -1), 3),
            ('LINEBELOW', (0, 0), (-1, -2), 0.5, HexColor("#EEEEEE")),
        ]))
        elements.append(tl_table)

    # Promotion Tips
    if s.get("promotion_tips"):
        elements.append(Paragraph("Promotion Tips", styles['KHeading']))
        for i, tip in enumerate(s["promotion_tips"], 1):
            elements.append(Paragraph(f"{i}. {tip}", styles['KBody']))

    # Confidence Note
    if s.get("confidence_note"):
        elements.append(Spacer(1, 3*mm))
        elements.append(Paragraph(f"Note: {s['confidence_note']}", styles['KSmall']))

    # Footer
    elements.append(Spacer(1, 6*mm))
    elements.append(Paragraph("Generated by Kalmori AI | kalmori.com", styles['KCenter']))

    doc.build(elements)
    pdf_bytes = buf.getvalue()
    buf.close()

    safe_label = "".join(c for c in (data.label or data.release_title or "strategy") if c.isalnum() or c in " _-").strip().replace(" ", "_")
    filename = f"Kalmori_Strategy_{safe_label}_{datetime.now(timezone.utc).strftime('%Y%m%d')}.pdf"

    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'}
    )


COUNTRY_NAMES = {"US": "United States", "UK": "United Kingdom", "NG": "Nigeria", "DE": "Germany", "CA": "Canada", "AU": "Australia", "BR": "Brazil", "JP": "Japan", "FR": "France", "IN": "India", "JM": "Jamaica", "KE": "Kenya", "GH": "Ghana", "ZA": "South Africa"}

@ai_router.post("/smart-insights")
async def generate_smart_insights(request: Request):
    """Analyze fan analytics trends and generate AI-powered actionable notifications"""
    user = await _get_user_from_request(request)
    from motor.motor_asyncio import AsyncIOMotorClient
    db_client = AsyncIOMotorClient(os.environ['MONGO_URL'])
    db = db_client[os.environ['DB_NAME']]

    try:
        now = datetime.now(timezone.utc)
        week_ago = (now - timedelta(days=7)).isoformat()
        two_weeks_ago = (now - timedelta(days=14)).isoformat()

        # Recent week streams
        recent = await db.stream_events.find(
            {"artist_id": user["id"], "timestamp": {"$gte": week_ago}}, {"_id": 0}
        ).to_list(5000)

        # Previous week streams
        prev = await db.stream_events.find(
            {"artist_id": user["id"], "timestamp": {"$gte": two_weeks_ago, "$lt": week_ago}}, {"_id": 0}
        ).to_list(5000)

        recent_total = len(recent)
        prev_total = len(prev) or 1

        # Country breakdown
        def count_by(items, key):
            counts = {}
            for item in items:
                v = item.get(key, "Unknown")
                counts[v] = counts.get(v, 0) + 1
            return counts

        recent_countries = count_by(recent, "country")
        prev_countries = count_by(prev, "country")
        recent_platforms = count_by(recent, "platform")
        prev_platforms = count_by(prev, "platform")

        # Peak hours
        def count_hours(items):
            hours = {}
            for item in items:
                ts = item.get("timestamp", "")
                if len(ts) >= 13:
                    h = ts[11:13]
                    if h.isdigit():
                        hours[int(h)] = hours.get(int(h), 0) + 1
            return hours

        recent_hours = count_hours(recent)
        prev_hours = count_hours(prev)

        # Compute growth metrics
        overall_growth = round((recent_total - prev_total) / max(prev_total, 1) * 100, 1)

        country_trends = []
        for c, cnt in sorted(recent_countries.items(), key=lambda x: -x[1])[:8]:
            prev_cnt = prev_countries.get(c, 0) or 1
            growth = round((cnt - prev_cnt) / prev_cnt * 100, 1)
            name = COUNTRY_NAMES.get(c, c)
            country_trends.append(f"{name} ({c}): {cnt} streams this week ({growth:+.1f}% vs last week)")

        platform_trends = []
        for p, cnt in sorted(recent_platforms.items(), key=lambda x: -x[1])[:6]:
            prev_cnt = prev_platforms.get(p, 0) or 1
            growth = round((cnt - prev_cnt) / prev_cnt * 100, 1)
            platform_trends.append(f"{p}: {cnt} streams ({growth:+.1f}%)")

        peak_shift = ""
        if recent_hours and prev_hours:
            recent_peak = max(recent_hours, key=recent_hours.get)
            prev_peak = max(prev_hours, key=prev_hours.get)
            if recent_peak != prev_peak:
                peak_shift = f"Peak listening hour shifted from {prev_peak}:00 UTC to {recent_peak}:00 UTC"

        # Pre-save campaigns
        campaigns = await db.presave_campaigns.find({"artist_id": user["id"]}, {"_id": 0, "subscriber_count": 1, "title": 1}).to_list(10)
        campaign_info = ", ".join(f"{c.get('title','Untitled')}: {c.get('subscriber_count',0)} subs" for c in campaigns[:3]) if campaigns else "No active campaigns"

        # Build AI prompt
        prompt = f"""You are a music growth coach analyzing an artist's streaming trends. Based on the data below, generate 3-5 actionable smart insights/notifications. Each should be specific, data-driven, and immediately actionable.

STREAMING OVERVIEW:
- This week: {recent_total} streams | Last week: {prev_total} streams | Growth: {overall_growth:+.1f}%

COUNTRY TRENDS (this week vs last):
{chr(10).join(country_trends) if country_trends else "No geographic data yet"}

PLATFORM TRENDS:
{chr(10).join(platform_trends) if platform_trends else "No platform data yet"}

{f"PEAK HOUR SHIFT: {peak_shift}" if peak_shift else ""}

PRE-SAVE CAMPAIGNS: {campaign_info}

Generate your response as a valid JSON array of objects with this structure:
[
  {{
    "title": "Short headline (max 60 chars)",
    "message": "Detailed actionable insight (max 200 chars)",
    "category": "growth|geographic|platform|timing|campaign",
    "priority": "high|medium|low",
    "metric_value": "e.g. +40%",
    "action_suggestion": "One specific action they should take"
  }}
]

Be specific with numbers from the data. Don't be generic. Return ONLY the JSON array."""

        insights_raw = []
        try:
            from emergentintegrations.llm.chat import LlmChat, UserMessage
            chat = LlmChat(
                api_key=EMERGENT_KEY,
                session_id=f"insights_{user['id']}_{uuid.uuid4().hex[:8]}",
                system_message="You are a music growth analyst. Always respond with valid JSON only."
            ).with_model("openai", "gpt-4o")

            response = await chat.send_message(UserMessage(text=prompt))
            clean = response.strip()
            if clean.startswith("```"):
                clean = clean.split("\n", 1)[1].rsplit("```", 1)[0].strip()
            insights_raw = json.loads(clean)
        except Exception as e:
            logger.error(f"Smart insights AI error: {e}")
            insights_raw = [
                {"title": f"Streams {'Up' if overall_growth > 0 else 'Down'} {abs(overall_growth)}%", "message": f"Your streams went from {prev_total} to {recent_total} this week. {'Keep the momentum going!' if overall_growth > 0 else 'Consider boosting promotion.'}", "category": "growth", "priority": "high", "metric_value": f"{overall_growth:+.1f}%", "action_suggestion": "Review your promotion strategy for this week."}
            ]

        # Store as notifications
        created_insights = []
        for insight in insights_raw[:5]:
            notif_id = f"notif_{uuid.uuid4().hex[:12]}"
            notif = {
                "id": notif_id,
                "user_id": user["id"],
                "message": f"{insight.get('title', 'Insight')}: {insight.get('message', '')}",
                "type": "ai_insight",
                "category": insight.get("category", "growth"),
                "priority": insight.get("priority", "medium"),
                "metric_value": insight.get("metric_value", ""),
                "action_suggestion": insight.get("action_suggestion", ""),
                "read": False,
                "created_at": now.isoformat(),
            }
            await db.notifications.insert_one(notif)
            notif.pop("_id", None)
            created_insights.append(notif)

        db_client.close()
        return {
            "insights": created_insights,
            "data_context": {
                "recent_streams": recent_total,
                "previous_streams": prev_total,
                "overall_growth": overall_growth,
                "top_country": max(recent_countries, key=recent_countries.get) if recent_countries else None,
                "top_platform": max(recent_platforms, key=recent_platforms.get) if recent_platforms else None,
            },
            "generated_at": now.isoformat(),
        }
    except HTTPException:
        db_client.close()
        raise
    except Exception as e:
        db_client.close()
        logger.error(f"Smart insights error: {e}")
        raise HTTPException(status_code=500, detail="Failed to generate insights")

@ai_router.get("/smart-insights")
async def get_smart_insights(request: Request):
    """Get recent AI-generated smart insights for the current user"""
    user = await _get_user_from_request(request)
    from motor.motor_asyncio import AsyncIOMotorClient
    db_client = AsyncIOMotorClient(os.environ['MONGO_URL'])
    db = db_client[os.environ['DB_NAME']]
    try:
        insights = await db.notifications.find(
            {"user_id": user["id"], "type": "ai_insight"}, {"_id": 0}
        ).sort("created_at", -1).to_list(20)
        return {"insights": insights, "total": len(insights)}
    finally:
        db_client.close()
