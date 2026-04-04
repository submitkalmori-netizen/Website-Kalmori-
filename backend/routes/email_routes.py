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


def email_base(header_gradient: str, header_title: str, body_html: str, footer_text: str = "Thank you for choosing Kalmori!") -> str:
    """Reusable branded email template wrapper"""
    return f"""<div style="font-family:'Helvetica Neue',Arial,sans-serif;max-width:600px;margin:0 auto;background:#000;color:#fff;border-radius:16px;overflow:hidden;">
    <div style="background:{header_gradient};padding:30px;text-align:center;">
    <h1 style="color:white;margin:0 0 4px;font-size:11px;letter-spacing:5px;font-weight:800;text-transform:uppercase;opacity:0.85;">KALMORI</h1>
    <h2 style="color:white;margin:0;font-size:24px;font-weight:700;">{header_title}</h2>
    </div>
    <div style="padding:30px;">
    {body_html}
    <p style="color:#555;font-size:12px;margin-top:28px;padding-top:16px;border-top:1px solid #222;text-align:center;">{footer_text}</p>
    </div></div>"""


async def send_welcome_email(user_email: str, user_name: str, user_role: str = "artist"):
    """Send a branded welcome email when a new user signs up"""
    if user_role == "label_producer":
        role_label = "Label / Producer"
        role_desc = "manage your artists, distribute catalogs, and track royalties"
        step2 = "Add your artists and start distributing their music to <strong style=\"color:#fff;\">150+ streaming platforms</strong>"
        step3 = "Use our <strong style=\"color:#fff;\">AI Release Strategy</strong> to optimize every release"
    else:
        role_label = "Artist"
        role_desc = "get your music heard worldwide"
        step2 = "Set up your <strong style=\"color:#fff;\">Artist Profile</strong> — your public link-in-bio page"
        step3 = "Use our <strong style=\"color:#fff;\">AI Release Strategy</strong> to plan your next drop"
    body = f"""<p style="color:#ccc;font-size:15px;margin:0 0 16px;">Yo {user_name}!</p>
    <p style="color:#999;font-size:14px;line-height:1.7;margin:0 0 20px;">Welcome to the <strong style="color:#E040FB;">Kalmori</strong> family! You just took the first step to {role_desc}. We're hype to have you on board as a <strong style="color:#FFD700;">{role_label}</strong>.</p>
    <div style="background:#111;border:1px solid #222;border-radius:12px;padding:20px;margin:20px 0;">
    <p style="color:#E040FB;font-size:13px;font-weight:bold;margin:0 0 12px;text-transform:uppercase;letter-spacing:2px;">Here's what you can do right now:</p>
    <table style="width:100%;border-collapse:collapse;">
    <tr><td style="padding:8px 0;color:#7C4DFF;font-size:20px;width:30px;vertical-align:top;">1</td><td style="padding:8px 0;color:#ccc;font-size:13px;">Upload your first release and distribute to <strong style="color:#fff;">150+ streaming platforms</strong></td></tr>
    <tr><td style="padding:8px 0;color:#7C4DFF;font-size:20px;width:30px;vertical-align:top;">2</td><td style="padding:8px 0;color:#ccc;font-size:13px;">{step2}</td></tr>
    <tr><td style="padding:8px 0;color:#7C4DFF;font-size:20px;width:30px;vertical-align:top;">3</td><td style="padding:8px 0;color:#ccc;font-size:13px;">{step3}</td></tr>
    <tr><td style="padding:8px 0;color:#7C4DFF;font-size:20px;width:30px;vertical-align:top;">4</td><td style="padding:8px 0;color:#ccc;font-size:13px;">Track your streams, revenue, and fan analytics in real-time</td></tr>
    </table></div>
    <div style="text-align:center;margin:28px 0 16px;">
    <a href="{FRONTEND_URL}/dashboard" style="background:linear-gradient(90deg,#7C4DFF,#E040FB);color:white;padding:14px 36px;border-radius:10px;text-decoration:none;font-weight:bold;font-size:14px;display:inline-block;">Go to Your Dashboard</a>
    </div>
    <p style="color:#888;font-size:13px;text-align:center;">Let's get your music out there. The world is waiting.</p>"""
    html = email_base(
        "linear-gradient(135deg,#7C4DFF 0%,#E040FB 50%,#FF4081 100%)",
        f"Welcome to Kalmori, {role_label}!",
        body,
        "You're receiving this because you just signed up at Kalmori. Let's go!"
    )
    await send_email(user_email, f"Welcome to Kalmori, {role_label}! Let's get your music worldwide", html)


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


