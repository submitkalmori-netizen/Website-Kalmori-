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
