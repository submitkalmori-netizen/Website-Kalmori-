"""Email notifications & Password Reset using Resend"""
from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel, EmailStr
from motor.motor_asyncio import AsyncIOMotorClient
from datetime import datetime, timezone, timedelta
import os
import uuid
import secrets
import bcrypt
import logging

logger = logging.getLogger(__name__)

email_router = APIRouter(prefix="/api")

RESEND_API_KEY = os.environ.get("RESEND_API_KEY")
SENDER_EMAIL = os.environ.get("SENDER_EMAIL", "onboarding@resend.dev")
FRONTEND_URL = os.environ.get("FRONTEND_URL", "")

_client = AsyncIOMotorClient(os.environ['MONGO_URL'])
db = _client[os.environ['DB_NAME']]

try:
    import resend
    if RESEND_API_KEY:
        resend.api_key = RESEND_API_KEY
except ImportError:
    resend = None

async def send_email(to: str, subject: str, html: str):
    if not resend or not RESEND_API_KEY:
        logger.warning(f"Email skipped (no Resend config): {subject} -> {to}")
        return False
    try:
        import asyncio
        params = {"from": f"Kalmori <{SENDER_EMAIL}>", "to": [to], "subject": subject, "html": html}
        await asyncio.to_thread(resend.Emails.send, params)
        logger.info(f"Email sent: {subject} -> {to}")
        return True
    except Exception as e:
        logger.error(f"Email failed: {e}")
        return False


async def send_beat_purchase_receipt(user_email: str, user_name: str, beat_title: str, license_type: str, amount: float, receipt_id: str):
    license_labels = {"basic_lease": "Basic Lease", "premium_lease": "Premium Lease", "unlimited_lease": "Unlimited Lease", "exclusive": "Exclusive Rights"}
    license_label = license_labels.get(license_type, license_type)
    html = f"""<div style="font-family:Arial;max-width:600px;margin:0 auto;background:#000;color:#fff;border-radius:16px;overflow:hidden;">
    <div style="background:linear-gradient(90deg,#7C4DFF,#E040FB);padding:30px;text-align:center;">
    <h1 style="color:white;margin:0;font-size:24px;">Beat Purchase Receipt</h1></div>
    <div style="padding:30px;">
    <p>Hi {user_name},</p>
    <p>Your beat purchase was successful! Here are the details:</p>
    <div style="background:#1a1a1a;border-radius:12px;padding:20px;margin:20px 0;">
    <table style="width:100%;border-collapse:collapse;">
    <tr><td style="padding:8px 0;color:#888;">Beat:</td><td style="padding:8px 0;text-align:right;font-weight:bold;">{beat_title}</td></tr>
    <tr><td style="padding:8px 0;color:#888;">License:</td><td style="padding:8px 0;text-align:right;font-weight:bold;">{license_label}</td></tr>
    <tr><td style="padding:8px 0;color:#888;">Amount:</td><td style="padding:8px 0;text-align:right;font-weight:bold;color:#4CAF50;">${amount:.2f} USD</td></tr>
    <tr><td style="padding:8px 0;color:#888;">Receipt ID:</td><td style="padding:8px 0;text-align:right;font-size:12px;">{receipt_id}</td></tr>
    </table></div>
    <p>You can download your beat files from your <strong>My Purchases</strong> page in the dashboard.</p>
    <div style="text-align:center;margin:30px 0;">
    <a href="{FRONTEND_URL}/purchases" style="background:#7C4DFF;color:white;padding:14px 32px;border-radius:8px;text-decoration:none;font-weight:bold;display:inline-block;">View My Purchases</a></div>
    <p style="color:#888;font-size:13px;">Thank you for choosing Kalmori!</p>
    </div></div>"""
    await send_email(user_email, f"Beat Purchase Receipt: {beat_title}", html)