# ============= EMAIL VERIFICATION =============

async def send_verification_email(user_email: str, user_name: str, verification_token: str):
    """Send email verification link to new user"""
    verify_url = f"{FRONTEND_URL}/verify-email?token={verification_token}"
    body = f"""<p style="color:#ccc;font-size:15px;margin:0 0 16px;">Hey {user_name}!</p>
    <p style="color:#999;font-size:14px;line-height:1.7;margin:0 0 20px;">Thanks for joining <strong style="color:#E040FB;">Kalmori</strong>. Please verify your email address to unlock all features.</p>
    <div style="text-align:center;margin:28px 0;">
    <a href="{verify_url}" style="background:linear-gradient(90deg,#1DB954,#4CAF50);color:white;padding:16px 40px;border-radius:12px;text-decoration:none;font-weight:bold;font-size:15px;display:inline-block;">Verify My Email</a>
    </div>
    <p style="color:#666;font-size:12px;text-align:center;">Or copy this link: <span style="color:#7C4DFF;">{verify_url}</span></p>
    <p style="color:#555;font-size:12px;margin-top:20px;">This link expires in 24 hours.</p>"""
    html = email_base(
        "linear-gradient(135deg,#1DB954 0%,#4CAF50 100%)",
        "Verify Your Email",
        body,
        "Kalmori Distribution — Verify to get started"
    )
    await send_email(user_email, "Kalmori — Please Verify Your Email Address", html)


async def send_admin_signup_notification(user_name: str, user_email: str, user_role: str):
    """Notify admin when a new user signs up"""
    admin = await db.users.find_one({"role": "admin"}, {"_id": 0, "email": 1, "id": 1})
    if not admin:
        return
    role_label = "Label / Producer" if user_role == "label_producer" else "Artist"
    now = datetime.now(timezone.utc).strftime("%B %d, %Y at %I:%M %p UTC")
    body = f"""<p style="color:#ccc;font-size:15px;margin:0 0 16px;">New Sign-Up Alert</p>
    <div style="background:#111;border:1px solid #222;border-radius:12px;padding:20px;margin:16px 0;">
    <table style="width:100%;border-collapse:collapse;">
    <tr><td style="padding:6px 0;color:#888;font-size:13px;">Name</td><td style="padding:6px 0;color:#fff;font-size:13px;font-weight:bold;">{user_name}</td></tr>
    <tr><td style="padding:6px 0;color:#888;font-size:13px;">Email</td><td style="padding:6px 0;color:#7C4DFF;font-size:13px;">{user_email}</td></tr>
    <tr><td style="padding:6px 0;color:#888;font-size:13px;">Role</td><td style="padding:6px 0;color:#FFD700;font-size:13px;font-weight:bold;">{role_label}</td></tr>
    <tr><td style="padding:6px 0;color:#888;font-size:13px;">Signed Up</td><td style="padding:6px 0;color:#ccc;font-size:13px;">{now}</td></tr>
    </table></div>
    <div style="text-align:center;margin:20px 0;">
    <a href="{FRONTEND_URL}/admin/users" style="background:#E53935;color:white;padding:12px 28px;border-radius:10px;text-decoration:none;font-weight:bold;font-size:13px;display:inline-block;">View All Users</a>
    </div>"""
    html = email_base(
        "linear-gradient(135deg,#E53935 0%,#FF5722 100%)",
        f"New {role_label} Sign-Up!",
        body,
        "Kalmori Admin Notification"
    )
    await send_email(admin["email"], f"Kalmori: New {role_label} sign-up — {user_name}", html)
    # Also create in-app notification for admin
    await db.notifications.insert_one({
        "id": f"notif_{uuid.uuid4().hex[:12]}",
        "user_id": admin["id"],
        "type": "new_signup",
        "message": f"New {role_label} signed up: {user_name} ({user_email})",
        "read": False,
        "created_at": datetime.now(timezone.utc).isoformat(),
    })


