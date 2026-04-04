"""Page Builder Routes — Admin-only CMS for drag-and-drop page editing"""
from fastapi import APIRouter, HTTPException, Request
from datetime import datetime, timezone
import uuid
import logging
import copy

from core import db, require_admin

logger = logging.getLogger(__name__)
page_builder_router = APIRouter(prefix="/api")

# Default block templates for new blocks
BLOCK_TEMPLATES = {
    "hero": {
        "type": "hero",
        "content": {"title": "Your Headline Here", "subtitle": "Add a compelling subtitle", "buttonText": "Get Started", "buttonUrl": "/register"},
        "styles": {"backgroundColor": "#0A0A0A", "textColor": "#FFFFFF", "accentColor": "#7C4DFF", "padding": "100", "textAlign": "center"},
    },
    "text": {
        "type": "text",
        "content": {"heading": "Section Heading", "body": "Write your content here. Click to edit this text and make it your own."},
        "styles": {"backgroundColor": "#0A0A0A", "textColor": "#FFFFFF", "headingColor": "#FFFFFF", "padding": "60", "textAlign": "left", "maxWidth": "800"},
    },
    "image": {
        "type": "image",
        "content": {"imageUrl": "", "altText": "Image description", "caption": ""},
        "styles": {"backgroundColor": "#0A0A0A", "padding": "40", "borderRadius": "16", "maxWidth": "900"},
    },
    "features": {
        "type": "features",
        "content": {
            "heading": "Our Features",
            "subtitle": "Everything you need",
            "items": [
                {"icon": "MusicNotes", "title": "Feature One", "description": "Describe this feature", "color": "#7C4DFF"},
                {"icon": "ChartLineUp", "title": "Feature Two", "description": "Describe this feature", "color": "#E040FB"},
                {"icon": "Users", "title": "Feature Three", "description": "Describe this feature", "color": "#1DB954"},
            ]
        },
        "styles": {"backgroundColor": "#0A0A0A", "textColor": "#FFFFFF", "padding": "80", "columns": "3"},
    },
    "cta": {
        "type": "cta",
        "content": {"heading": "Ready to Get Started?", "subtitle": "Join thousands of artists already on the platform.", "buttonText": "Sign Up Free", "buttonUrl": "/register"},
        "styles": {"backgroundColor": "#111111", "textColor": "#FFFFFF", "accentColor": "#7C4DFF", "padding": "80"},
    },
    "testimonials": {
        "type": "testimonials",
        "content": {
            "heading": "What Artists Say",
            "items": [
                {"quote": "This platform changed everything for me.", "author": "Artist Name", "role": "Independent Artist"},
                {"quote": "The best tools for music distribution.", "author": "Producer Name", "role": "Producer"},
            ]
        },
        "styles": {"backgroundColor": "#0A0A0A", "textColor": "#FFFFFF", "accentColor": "#7C4DFF", "padding": "80"},
    },
    "stats": {
        "type": "stats",
        "content": {
            "items": [
                {"value": "10K+", "label": "Artists"},
                {"value": "1M+", "label": "Streams"},
                {"value": "50+", "label": "Countries"},
                {"value": "24/7", "label": "Support"},
            ]
        },
        "styles": {"backgroundColor": "#111111", "textColor": "#FFFFFF", "accentColor": "#7C4DFF", "padding": "60"},
    },
    "spacer": {
        "type": "spacer",
        "content": {},
        "styles": {"height": "60", "backgroundColor": "transparent"},
    },
    "two_column": {
        "type": "two_column",
        "content": {"leftHeading": "Left Column", "leftBody": "Content for the left side.", "rightHeading": "Right Column", "rightBody": "Content for the right side."},
        "styles": {"backgroundColor": "#0A0A0A", "textColor": "#FFFFFF", "padding": "80"},
    },
    "video": {
        "type": "video",
        "content": {"videoUrl": "", "title": "Video Title"},
        "styles": {"backgroundColor": "#0A0A0A", "padding": "60", "maxWidth": "900"},
    },
    "logo_bar": {
        "type": "logo_bar",
        "content": {
            "heading": "Distributed To",
            "items": ["Spotify", "Apple Music", "YouTube Music", "Amazon Music", "TikTok", "Tidal", "Deezer"]
        },
        "styles": {"backgroundColor": "#0A0A0A", "textColor": "#FFFFFF", "padding": "40"},
    },
    "pricing": {
        "type": "pricing",
        "content": {
            "heading": "Simple Pricing",
            "subtitle": "Choose the plan that fits your needs",
            "items": [
                {"name": "Free", "price": "$0", "period": "/mo", "features": ["Basic distribution", "Analytics"], "buttonText": "Start Free", "highlighted": False},
                {"name": "Pro", "price": "$9.99", "period": "/mo", "features": ["Unlimited distribution", "Advanced analytics", "Priority support"], "buttonText": "Go Pro", "highlighted": True},
            ]
        },
        "styles": {"backgroundColor": "#0A0A0A", "textColor": "#FFFFFF", "accentColor": "#7C4DFF", "padding": "80"},
    },
}