async def send_subscription_receipt(user_email: str, user_name: str, plan_name: str, amount: float, receipt_id: str):
    html = f"""<div style="font-family:Arial;max-width:600px;margin:0 auto;background:#000;color:#fff;border-radius:16px;overflow:hidden;">
    <div style="background:linear-gradient(90deg,#FFD700,#FFA000);padding:30px;text-align:center;">
    <h1 style="color:#000;margin:0;font-size:24px;">Subscription Activated!</h1></div>
    <div style="padding:30px;">
    <p>Hi {user_name},</p>
    <p>Your subscription has been activated! Here are the details:</p>
    <div style="background:#1a1a1a;border-radius:12px;padding:20px;margin:20px 0;">
    <table style="width:100%;border-collapse:collapse;">
    <tr><td style="padding:8px 0;color:#888;">Plan:</td><td style="padding:8px 0;text-align:right;font-weight:bold;">{plan_name}</td></tr>
    <tr><td style="padding:8px 0;color:#888;">Amount:</td><td style="padding:8px 0;text-align:right;font-weight:bold;color:#4CAF50;">${amount:.2f}/month</td></tr>
    <tr><td style="padding:8px 0;color:#888;">Receipt ID:</td><td style="padding:8px 0;text-align:right;font-size:12px;">{receipt_id}</td></tr>
    </table></div>
    <p>Enjoy all the premium features of your new plan!</p>
    <div style="text-align:center;margin:30px 0;">
    <a href="{FRONTEND_URL}/dashboard" style="background:#FFD700;color:#000;padding:14px 32px;border-radius:8px;text-decoration:none;font-weight:bold;display:inline-block;">Go to Dashboard</a></div>
    </div></div>"""
    await send_email(user_email, f"Subscription Receipt: {plan_name} Plan", html)

class PasswordResetRequest(BaseModel):
    email: EmailStr

class PasswordResetConfirm(BaseModel):
    token: str
    new_password: str

class PasswordChangeRequest(BaseModel):
    current_password: str
    new_password: str

# Password Reset - Request
@email_router.post("/auth/forgot-password")
async def forgot_password(data: PasswordResetRequest):
    user = await db.users.find_one({"email": data.email})
    if not user:
        return {"message": "If that email exists, a reset link has been sent."}
    
    reset_token = secrets.token_urlsafe(32)
    expires = datetime.now(timezone.utc) + timedelta(hours=1)
    
    await db.password_resets.insert_one({
        "id": str(uuid.uuid4()), "user_id": user["id"], "email": data.email,
        "token": reset_token, "expires_at": expires, "used": False,
        "created_at": datetime.now(timezone.utc)
    })
    
    reset_url = f"{FRONTEND_URL}/reset-password?token={reset_token}"
    html = f"""<div style="font-family:Arial;max-width:600px;margin:0 auto;background:#000;color:#fff;border-radius:16px;overflow:hidden;">
    <div style="background:linear-gradient(90deg,#E040FB,#7C4DFF);padding:30px;text-align:center;">
    <h1 style="color:white;margin:0;font-size:24px;">Password Reset</h1></div>
    <div style="padding:30px;">
    <p>Hi {user.get('name', 'there')},</p>
    <p>We received a request to reset your password. Click the button below:</p>
    <div style="text-align:center;margin:30px 0;">
    <a href="{reset_url}" style="background:#E040FB;color:white;padding:14px 32px;border-radius:8px;text-decoration:none;font-weight:bold;display:inline-block;">Reset Password</a></div>
    <p style="color:#888;font-size:13px;">This link expires in 1 hour. If you didn't request this, ignore this email.</p>
    </div></div>"""
    
    await send_email(data.email, "Kalmori - Password Reset", html)
    return {"message": "If that email exists, a reset link has been sent."}