@email_router.get("/auth/verify-email")
async def verify_email(token: str):
    """Verify user email via token"""
    record = await db.email_verifications.find_one({"token": token, "used": False})
    if not record:
        raise HTTPException(status_code=400, detail="Invalid or expired verification link")
    if datetime.now(timezone.utc) > record["expires_at"]:
        raise HTTPException(status_code=400, detail="Verification link has expired")
    await db.users.update_one({"id": record["user_id"]}, {"$set": {"email_verified": True}})
    await db.email_verifications.update_one({"token": token}, {"$set": {"used": True}})
    return {"message": "Email verified successfully", "verified": True}


@email_router.post("/auth/resend-verification")
async def resend_verification(request: Request):
    """Resend verification email"""
    from server import get_current_user
    user = await get_current_user(request)
    if user.get("email_verified"):
        return {"message": "Email already verified"}
    token = secrets.token_urlsafe(32)
    expires = datetime.now(timezone.utc) + timedelta(hours=24)
    await db.email_verifications.insert_one({
        "id": str(uuid.uuid4()), "user_id": user["id"], "email": user["email"],
        "token": token, "expires_at": expires, "used": False,
        "created_at": datetime.now(timezone.utc),
    })
    import asyncio
    asyncio.ensure_future(send_verification_email(user["email"], user.get("name", "Artist"), token))
    return {"message": "Verification email sent"}


# ============= MARKETING CAMPAIGNS (Admin) =============

class CampaignInput(BaseModel):
    name: str
    subject: str
    body_html: str
    audience: str = "all"  # "all", "artist", "label_producer"
    header_title: str = ""
    header_gradient: str = "linear-gradient(135deg,#7C4DFF 0%,#E040FB 100%)"

@email_router.post("/admin/campaigns")
async def create_campaign(data: CampaignInput, request: Request):
    from server import get_current_user
    user = await get_current_user(request)
    if user.get("role") != "admin":
        raise HTTPException(status_code=403, detail="Admin only")
    now = datetime.now(timezone.utc).isoformat()
    campaign = {
        "id": f"camp_{uuid.uuid4().hex[:12]}",
        "name": data.name.strip(),
        "subject": data.subject.strip(),
        "body_html": data.body_html,
        "audience": data.audience,
        "header_title": data.header_title or data.subject,
        "header_gradient": data.header_gradient,
        "status": "draft",
        "sent_count": 0,
        "created_at": now,
        "sent_at": None,
    }
    await db.campaigns.insert_one(campaign)
    campaign.pop("_id", None)
    return campaign

@email_router.get("/admin/campaigns")
async def list_campaigns(request: Request):
    from server import get_current_user
    user = await get_current_user(request)
    if user.get("role") != "admin":
        raise HTTPException(status_code=403, detail="Admin only")
    campaigns = await db.campaigns.find({}, {"_id": 0}).sort("created_at", -1).to_list(100)
    return {"campaigns": campaigns}

