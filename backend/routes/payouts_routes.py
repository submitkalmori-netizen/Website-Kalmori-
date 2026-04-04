"""Admin Payout Dashboard Routes — Payout management, scheduling, batch processing, CSV export"""
from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import StreamingResponse
from datetime import datetime, timezone
from io import BytesIO
import logging

from core import db, require_admin

logger = logging.getLogger(__name__)
payouts_router = APIRouter(prefix="/api")


@payouts_router.get("/admin/payouts")
async def admin_list_payouts(request: Request, status: str = None):
    """Admin: List all withdrawal requests with user details"""
    await require_admin(request)
    query = {} if not status or status == "all" else {"status": status}
    withdrawals = await db.withdrawals.find(query, {"_id": 0}).sort("created_at", -1).to_list(500)
    for w in withdrawals:
        user = await db.users.find_one({"id": w.get("user_id")}, {"_id": 0, "email": 1, "artist_name": 1, "name": 1})
        w["user_email"] = (user or {}).get("email", "")
        w["user_name"] = (user or {}).get("artist_name") or (user or {}).get("name", "Unknown")
    return {"withdrawals": withdrawals}


@payouts_router.get("/admin/payouts/summary")
async def admin_payouts_summary(request: Request):
    """Admin: Payout stats overview"""
    await require_admin(request)
    all_wd = await db.withdrawals.find({}, {"_id": 0}).to_list(1000)
    pending = [w for w in all_wd if w.get("status") == "pending"]
    processing = [w for w in all_wd if w.get("status") == "processing"]
    completed = [w for w in all_wd if w.get("status") == "completed"]
    failed = [w for w in all_wd if w.get("status") == "failed"]
    wallets = await db.wallets.find({}, {"_id": 0}).to_list(1000)
    total_balance = sum(w.get("balance", 0) for w in wallets)
    return {
        "pending_count": len(pending),
        "pending_amount": round(sum(w.get("amount", 0) for w in pending), 2),
        "processing_count": len(processing),
        "processing_amount": round(sum(w.get("amount", 0) for w in processing), 2),
        "completed_count": len(completed),
        "completed_amount": round(sum(w.get("amount", 0) for w in completed), 2),
        "failed_count": len(failed),
        "total_user_balances": round(total_balance, 2),
    }


@payouts_router.get("/admin/payouts/schedule")
async def get_payout_schedule(request: Request):
    """Admin: Get payout schedule config"""
    await require_admin(request)
    defaults = {"key": "schedule", "frequency": "monthly", "day_of_month": 1,
                "min_threshold": 100.0, "auto_process": False, "notify_email": True}
    config = await db.payout_settings.find_one({"key": "schedule"}, {"_id": 0})
    if not config:
        return defaults
    return {**defaults, **config}


@payouts_router.put("/admin/payouts/schedule")
async def update_payout_schedule(request: Request):
    """Admin: Update payout schedule config"""
    await require_admin(request)
    body = await request.json()
    update = {}
    for field in ["frequency", "day_of_month", "min_threshold", "auto_process", "notify_email"]:
        if field in body:
            update[field] = body[field]
    if update:
        update["updated_at"] = datetime.now(timezone.utc).isoformat()
        await db.payout_settings.update_one(
            {"key": "schedule"}, {"$set": update}, upsert=True
        )
    config = await db.payout_settings.find_one({"key": "schedule"}, {"_id": 0})
    return config


@payouts_router.post("/admin/payouts/auto-process")
async def auto_process_payouts(request: Request):
    """Admin: Auto-process all eligible pending payouts (balance >= threshold)"""
    await require_admin(request)
    config = await db.payout_settings.find_one({"key": "schedule"}, {"_id": 0})
    threshold = (config or {}).get("min_threshold", 100.0)
    notify = (config or {}).get("notify_email", True)
    pending = await db.withdrawals.find({"status": "pending"}, {"_id": 0}).to_list(1000)
    processed = 0
    notified = 0
    for w in pending:
        if w.get("amount", 0) < threshold:
            continue
        now_iso = datetime.now(timezone.utc).isoformat()
        await db.withdrawals.update_one({"id": w["id"]}, {"$set": {
            "status": "processing", "updated_at": now_iso,
            "auto_processed": True, "processing_started_at": now_iso,
        }})
        processed += 1
        if notify:
            try:
                user = await db.users.find_one({"id": w.get("user_id")}, {"_id": 0, "email": 1, "artist_name": 1, "name": 1})
                if user and user.get("email"):
                    from routes.email_routes import send_email
                    artist_name = user.get("artist_name") or user.get("name", "Artist")
                    await send_email(user["email"],
                        f"Kalmori Payout Processing - ${w['amount']:.2f}",
                        f"""<div style="font-family:Helvetica,Arial,sans-serif;max-width:600px;margin:0 auto;background:#000;color:#fff;border-radius:16px;overflow:hidden;">
                        <div style="background:linear-gradient(135deg,#7C4DFF,#E040FB);padding:30px;text-align:center;">
                        <h1 style="color:white;margin:0 0 4px;font-size:11px;letter-spacing:5px;font-weight:800;text-transform:uppercase;opacity:0.85;">KALMORI</h1>
                        <h2 style="color:white;margin:0;font-size:22px;">Payout Processing</h2>
                        </div>
                        <div style="padding:30px;">
                        <p style="color:#ccc;font-size:15px;">Hi {artist_name},</p>
                        <p style="color:#ccc;font-size:15px;">Your payout of <b>${w['amount']:.2f} USD</b> is now being processed.</p>
                        <div style="background:#111;border:1px solid #222;border-radius:12px;padding:20px;margin:20px 0;">
                        <p style="color:#888;font-size:13px;margin:0 0 8px;">Payout ID: {w['id']}</p>
                        <p style="color:#888;font-size:13px;margin:0 0 8px;">Method: {w.get('method', 'PayPal').upper()}</p>
                        <p style="color:#888;font-size:13px;margin:0;">Amount: <span style="color:#4CAF50;font-weight:bold;">${w['amount']:.2f}</span></p>
                        </div>
                        <p style="color:#888;font-size:13px;">You will receive your funds within 3-5 business days.</p>
                        <p style="color:#555;font-size:12px;margin-top:28px;padding-top:16px;border-top:1px solid #222;text-align:center;">Kalmori Digital Distribution | support@kalmori.org</p>
                        </div></div>""")
                    notified += 1
            except Exception as e:
                logger.warning(f"Payout notification email failed for {w['id']}: {e}")
    return {"message": f"Auto-processed {processed} payouts, {notified} notifications sent",
            "processed": processed, "notified": notified, "threshold": threshold}