# Password Reset - Confirm
@email_router.post("/auth/reset-password")
async def reset_password(data: PasswordResetConfirm):
    reset = await db.password_resets.find_one({"token": data.token, "used": False})
    if not reset:
        raise HTTPException(status_code=400, detail="Invalid or expired reset token")
    
    if datetime.now(timezone.utc) > reset["expires_at"]:
        raise HTTPException(status_code=400, detail="Reset token has expired")
    
    if len(data.new_password) < 6:
        raise HTTPException(status_code=400, detail="Password must be at least 6 characters")
    
    password_hash = bcrypt.hashpw(data.new_password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    await db.users.update_one({"id": reset["user_id"]}, {"$set": {"password_hash": password_hash}})
    await db.password_resets.update_one({"token": data.token}, {"$set": {"used": True}})
    
    return {"message": "Password has been reset successfully"}

# Password Reset - Verify token
@email_router.get("/auth/verify-reset-token")
async def verify_reset_token(token: str):
    reset = await db.password_resets.find_one({"token": token, "used": False})
    if not reset:
        raise HTTPException(status_code=400, detail="Invalid or expired reset token")
    if datetime.now(timezone.utc) > reset["expires_at"]:
        raise HTTPException(status_code=400, detail="Reset token has expired")
    return {"valid": True, "email": reset["email"]}

# Change password (authenticated)
@email_router.post("/auth/change-password")
async def change_password(data: PasswordChangeRequest, request: Request):
    from server import get_current_user
    user = await get_current_user(request)
    
    if not bcrypt.checkpw(data.current_password.encode('utf-8'), user["password_hash"].encode('utf-8')):
        raise HTTPException(status_code=400, detail="Current password is incorrect")
    
    if len(data.new_password) < 6:
        raise HTTPException(status_code=400, detail="New password must be at least 6 characters")
    
    new_hash = bcrypt.hashpw(data.new_password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    await db.users.update_one({"id": user["id"]}, {"$set": {"password_hash": new_hash}})
    return {"message": "Password changed successfully"}

# Notification email helpers
async def send_release_approved_email(user_email: str, user_name: str, release_title: str):
    html = f"""<div style="font-family:Arial;max-width:600px;margin:0 auto;background:#000;color:#fff;border-radius:16px;overflow:hidden;">
    <div style="background:linear-gradient(90deg,#4CAF50,#2E7D32);padding:30px;text-align:center;">
    <h1 style="color:white;margin:0;">Release Approved!</h1></div>
    <div style="padding:30px;">
    <p>Hi {user_name},</p>
    <p>Great news! Your release <strong>"{release_title}"</strong> has been approved and is now being distributed to all streaming platforms.</p>
    <p>It may take 24-72 hours for your music to appear on all stores.</p>
    <div style="text-align:center;margin:30px 0;">
    <a href="{FRONTEND_URL}/dashboard" style="background:#4CAF50;color:white;padding:14px 32px;border-radius:8px;text-decoration:none;font-weight:bold;display:inline-block;">View Dashboard</a></div>
    </div></div>"""
    await send_email(user_email, f"Release Approved: {release_title}", html)

async def send_release_rejected_email(user_email: str, user_name: str, release_title: str, reason: str):
    html = f"""<div style="font-family:Arial;max-width:600px;margin:0 auto;background:#000;color:#fff;border-radius:16px;overflow:hidden;">
    <div style="background:linear-gradient(90deg,#F44336,#B71C1C);padding:30px;text-align:center;">
    <h1 style="color:white;margin:0;">Release Needs Changes</h1></div>
    <div style="padding:30px;">
    <p>Hi {user_name},</p>
    <p>Your release <strong>"{release_title}"</strong> needs some changes before it can be distributed:</p>
    <div style="background:#1a1a1a;border-left:4px solid #F44336;padding:15px;margin:20px 0;border-radius:4px;">
    <p style="margin:0;">{reason}</p></div>
    <p>Please update your release and resubmit for review.</p>
    </div></div>"""
    await send_email(user_email, f"Release Update Needed: {release_title}", html)

async def send_payment_received_email(user_email: str, user_name: str, amount: float):
    html = f"""<div style="font-family:Arial;max-width:600px;margin:0 auto;background:#000;color:#fff;border-radius:16px;overflow:hidden;">
    <div style="background:linear-gradient(90deg,#FFD700,#FFA000);padding:30px;text-align:center;">
    <h1 style="color:#000;margin:0;">Payment Received!</h1></div>
    <div style="padding:30px;">
    <p>Hi {user_name},</p>
    <p>We've received your payment of <strong>${amount:.2f}</strong>.</p>
    <p>Thank you for using Kalmori!</p>
    </div></div>"""
    await send_email(user_email, f"Payment Received: ${amount:.2f}", html)


async def _build_digest_data(user):
    """Gather all streaming analytics data for the weekly digest"""
    now = datetime.now(timezone.utc)
    week_ago = (now - timedelta(days=7)).isoformat()
    two_weeks_ago = (now - timedelta(days=14)).isoformat()

    recent = await db.stream_events.find(
        {"artist_id": user["id"], "timestamp": {"$gte": week_ago}}, {"_id": 0}
    ).to_list(5000)
    prev = await db.stream_events.find(
        {"artist_id": user["id"], "timestamp": {"$gte": two_weeks_ago, "$lt": week_ago}}, {"_id": 0}
    ).to_list(5000)

    recent_total = len(recent)
    prev_total = len(prev) or 1
    growth = round((recent_total - prev_total) / prev_total * 100, 1)

    # Country breakdown
    countries = {}
    for e in recent:
        c = e.get("country", "Unknown")
        countries[c] = countries.get(c, 0) + 1
    top_countries = sorted(countries.items(), key=lambda x: -x[1])[:5]

    # Platform breakdown
    platforms = {}
    for e in recent:
        p = e.get("platform", "Unknown")
        platforms[p] = platforms.get(p, 0) + 1
    top_platforms = sorted(platforms.items(), key=lambda x: -x[1])[:5]

    # Recent releases
    releases = await db.releases.find(
        {"artist_id": user["id"]}, {"_id": 0, "title": 1, "status": 1, "created_at": 1}
    ).sort("created_at", -1).to_list(3)

    # Pre-save campaigns
    campaigns = await db.presave_campaigns.find(
        {"artist_id": user["id"]}, {"_id": 0, "title": 1, "subscriber_count": 1}
    ).to_list(5)
    total_presave = sum(c.get("subscriber_count", 0) for c in campaigns)

    # AI insights from this week
    insights = await db.notifications.find(
        {"user_id": user["id"], "type": "ai_insight"},
        {"_id": 0, "message": 1, "action_suggestion": 1, "category": 1, "priority": 1, "metric_value": 1}
    ).sort("created_at", -1).to_list(5)

    country_names = {"US": "United States", "UK": "United Kingdom", "NG": "Nigeria", "DE": "Germany", "CA": "Canada", "AU": "Australia", "BR": "Brazil", "JP": "Japan", "FR": "France", "IN": "India"}

    return {
        "recent_total": recent_total,
        "prev_total": prev_total,
        "growth": growth,
        "top_countries": [(country_names.get(c, c), cnt) for c, cnt in top_countries],
        "top_platforms": top_platforms,
        "releases": releases,
        "total_presave": total_presave,
        "insights": insights,
        "week_ending": now.strftime("%B %d, %Y"),
    }


def _build_digest_html(user, data):
    """Build branded HTML email for weekly digest"""
    artist = user.get("artist_name") or user.get("name", "Artist")
    growth_color = "#4CAF50" if data["growth"] >= 0 else "#F44336"
    growth_arrow = "+" if data["growth"] >= 0 else ""

    # Country rows
    country_rows = ""
    for name, cnt in data["top_countries"]:
        pct = round(cnt / max(data["recent_total"], 1) * 100, 1)
        country_rows += f'<tr><td style="padding:6px 0;color:#ccc;font-size:13px;">{name}</td><td style="padding:6px 0;text-align:right;color:#fff;font-weight:bold;font-size:13px;">{cnt:,}</td><td style="padding:6px 0;text-align:right;color:#888;font-size:12px;">{pct}%</td></tr>'

    # Platform rows
    platform_rows = ""
    for name, cnt in data["top_platforms"]:
        pct = round(cnt / max(data["recent_total"], 1) * 100, 1)
        platform_rows += f'<tr><td style="padding:6px 0;color:#ccc;font-size:13px;">{name}</td><td style="padding:6px 0;text-align:right;color:#fff;font-weight:bold;font-size:13px;">{cnt:,}</td><td style="padding:6px 0;text-align:right;color:#888;font-size:12px;">{pct}%</td></tr>'

    # Insights section
    insights_html = ""
    if data["insights"]:
        insights_items = ""
        for ins in data["insights"][:3]:
            cat = ins.get("category", "growth")
            cat_colors = {"growth": "#1DB954", "geographic": "#E040FB", "platform": "#7C4DFF", "timing": "#FFD700", "campaign": "#FF6B6B"}
            color = cat_colors.get(cat, "#7C4DFF")
            metric = f'<span style="color:#FFD700;font-size:11px;font-weight:bold;"> {ins.get("metric_value", "")}</span>' if ins.get("metric_value") else ""
            action = f'<p style="color:#7C4DFF;font-size:12px;margin:4px 0 0;">&rarr; {ins["action_suggestion"]}</p>' if ins.get("action_suggestion") else ""
            insights_items += f'''<div style="background:#0a0a0a;border-left:3px solid {color};border-radius:6px;padding:12px;margin-bottom:8px;">
            <p style="color:#fff;font-size:13px;margin:0;">{ins.get("message", "")}{metric}</p>{action}</div>'''

        insights_html = f'''<div style="margin-top:24px;">
        <h2 style="color:#E040FB;font-size:16px;margin:0 0 12px;">AI Smart Insights</h2>
        {insights_items}</div>'''

    # Release updates
    releases_html = ""
    if data["releases"]:
        rel_items = ""
        for r in data["releases"]:
            status_colors = {"approved": "#4CAF50", "pending": "#FFD700", "distributed": "#1DB954", "draft": "#888"}
            sc = status_colors.get(r.get("status", ""), "#888")
            rel_items += f'<span style="display:inline-block;background:{sc}20;color:{sc};padding:4px 10px;border-radius:20px;font-size:11px;margin:2px 4px;font-weight:bold;">{r.get("title","Untitled")} &bull; {r.get("status","draft").title()}</span>'
        releases_html = f'''<div style="margin-top:20px;">
        <h2 style="color:#7C4DFF;font-size:16px;margin:0 0 12px;">Your Releases</h2>
        <div>{rel_items}</div></div>'''

    html = f'''<div style="font-family:'Helvetica Neue',Arial,sans-serif;max-width:600px;margin:0 auto;background:#000;color:#fff;border-radius:16px;overflow:hidden;">
    <div style="background:linear-gradient(135deg,#7C4DFF 0%,#E040FB 50%,#FF6B6B 100%);padding:36px 30px;text-align:center;">
        <h1 style="color:white;margin:0;font-size:28px;letter-spacing:6px;font-weight:800;">KALMORI</h1>
        <p style="color:rgba(255,255,255,0.85);margin:8px 0 0;font-size:14px;">Weekly Performance Digest</p>
        <p style="color:rgba(255,255,255,0.6);margin:4px 0 0;font-size:12px;">Week ending {data["week_ending"]}</p>
    </div>
    <div style="padding:30px;">
        <p style="color:#ccc;font-size:14px;margin:0 0 24px;">Hi {artist},</p>
        <p style="color:#999;font-size:13px;margin:0 0 20px;">Here's your weekly streaming performance and AI-powered recommendations:</p>

        <div style="display:flex;gap:12px;margin-bottom:24px;">
            <div style="flex:1;background:#111;border:1px solid #222;border-radius:12px;padding:16px;text-align:center;">
                <p style="color:#888;font-size:11px;margin:0 0 4px;text-transform:uppercase;letter-spacing:1px;">This Week</p>
                <p style="color:#fff;font-size:24px;font-weight:bold;margin:0;">{data["recent_total"]:,}</p>
                <p style="color:#888;font-size:11px;margin:2px 0 0;">streams</p>
            </div>
            <div style="flex:1;background:#111;border:1px solid #222;border-radius:12px;padding:16px;text-align:center;">
                <p style="color:#888;font-size:11px;margin:0 0 4px;text-transform:uppercase;letter-spacing:1px;">Last Week</p>
                <p style="color:#fff;font-size:24px;font-weight:bold;margin:0;">{data["prev_total"]:,}</p>
                <p style="color:#888;font-size:11px;margin:2px 0 0;">streams</p>
            </div>
            <div style="flex:1;background:#111;border:1px solid #222;border-radius:12px;padding:16px;text-align:center;">
                <p style="color:#888;font-size:11px;margin:0 0 4px;text-transform:uppercase;letter-spacing:1px;">Growth</p>
                <p style="color:{growth_color};font-size:24px;font-weight:bold;margin:0;">{growth_arrow}{data["growth"]}%</p>
                <p style="color:#888;font-size:11px;margin:2px 0 0;">vs last week</p>
            </div>
        </div>

        <div style="display:flex;gap:12px;">
            <div style="flex:1;">
                <h2 style="color:#E040FB;font-size:14px;margin:0 0 8px;">Top Markets</h2>
                <table style="width:100%;border-collapse:collapse;">{country_rows}</table>
            </div>
            <div style="flex:1;">
                <h2 style="color:#1DB954;font-size:14px;margin:0 0 8px;">Top Platforms</h2>
                <table style="width:100%;border-collapse:collapse;">{platform_rows}</table>
            </div>
        </div>

        {insights_html}
        {releases_html}

        {f'<p style="color:#888;font-size:12px;margin-top:16px;">Pre-Save Subscribers: <strong style="color:#FFD700;">{data["total_presave"]}</strong></p>' if data["total_presave"] > 0 else ''}

        <div style="text-align:center;margin:28px 0 16px;">
            <a href="{FRONTEND_URL}/fan-analytics" style="background:linear-gradient(90deg,#7C4DFF,#E040FB);color:white;padding:14px 36px;border-radius:10px;text-decoration:none;font-weight:bold;font-size:14px;display:inline-block;">View Full Analytics</a>
        </div>

        <p style="color:#555;font-size:11px;text-align:center;margin:20px 0 0;">You're receiving this because you enabled Weekly Digest in your notification settings.<br/>
        <a href="{FRONTEND_URL}/settings" style="color:#7C4DFF;text-decoration:none;">Manage preferences</a></p>
    </div>
</div>'''
    return html


@email_router.post("/digest/send")
async def send_weekly_digest(request: Request):
    """Send a weekly digest email to the current user (manual trigger or test)"""
    from server import get_current_user
    user = await get_current_user(request)

    data = await _build_digest_data(user)
    html = _build_digest_html(user, data)
    subject = f"Kalmori Weekly Digest - {data['week_ending']} | {data['recent_total']:,} streams"

    sent = await send_email(user["email"], subject, html)

    # Log digest send
    await db.digest_log.insert_one({
        "id": f"digest_{uuid.uuid4().hex[:12]}",
        "user_id": user["id"],
        "sent_at": datetime.now(timezone.utc).isoformat(),
        "streams_this_week": data["recent_total"],
        "growth": data["growth"],
        "email_sent": sent,
    })

    return {
        "message": "Weekly digest sent!" if sent else "Digest generated but email delivery pending (check Resend config)",
        "email_sent": sent,
        "stats": {
            "streams_this_week": data["recent_total"],
            "streams_last_week": data["prev_total"],
            "growth": data["growth"],
            "top_countries": len(data["top_countries"]),
            "insights_included": len(data["insights"]),
        }
    }


@email_router.post("/digest/preview")
async def preview_weekly_digest(request: Request):
    """Preview the weekly digest HTML without sending"""
    from server import get_current_user
    user = await get_current_user(request)
    data = await _build_digest_data(user)
    html = _build_digest_html(user, data)
    return {
        "html": html,
        "stats": {
            "streams_this_week": data["recent_total"],
            "streams_last_week": data["prev_total"],
            "growth": data["growth"],
            "top_countries": len(data["top_countries"]),
            "insights_included": len(data["insights"]),
        }
    }


@email_router.get("/digest/history")
async def get_digest_history(request: Request):
    """Get the history of sent weekly digests"""
    from server import get_current_user
    user = await get_current_user(request)
    history = await db.digest_log.find(
        {"user_id": user["id"]}, {"_id": 0}
    ).sort("sent_at", -1).to_list(20)
    return {"history": history, "total": len(history)}