@email_router.post("/admin/campaigns/{campaign_id}/send")
async def send_campaign(campaign_id: str, request: Request):
    from server import get_current_user
    user = await get_current_user(request)
    if user.get("role") != "admin":
        raise HTTPException(status_code=403, detail="Admin only")
    campaign = await db.campaigns.find_one({"id": campaign_id})
    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")

    query = {}
    if campaign["audience"] == "artist":
        query["user_role"] = "artist"
    elif campaign["audience"] == "label_producer":
        query["user_role"] = "label_producer"

    users = await db.users.find(query, {"_id": 0, "email": 1, "name": 1, "artist_name": 1, "id": 1}).to_list(10000)
    sent = 0
    import asyncio
    for u in users:
        name = u.get("artist_name", u.get("name", "there"))
        personalized_body = campaign["body_html"].replace("{{name}}", name).replace("{{email}}", u.get("email", ""))
        html = email_base(campaign["header_gradient"], campaign["header_title"], personalized_body, "Kalmori Distribution")
        asyncio.ensure_future(send_email(u["email"], campaign["subject"], html))
        # In-app notification
        await db.notifications.insert_one({
            "id": f"notif_{uuid.uuid4().hex[:12]}",
            "user_id": u["id"],
            "type": "campaign",
            "message": campaign["subject"],
            "read": False,
            "created_at": datetime.now(timezone.utc).isoformat(),
        })
        sent += 1

    await db.campaigns.update_one({"id": campaign_id}, {
        "$set": {"status": "sent", "sent_count": sent, "sent_at": datetime.now(timezone.utc).isoformat()}
    })
    return {"message": f"Campaign sent to {sent} users", "sent_count": sent}