@payouts_router.put("/admin/payouts/{withdrawal_id}")
async def admin_update_payout(withdrawal_id: str, request: Request):
    """Admin: Update payout status (pending -> processing -> completed/failed)"""
    await require_admin(request)
    body = await request.json()
    new_status = body.get("status")
    if new_status not in ["processing", "completed", "failed", "pending"]:
        raise HTTPException(status_code=400, detail="Invalid status")
    wd = await db.withdrawals.find_one({"id": withdrawal_id})
    if not wd:
        raise HTTPException(status_code=404, detail="Withdrawal not found")
    update = {"status": new_status, "updated_at": datetime.now(timezone.utc).isoformat()}
    if body.get("transaction_ref"):
        update["transaction_ref"] = body["transaction_ref"]
    if body.get("notes"):
        update["notes"] = body["notes"]
    if new_status == "completed":
        update["paid_at"] = datetime.now(timezone.utc).isoformat()
        await db.wallets.update_one(
            {"user_id": wd["user_id"]},
            {"$inc": {"pending_balance": -wd["amount"], "total_withdrawn": wd["amount"]}}
        )
    elif new_status == "failed":
        await db.wallets.update_one(
            {"user_id": wd["user_id"]},
            {"$inc": {"balance": wd["amount"], "pending_balance": -wd["amount"]}}
        )
    await db.withdrawals.update_one({"id": withdrawal_id}, {"$set": update})
    return {"message": f"Payout updated to {new_status}", "id": withdrawal_id}


@payouts_router.post("/admin/payouts/batch")
async def admin_batch_process(request: Request):
    """Admin: Batch update multiple payout statuses"""
    await require_admin(request)
    body = await request.json()
    ids = body.get("withdrawal_ids", [])
    new_status = body.get("status", "processing")
    if new_status not in ["processing", "completed", "failed"]:
        raise HTTPException(status_code=400, detail="Invalid status")
    updated = 0
    for wid in ids:
        wd = await db.withdrawals.find_one({"id": wid})
        if not wd:
            continue
        update = {"status": new_status, "updated_at": datetime.now(timezone.utc).isoformat()}
        if new_status == "completed":
            update["paid_at"] = datetime.now(timezone.utc).isoformat()
            await db.wallets.update_one({"user_id": wd["user_id"]},
                {"$inc": {"pending_balance": -wd["amount"], "total_withdrawn": wd["amount"]}})
        elif new_status == "failed":
            await db.wallets.update_one({"user_id": wd["user_id"]},
                {"$inc": {"balance": wd["amount"], "pending_balance": -wd["amount"]}})
        await db.withdrawals.update_one({"id": wid}, {"$set": update})
        updated += 1
    return {"message": f"{updated} payouts updated to {new_status}", "updated": updated}


@payouts_router.get("/admin/payouts/export")
async def admin_export_payouts(request: Request, status: str = "pending"):
    """Admin: Export payout report as CSV"""
    await require_admin(request)
    query = {} if status == "all" else {"status": status}
    withdrawals = await db.withdrawals.find(query, {"_id": 0}).sort("created_at", -1).to_list(1000)
    import csv
    import io
    text_buf = io.StringIO()
    writer = csv.writer(text_buf)
    writer.writerow(["ID", "User", "Email", "Amount (USD)", "Method", "PayPal Email", "Status", "Requested", "Paid At", "Transaction Ref", "Notes"])
    for w in withdrawals:
        user = await db.users.find_one({"id": w.get("user_id")}, {"_id": 0, "email": 1, "artist_name": 1})
        writer.writerow([
            w.get("id", ""), (user or {}).get("artist_name", ""), (user or {}).get("email", ""),
            f'{w.get("amount", 0):.2f}', w.get("method", ""), w.get("paypal_email", ""),
            w.get("status", ""), w.get("created_at", "")[:10], w.get("paid_at", "")[:10] if w.get("paid_at") else "",
            w.get("transaction_ref", ""), w.get("notes", ""),
        ])
    csv_bytes = text_buf.getvalue().encode("utf-8")
    return StreamingResponse(BytesIO(csv_bytes), media_type="text/csv",
        headers={"Content-Disposition": f'attachment; filename="Kalmori_Payouts_{status}_{datetime.now(timezone.utc).strftime("%Y%m%d")}.csv"'})