@page_builder_router.get("/admin/pages")
async def list_editable_pages(request: Request):
    """Admin: List all editable pages"""
    await require_admin(request)
    pages = await db.page_layouts.find({}, {"_id": 0}).sort("page_slug", 1).to_list(50)
    # Always include default pages even if not yet saved
    default_pages = [
        {"page_slug": "landing", "title": "Landing Page", "path": "/"},
        {"page_slug": "about", "title": "About Page", "path": "/about"},
        {"page_slug": "pricing", "title": "Pricing Page", "path": "/pricing"},
    ]
    existing_slugs = {p["page_slug"] for p in pages}
    for dp in default_pages:
        if dp["page_slug"] not in existing_slugs:
            dp["blocks"] = []
            dp["published"] = False
            dp["updated_at"] = None
            pages.append(dp)
    return {"pages": sorted(pages, key=lambda x: x.get("page_slug", ""))}


@page_builder_router.get("/admin/pages/{slug}")
async def get_page_layout(slug: str, request: Request):
    """Admin: Get a page layout for editing"""
    await require_admin(request)
    page = await db.page_layouts.find_one({"page_slug": slug}, {"_id": 0})
    if not page:
        return {"page_slug": slug, "title": slug.replace("-", " ").title() + " Page", "blocks": [], "published": False}
    return page


@page_builder_router.put("/admin/pages/{slug}")
async def save_page_layout(slug: str, request: Request):
    """Admin: Save a page layout (draft)"""
    await require_admin(request)
    body = await request.json()
    blocks = body.get("blocks", [])
    title = body.get("title", slug.replace("-", " ").title() + " Page")
    now = datetime.now(timezone.utc).isoformat()
    await db.page_layouts.update_one(
        {"page_slug": slug},
        {"$set": {
            "page_slug": slug, "title": title, "blocks": blocks,
            "updated_at": now, "draft": True,
        }},
        upsert=True
    )
    return {"message": "Layout saved", "page_slug": slug, "updated_at": now}


@page_builder_router.post("/admin/pages/{slug}/publish")
async def publish_page_layout(slug: str, request: Request):
    """Admin: Publish a page layout (makes it live)"""
    await require_admin(request)
    page = await db.page_layouts.find_one({"page_slug": slug}, {"_id": 0})
    if not page or not page.get("blocks"):
        raise HTTPException(status_code=400, detail="No layout to publish. Add blocks first.")
    now = datetime.now(timezone.utc).isoformat()
    await db.page_layouts.update_one(
        {"page_slug": slug},
        {"$set": {"published": True, "published_at": now, "draft": False}}
    )
    return {"message": "Page published!", "page_slug": slug, "published_at": now}


@page_builder_router.post("/admin/pages/{slug}/unpublish")
async def unpublish_page_layout(slug: str, request: Request):
    """Admin: Unpublish a page (reverts to default)"""
    await require_admin(request)
    await db.page_layouts.update_one(
        {"page_slug": slug},
        {"$set": {"published": False}}
    )
    return {"message": "Page unpublished. Default layout will be shown.", "page_slug": slug}


@page_builder_router.get("/admin/pages/block-templates/all")
async def get_block_templates(request: Request):
    """Admin: Get all available block templates"""
    await require_admin(request)
    templates = []
    for key, tmpl in BLOCK_TEMPLATES.items():
        templates.append({"key": key, **tmpl})
    return {"templates": templates}


@page_builder_router.post("/admin/pages/{slug}/add-block")
async def add_block_to_page(slug: str, request: Request):
    """Admin: Add a new block to a page"""
    await require_admin(request)
    body = await request.json()
    block_type = body.get("type")
    if block_type not in BLOCK_TEMPLATES:
        raise HTTPException(status_code=400, detail=f"Unknown block type: {block_type}")
    template = copy.deepcopy(BLOCK_TEMPLATES[block_type])
    new_block = {
        "id": f"blk_{uuid.uuid4().hex[:10]}",
        **template,
        "order": body.get("order", 999),
    }
    page = await db.page_layouts.find_one({"page_slug": slug})
    if not page:
        await db.page_layouts.insert_one({
            "page_slug": slug, "title": slug.replace("-", " ").title() + " Page",
            "blocks": [new_block], "published": False,
            "updated_at": datetime.now(timezone.utc).isoformat(),
        })
    else:
        await db.page_layouts.update_one(
            {"page_slug": slug},
            {"$push": {"blocks": new_block}, "$set": {"updated_at": datetime.now(timezone.utc).isoformat()}}
        )
    new_block.pop("_id", None)
    return new_block


@page_builder_router.delete("/admin/pages/{slug}/blocks/{block_id}")
async def delete_block(slug: str, block_id: str, request: Request):
    """Admin: Delete a block from a page"""
    await require_admin(request)
    await db.page_layouts.update_one(
        {"page_slug": slug},
        {"$pull": {"blocks": {"id": block_id}}, "$set": {"updated_at": datetime.now(timezone.utc).isoformat()}}
    )
    return {"message": "Block deleted", "block_id": block_id}


# ===== PUBLIC endpoint (no auth) =====
@page_builder_router.get("/pages/{slug}")
async def get_published_page(slug: str):
    """Public: Get a published page layout for rendering"""
    page = await db.page_layouts.find_one(
        {"page_slug": slug, "published": True}, {"_id": 0}
    )
    if not page:
        return {"page_slug": slug, "blocks": [], "published": False}
    return page