@email_router.delete("/admin/campaigns/{campaign_id}")
async def delete_campaign(campaign_id: str, request: Request):
    from server import get_current_user
    user = await get_current_user(request)
    if user.get("role") != "admin":
        raise HTTPException(status_code=403, detail="Admin only")
    result = await db.campaigns.delete_one({"id": campaign_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Campaign not found")
    return {"message": "Campaign deleted"}

@email_router.post("/admin/campaigns/{campaign_id}/preview")
async def preview_campaign(campaign_id: str, request: Request):
    from server import get_current_user
    user = await get_current_user(request)
    if user.get("role") != "admin":
        raise HTTPException(status_code=403, detail="Admin only")
    campaign = await db.campaigns.find_one({"id": campaign_id}, {"_id": 0})
    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")
    html = email_base(campaign["header_gradient"], campaign["header_title"],
                      campaign["body_html"].replace("{{name}}", "Preview User").replace("{{email}}", "preview@example.com"),
                      "Kalmori Distribution")
    return {"html": html, "subject": campaign["subject"]}


# ============= LEAD / DRAFT TRACKING =============

@email_router.get("/admin/leads")
async def get_leads(request: Request):
    """Get all abandoned/draft actions for admin follow-up"""
    from server import get_current_user
    user = await get_current_user(request)
    if user.get("role") != "admin":
        raise HTTPException(status_code=403, detail="Admin only")

    now = datetime.now(timezone.utc)
    stale_threshold = now - timedelta(hours=24)

    # Find draft releases (started but not submitted/live)
    draft_releases = await db.releases.find(
        {"status": {"$in": ["draft", "pending"]}}, {"_id": 0}
    ).to_list(500)

    leads = []
    for r in draft_releases:
        user_info = await db.users.find_one({"id": r.get("artist_id")}, {"_id": 0, "email": 1, "name": 1, "artist_name": 1})
        if not user_info:
            continue
        created = r.get("created_at", "")
        is_stale = False
        if created:
            try:
                created_dt = datetime.fromisoformat(created.replace("Z", "+00:00"))
                is_stale = created_dt < stale_threshold
            except:
                pass
        leads.append({
            "id": r.get("id", ""),
            "type": "draft_release",
            "user_id": r.get("artist_id", ""),
            "user_name": user_info.get("artist_name", user_info.get("name", "")),
            "user_email": user_info.get("email", ""),
            "title": r.get("title", "Untitled"),
            "status": r.get("status", "draft"),
            "created_at": created,
            "stale": is_stale,
            "reminder_sent": r.get("reminder_sent", False),
        })

    # Find incomplete beat uploads
    draft_beats = await db.beats.find(
        {"status": {"$in": ["draft", "inactive"]}}, {"_id": 0}
    ).to_list(500)
    for b in draft_beats:
        user_info = await db.users.find_one({"id": b.get("producer_id")}, {"_id": 0, "email": 1, "name": 1, "artist_name": 1})
        if not user_info:
            continue
        created = b.get("created_at", "")
        is_stale = False
        if created:
            try:
                created_dt = datetime.fromisoformat(created.replace("Z", "+00:00"))
                is_stale = created_dt < stale_threshold
            except:
                pass
        leads.append({
            "id": b.get("id", ""),
            "type": "draft_beat",
            "user_id": b.get("producer_id", ""),
            "user_name": user_info.get("artist_name", user_info.get("name", "")),
            "user_email": user_info.get("email", ""),
            "title": b.get("title", "Untitled Beat"),
            "status": b.get("status", "draft"),
            "created_at": created,
            "stale": is_stale,
            "reminder_sent": b.get("reminder_sent", False),
        })

    leads.sort(key=lambda x: x.get("created_at", ""), reverse=True)
    stale_count = sum(1 for l in leads if l.get("stale"))
    return {"leads": leads, "total": len(leads), "stale_count": stale_count}


@email_router.post("/admin/leads/send-reminder")
async def send_lead_reminder(request: Request):
    """Send reminder to a specific lead/draft user"""
    from server import get_current_user
    user = await get_current_user(request)
    if user.get("role") != "admin":
        raise HTTPException(status_code=403, detail="Admin only")
    body = await request.json()
    lead_id = body.get("lead_id", "")
    lead_type = body.get("lead_type", "")
    if not lead_id or not lead_type:
        raise HTTPException(status_code=400, detail="lead_id and lead_type required")

    collection = db.releases if lead_type == "draft_release" else db.beats
    item = await collection.find_one({"id": lead_id}, {"_id": 0})
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")

    target_user_id = item.get("artist_id") or item.get("producer_id")
    target_user = await db.users.find_one({"id": target_user_id}, {"_id": 0, "email": 1, "name": 1, "artist_name": 1, "id": 1})
    if not target_user:
        raise HTTPException(status_code=404, detail="User not found")

    name = target_user.get("artist_name", target_user.get("name", "there"))
    title = item.get("title", "your project")
    item_label = "release" if lead_type == "draft_release" else "beat"

    email_body = f"""<p style="color:#ccc;font-size:15px;margin:0 0 16px;">Hey {name}!</p>
    <p style="color:#999;font-size:14px;line-height:1.7;margin:0 0 20px;">We noticed you started working on <strong style="color:#fff;">{title}</strong> but haven't finished it yet. Pick up where you left off — your {item_label} is saved as a draft.</p>
    <div style="background:#111;border:1px solid #222;border-radius:12px;padding:20px;margin:20px 0;text-align:center;">
    <p style="color:#FFD700;font-size:18px;font-weight:bold;margin:0;">"{title}"</p>
    <p style="color:#999;font-size:13px;margin:4px 0 0;">Saved as draft — ready for you to finish</p>
    </div>
    <div style="text-align:center;margin:24px 0;">
    <a href="{FRONTEND_URL}/dashboard" style="background:linear-gradient(90deg,#7C4DFF,#E040FB);color:white;padding:14px 36px;border-radius:10px;text-decoration:none;font-weight:bold;font-size:14px;display:inline-block;">Continue Where You Left Off</a>
    </div>
    <p style="color:#888;font-size:13px;text-align:center;">Your fans are waiting. Let's finish this!</p>"""
    html = email_base(
        "linear-gradient(135deg,#FFD700 0%,#FFA000 100%)",
        "Don't Leave Your Music Behind!",
        email_body,
        "Kalmori Distribution — We're here to help"
    )
    import asyncio
    asyncio.ensure_future(send_email(target_user["email"], f"Kalmori: Your {item_label} \"{title}\" is waiting for you", html))

    # In-app notification
    await db.notifications.insert_one({
        "id": f"notif_{uuid.uuid4().hex[:12]}",
        "user_id": target_user["id"],
        "type": "draft_reminder",
        "message": f"Don't forget to finish your {item_label} \"{title}\"! It's saved as a draft.",
        "read": False,
        "created_at": datetime.now(timezone.utc).isoformat(),
    })

    # Mark as reminded
    await collection.update_one({"id": lead_id}, {"$set": {"reminder_sent": True}})
    return {"message": f"Reminder sent to {target_user['email']}"}


@email_router.post("/admin/leads/send-all-reminders")
async def send_all_lead_reminders(request: Request):
    """Send reminders to all stale leads"""
    from server import get_current_user
    user = await get_current_user(request)
    if user.get("role") != "admin":
        raise HTTPException(status_code=403, detail="Admin only")

    now = datetime.now(timezone.utc)
    stale_threshold = now - timedelta(hours=24)
    sent_count = 0

    for collection_name, lead_type, user_id_field, item_label in [
        ("releases", "draft_release", "artist_id", "release"),
        ("beats", "draft_beat", "producer_id", "beat"),
    ]:
        col = db[collection_name]
        items = await col.find(
            {"status": {"$in": ["draft", "pending", "inactive"]}, "reminder_sent": {"$ne": True}}, {"_id": 0}
        ).to_list(500)
        for item in items:
            created = item.get("created_at", "")
            if not created:
                continue
            try:
                created_dt = datetime.fromisoformat(created.replace("Z", "+00:00"))
                if created_dt >= stale_threshold:
                    continue
            except:
                continue
            target_user = await db.users.find_one({"id": item.get(user_id_field)}, {"_id": 0, "email": 1, "name": 1, "artist_name": 1, "id": 1})
            if not target_user:
                continue
            name = target_user.get("artist_name", target_user.get("name", "there"))
            title = item.get("title", "your project")
            email_body = f"""<p style="color:#ccc;font-size:15px;">Hey {name}!</p>
            <p style="color:#999;font-size:14px;line-height:1.7;">You started working on <strong style="color:#fff;">{title}</strong> but didn't finish. Your {item_label} is saved — pick up where you left off!</p>
            <div style="text-align:center;margin:24px 0;">
            <a href="{FRONTEND_URL}/dashboard" style="background:linear-gradient(90deg,#7C4DFF,#E040FB);color:white;padding:14px 36px;border-radius:10px;text-decoration:none;font-weight:bold;font-size:14px;display:inline-block;">Continue Now</a></div>"""
            html = email_base("linear-gradient(135deg,#FFD700 0%,#FFA000 100%)", "Finish Your Draft!", email_body, "Kalmori Distribution")
            import asyncio
            asyncio.ensure_future(send_email(target_user["email"], f"Kalmori: Your {item_label} \"{title}\" is waiting", html))
            await db.notifications.insert_one({
                "id": f"notif_{uuid.uuid4().hex[:12]}",
                "user_id": target_user["id"],
                "type": "draft_reminder",
                "message": f"Don't forget to finish your {item_label} \"{title}\"!",
                "read": False,
                "created_at": now.isoformat(),
            })
            await col.update_one({"id": item["id"]}, {"$set": {"reminder_sent": True}})
            sent_count += 1

    return {"message": f"Sent {sent_count} reminder(s)", "sent_count": sent_count}


# ============= EMAIL DOMAIN MANAGEMENT (Admin) =============

class DomainInput(BaseModel):
    domain: str

@email_router.post("/admin/email/domain")
async def add_email_domain(data: DomainInput, request: Request):
    """Add a custom sending domain to Resend"""
    from server import get_current_user
    user = await get_current_user(request)
    if user.get("role") != "admin":
        raise HTTPException(status_code=403, detail="Admin only")
    if not resend or not RESEND_API_KEY:
        raise HTTPException(status_code=500, detail="Resend API not configured")

    domain_name = data.domain.strip().lower()
    if not domain_name or "." not in domain_name:
        raise HTTPException(status_code=400, detail="Invalid domain name")

    # Check if domain already exists in our DB
    existing = await db.email_domains.find_one({"domain": domain_name}, {"_id": 0})
    if existing:
        raise HTTPException(status_code=400, detail="Domain already added. Use verify to check status.")

    try:
        import asyncio
        result = await asyncio.to_thread(resend.Domains.create, {"name": domain_name, "region": "us-east-1"})
        # Resend returns domain object with DNS records
        domain_data = result if isinstance(result, dict) else result.__dict__ if hasattr(result, '__dict__') else {"id": str(result)}

        # Extract records from response
        records = []
        if hasattr(result, 'records') and result.records:
            for rec in result.records:
                rec_dict = rec if isinstance(rec, dict) else rec.__dict__ if hasattr(rec, '__dict__') else {}
                records.append({
                    "record": rec_dict.get("record", rec_dict.get("type", "")),
                    "name": rec_dict.get("name", ""),
                    "type": rec_dict.get("type", ""),
                    "ttl": rec_dict.get("ttl", "Auto"),
                    "value": rec_dict.get("value", ""),
                    "status": rec_dict.get("status", "not_started"),
                    "priority": rec_dict.get("priority", None),
                })

        domain_id = domain_data.get("id", "") if isinstance(domain_data, dict) else getattr(result, "id", "")
        status = domain_data.get("status", "pending") if isinstance(domain_data, dict) else getattr(result, "status", "pending")

        doc = {
            "id": f"domain_{uuid.uuid4().hex[:12]}",
            "resend_domain_id": str(domain_id),
            "domain": domain_name,
            "status": status,
            "records": records,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "activated": False,
        }
        await db.email_domains.insert_one(doc)
        doc.pop("_id", None)
        return doc

    except Exception as e:
        logger.error(f"Failed to add domain to Resend: {e}")
        raise HTTPException(status_code=500, detail=f"Resend API error: {str(e)}")


@email_router.get("/admin/email/domain")
async def get_email_domains(request: Request):
    """Get all configured email domains"""
    from server import get_current_user
    user = await get_current_user(request)
    if user.get("role") != "admin":
        raise HTTPException(status_code=403, detail="Admin only")
    domains = await db.email_domains.find({}, {"_id": 0}).sort("created_at", -1).to_list(20)
    current_sender = os.environ.get("SENDER_EMAIL", "onboarding@resend.dev")
    return {"domains": domains, "current_sender": current_sender}


@email_router.post("/admin/email/domain/{domain_id}/verify")
async def verify_email_domain(domain_id: str, request: Request):
    """Trigger domain verification in Resend"""
    from server import get_current_user
    user = await get_current_user(request)
    if user.get("role") != "admin":
        raise HTTPException(status_code=403, detail="Admin only")
    if not resend or not RESEND_API_KEY:
        raise HTTPException(status_code=500, detail="Resend API not configured")

    domain_doc = await db.email_domains.find_one({"id": domain_id}, {"_id": 0})
    if not domain_doc:
        raise HTTPException(status_code=404, detail="Domain not found")

    try:
        import asyncio
        result = await asyncio.to_thread(resend.Domains.verify, domain_doc["resend_domain_id"])

        # Also get latest domain info
        domain_info = await asyncio.to_thread(resend.Domains.get, domain_doc["resend_domain_id"])
        info_dict = domain_info if isinstance(domain_info, dict) else domain_info.__dict__ if hasattr(domain_info, '__dict__') else {}

        new_status = info_dict.get("status", domain_doc.get("status", "pending")) if isinstance(info_dict, dict) else getattr(domain_info, "status", "pending")

        # Update records from latest info
        records = []
        raw_records = info_dict.get("records", []) if isinstance(info_dict, dict) else getattr(domain_info, "records", [])
        for rec in raw_records:
            rec_dict = rec if isinstance(rec, dict) else rec.__dict__ if hasattr(rec, '__dict__') else {}
            records.append({
                "record": rec_dict.get("record", rec_dict.get("type", "")),
                "name": rec_dict.get("name", ""),
                "type": rec_dict.get("type", ""),
                "ttl": rec_dict.get("ttl", "Auto"),
                "value": rec_dict.get("value", ""),
                "status": rec_dict.get("status", "not_started"),
                "priority": rec_dict.get("priority", None),
            })

        await db.email_domains.update_one({"id": domain_id}, {"$set": {
            "status": new_status,
            "records": records if records else domain_doc.get("records", []),
            "last_checked": datetime.now(timezone.utc).isoformat(),
        }})

        updated = await db.email_domains.find_one({"id": domain_id}, {"_id": 0})
        return updated

    except Exception as e:
        logger.error(f"Domain verification failed: {e}")
        raise HTTPException(status_code=500, detail=f"Verification error: {str(e)}")


@email_router.post("/admin/email/domain/{domain_id}/activate")
async def activate_email_domain(domain_id: str, request: Request):
    """Set a verified domain as the active sender domain"""
    from server import get_current_user
    user = await get_current_user(request)
    if user.get("role") != "admin":
        raise HTTPException(status_code=403, detail="Admin only")

    domain_doc = await db.email_domains.find_one({"id": domain_id}, {"_id": 0})
    if not domain_doc:
        raise HTTPException(status_code=404, detail="Domain not found")

    if domain_doc.get("status") != "verified":
        raise HTTPException(status_code=400, detail="Domain must be verified before activation. Add the DNS records and click Verify.")

    new_sender = f"noreply@{domain_doc['domain']}"

    # Deactivate all other domains
    await db.email_domains.update_many({}, {"$set": {"activated": False}})
    await db.email_domains.update_one({"id": domain_id}, {"$set": {"activated": True}})

    # Update env var in memory and .env file
    global SENDER_EMAIL
    SENDER_EMAIL = new_sender
    os.environ["SENDER_EMAIL"] = new_sender

    # Update .env file
    env_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), ".env")
    try:
        with open(env_path, "r") as f:
            lines = f.readlines()
        new_lines = []
        found = False
        for line in lines:
            if line.startswith("SENDER_EMAIL="):
                new_lines.append(f"SENDER_EMAIL={new_sender}\n")
                found = True
            else:
                new_lines.append(line)
        if not found:
            new_lines.append(f"SENDER_EMAIL={new_sender}\n")
        with open(env_path, "w") as f:
            f.writelines(new_lines)
    except Exception as e:
        logger.error(f"Failed to update .env: {e}")

    return {"message": f"Domain activated! Emails will now be sent from {new_sender}", "sender_email": new_sender}


@email_router.delete("/admin/email/domain/{domain_id}")
async def delete_email_domain(domain_id: str, request: Request):
    """Remove a domain"""
    from server import get_current_user
    user = await get_current_user(request)
    if user.get("role") != "admin":
        raise HTTPException(status_code=403, detail="Admin only")

    domain_doc = await db.email_domains.find_one({"id": domain_id})
    if not domain_doc:
        raise HTTPException(status_code=404, detail="Domain not found")

    # Remove from Resend
    if resend and RESEND_API_KEY and domain_doc.get("resend_domain_id"):
        try:
            import asyncio
            await asyncio.to_thread(resend.Domains.remove, domain_doc["resend_domain_id"])
        except Exception as e:
            logger.warning(f"Failed to remove domain from Resend: {e}")

    # If this was active, revert to default
    if domain_doc.get("activated"):
        global SENDER_EMAIL
        SENDER_EMAIL = "onboarding@resend.dev"
        os.environ["SENDER_EMAIL"] = "onboarding@resend.dev"

    await db.email_domains.delete_one({"id": domain_id})
    return {"message": "Domain removed"}
