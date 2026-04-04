"""Page Builder Routes — Admin-only CMS for drag-and-drop page editing"""
from fastapi import APIRouter, HTTPException, Request, File, UploadFile, Response
from datetime import datetime, timezone
import uuid
import logging
import copy

from core import db, require_admin, APP_NAME, put_object, get_object

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


# ===== SEED CURRENT LAYOUTS — Pre-populate builder with actual site content =====
LANDING_SEED_BLOCKS = [
    {
        "id": "blk_hero_main", "type": "hero", "order": 0,
        "content": {
            "title": "G.O.A.T In Music Distribution",
            "subtitle": "Get your music on Spotify, Apple Music, TikTok, YouTube, Tidal and more. Keep 100% ownership of your music and stay in control of your career.",
            "buttonText": "DISTRIBUTE MY MUSIC ONLINE",
            "buttonUrl": "/register"
        },
        "styles": {"backgroundColor": "#000000", "textColor": "#FFFFFF", "accentColor": "#E040FB", "padding": "120", "textAlign": "left"}
    },
    {
        "id": "blk_logo_platforms", "type": "logo_bar", "order": 1,
        "content": {
            "heading": "DISTRIBUTE TO 150+ PLATFORMS",
            "items": ["Spotify", "Apple Music", "YouTube Music", "TikTok", "Amazon Music", "Deezer", "Tidal"]
        },
        "styles": {"backgroundColor": "#000000", "textColor": "#FFFFFF", "padding": "40"}
    },
    {
        "id": "blk_distribution", "type": "two_column", "order": 2,
        "content": {
            "leftHeading": "Unlimited Distribution Starting at $20/year",
            "leftBody": "Increase the reach of your music across the most popular stores & platforms. Empower yourself with unlimited distribution and get your music heard by a global audience.\n\nKeep 100% ownership of your music, maintaining creative control and authority in your music career.",
            "rightHeading": "150+ Streaming Platforms",
            "rightBody": "Your music goes live on Spotify, Apple Music, YouTube Music, TikTok, Amazon Music, Deezer, Tidal, and 140+ more digital stores worldwide."
        },
        "styles": {"backgroundColor": "#000000", "textColor": "#FFFFFF", "padding": "80"}
    },
    {
        "id": "blk_about", "type": "text", "order": 3,
        "content": {
            "heading": "What is Kalmori?",
            "body": "Your Independent Music Distribution Company\n\nKalmori is a leading global platform empowering independent artists to build sustainable careers. Through innovative technology and artist-first services, we offer distribution, publishing administration, and promotional tools that help musicians grow their audience and revenue.\n\nAs a pioneer in indie music distribution, Kalmori is dedicated to making music accessible while keeping artists in full control of their creative work."
        },
        "styles": {"backgroundColor": "#0a0a0a", "textColor": "#FFFFFF", "headingColor": "#FFFFFF", "padding": "80", "textAlign": "left", "maxWidth": "900"}
    },
    {
        "id": "blk_why_choose", "type": "two_column", "order": 4,
        "content": {
            "leftHeading": "Why Choose Kalmori — Best Choice of Music Distribution Companies",
            "leftBody": "- Unlimited music distribution worldwide\n- Direct access to 150+ digital stores and streaming services\n- Keep 100% ownership and control of your master recordings\n- Get paid directly with transparent royalty reporting and no hidden fees\n- Free ISRC and UPC codes included with every release\n- AI-powered metadata suggestions and analytics insights\n- Dedicated support team available to help you succeed",
            "rightHeading": "150+ Streaming Platforms",
            "rightBody": "We connect you to every major digital store and streaming service globally, so your music reaches fans everywhere."
        },
        "styles": {"backgroundColor": "#000000", "textColor": "#FFFFFF", "padding": "80"}
    },
    {
        "id": "blk_stream_distribute", "type": "two_column", "order": 5,
        "content": {
            "leftHeading": "Stream & Distribute Your Music Without a Label",
            "leftBody": "Sell Your Music Online Worldwide\n\nBefore platforms like Kalmori, artists needed a label to get their music sold online. We changed that. Choose an unlimited distribution plan, upload your music, and we'll do the rest. Your music will hit top digital stores in no time.",
            "rightHeading": "No Label Needed",
            "rightBody": "Upload your tracks, select your stores, and we handle the rest. You stay independent and keep all your rights."
        },
        "styles": {"backgroundColor": "#0a0a0a", "textColor": "#FFFFFF", "padding": "80"}
    },
    {
        "id": "blk_testimonials", "type": "testimonials", "order": 6,
        "content": {
            "heading": "What Are Artists Saying About Kalmori?",
            "items": [
                {"quote": "Kalmori changed my life. I can distribute my music on my own terms, keeping 100% of my rights and earnings.", "author": "Rising Star", "role": "Kalmori Artist"},
                {"quote": "The best platform for independent artists. The analytics and AI features help me understand my audience better.", "author": "Indie Producer", "role": "Kalmori Artist"},
                {"quote": "I recommend Kalmori to every artist I meet. They make distribution easy and manageable.", "author": "Beat Maker", "role": "Kalmori Artist"},
            ]
        },
        "styles": {"backgroundColor": "#000000", "textColor": "#FFFFFF", "accentColor": "#E040FB", "padding": "80"}
    },
    {
        "id": "blk_features_grid", "type": "features", "order": 7,
        "content": {
            "heading": "Everything You Need to Win",
            "subtitle": "More than just distribution. Kalmori gives you AI-powered tools, deep analytics, and everything to build a real music career.",
            "items": [
                {"icon": "MusicNotes", "title": "AI Release Strategy", "description": "Get AI-powered release plans with optimal timing, playlist targeting, and marketing recommendations tailored to your genre.", "color": "#E040FB"},
                {"icon": "ChartLineUp", "title": "Real-Time Analytics", "description": "Track streams, revenue, fan demographics, peak listening hours, and geographic data across all platforms in one dashboard.", "color": "#1DB954"},
                {"icon": "CurrencyDollar", "title": "Revenue & Royalty Calculator", "description": "See exactly what you earn per stream on each platform. Model different scenarios with our what-if royalty calculator.", "color": "#FFD700"},
                {"icon": "MusicNotes", "title": "Beat Marketplace", "description": "Browse, preview, and purchase professional instrumentals with 4-tier licensing. Producers sell beats with auto-generated contracts.", "color": "#9C27B0"},
                {"icon": "ShieldCheck", "title": "Digital Contracts & E-Sign", "description": "Every beat purchase generates a legally-binding PDF contract with e-signatures. Full admin tracking and audit trail.", "color": "#FF6B6B"},
                {"icon": "MusicNotes", "title": "AI Audio Watermarking", "description": "AI-generated voice tags automatically overlaid on beat previews. Clean versions unlock after purchase for full protection.", "color": "#00BCD4"},
                {"icon": "Users", "title": "In-App Messaging", "description": "Real-time chat with file sharing, audio messages, read receipts, and typing indicators. Collaborate without leaving the platform.", "color": "#2196F3"},
                {"icon": "CurrencyDollar", "title": "Producer Royalty Splits", "description": "Auto-calculated royalty splits between producers and artists on every beat stream and purchase. Credited directly to wallets.", "color": "#FF9800"},
                {"icon": "Users", "title": "Collaboration Hub", "description": "Post collaboration opportunities, find vocalists, producers, and engineers. Build your network and create together.", "color": "#E040FB"},
                {"icon": "Globe", "title": "Artist Public Profile", "description": "Your shareable link-in-bio page with audio previews, custom theme colors, QR code sharing, and pre-save campaigns.", "color": "#00BCD4"},
                {"icon": "Star", "title": "Release Leaderboard", "description": "See how your releases stack up. Track momentum, hot streaks, and compete with your own catalog.", "color": "#FF6B6B"},
                {"icon": "Target", "title": "Goal Tracking & Milestones", "description": "Set stream goals, revenue targets, and geographic reach milestones. Watch your progress and celebrate achievements.", "color": "#7C4DFF"},
            ]
        },
        "styles": {"backgroundColor": "#0a0a0a", "textColor": "#FFFFFF", "padding": "80", "columns": "3"}
    },
    {
        "id": "blk_promotion", "type": "two_column", "order": 8,
        "content": {
            "leftHeading": "Promotion Services",
            "leftBody": "Boost your reach with our professional promotion services. Get your music in front of the right audience across all major social platforms.\n\n- Instagram (Stories, Reels & Posts)\n- TikTok (Viral Marketing)\n- Email (Curator Outreach)\n- Playlists (Editorial Pitching)",
            "rightHeading": "Need Beats or Instrumentals?",
            "rightBody": "Can't make your own beats? No problem! Get professional instrumentals with full rights or lease options.\n\n- Exclusive Rights Available\n- Affordable Lease Options\n- All Genres: Hip-Hop, R&B, Afrobeats, Dancehall\n- Custom Beats on Request"
        },
        "styles": {"backgroundColor": "#000000", "textColor": "#FFFFFF", "padding": "80"}
    },
    {
        "id": "blk_publishing", "type": "two_column", "order": 9,
        "content": {
            "leftHeading": "Maximize Your Earnings with Music Publishing",
            "leftBody": "Distribution isn't the only way to make money. Your original songs generate publishing revenue with every stream, video creation, view, or live performance worldwide.\n\n- Collecting your royalties globally/worldwide\n- Tracking publishing royalties from Spotify, YouTube, TikTok, Radio\n- Offering advanced analytics on royalty sources\n- All while you keep 100% of your copyrights",
            "rightHeading": "Reach More Fans. Grow Your Career.",
            "rightBody": "Kalmori leverages innovative, in-house tools to elevate the ideal tracks for greater audience reach. Our comprehensive suite of tools, analytics, and promotion services gives you everything you need to succeed."
        },
        "styles": {"backgroundColor": "#000000", "textColor": "#FFFFFF", "padding": "80"}
    },
    {
        "id": "blk_stats_row", "type": "stats", "order": 10,
        "content": {
            "items": [
                {"value": "150+", "label": "Streaming Platforms"},
                {"value": "100%", "label": "Your Royalties"},
                {"value": "24/7", "label": "Analytics Dashboard"},
                {"value": "AI", "label": "Powered Strategy"},
            ]
        },
        "styles": {"backgroundColor": "#000000", "textColor": "#FFFFFF", "accentColor": "#E040FB", "padding": "60"}
    },
    {
        "id": "blk_young_artists", "type": "text", "order": 11,
        "content": {
            "heading": "Built for Young Artists & Producers",
            "body": "Whether you're just starting out or ready to take your career to the next level, Kalmori provides the tools, distribution, and support you need to succeed in the music industry.\n\nUpload your first track, get AI-powered release strategies, build your fanbase with real-time analytics, and share your artist profile with the world. All from one platform."
        },
        "styles": {"backgroundColor": "#000000", "textColor": "#FFFFFF", "headingColor": "#FFFFFF", "padding": "80", "textAlign": "center", "maxWidth": "800"}
    },
    {
        "id": "blk_pricing_quick", "type": "pricing", "order": 12,
        "content": {
            "heading": "Plans That Scale With You",
            "subtitle": "Simple, transparent pricing for every stage of your career",
            "items": [
                {"name": "FREE", "price": "$0", "period": "", "features": ["All platforms", "15-20% rev share", "Basic analytics"], "buttonText": "Start Free", "highlighted": False},
                {"name": "SINGLE", "price": "$20", "period": "/yr", "features": ["Up to 3 tracks", "100% royalties", "Free ISRC codes"], "buttonText": "Get Started", "highlighted": False},
                {"name": "ALBUM", "price": "$75", "period": "/yr", "features": ["7+ tracks", "Priority support", "Free ISRC & UPC"], "buttonText": "Best Value", "highlighted": True},
            ]
        },
        "styles": {"backgroundColor": "#0a0a0a", "textColor": "#FFFFFF", "accentColor": "#FFD700", "padding": "80"}
    },
    {
        "id": "blk_final_cta", "type": "cta", "order": 13,
        "content": {
            "heading": "Ready to Start Your Journey?",
            "subtitle": "Join thousands of artists distributing their music worldwide with Kalmori.",
            "buttonText": "GET STARTED FREE",
            "buttonUrl": "/register"
        },
        "styles": {"backgroundColor": "#111111", "textColor": "#FFFFFF", "accentColor": "#E040FB", "padding": "100"}
    },
]

ABOUT_SEED_BLOCKS = [
    {
        "id": "blk_about_hero", "type": "hero", "order": 0,
        "content": {
            "title": "About Kalmori",
            "subtitle": "Empowering independent artists worldwide with cutting-edge distribution, AI-powered tools, and a community that puts artists first.",
            "buttonText": "GET STARTED",
            "buttonUrl": "/register"
        },
        "styles": {"backgroundColor": "#0A0A0A", "textColor": "#FFFFFF", "accentColor": "#E040FB", "padding": "100", "textAlign": "center"}
    },
    {
        "id": "blk_about_values", "type": "features", "order": 1,
        "content": {
            "heading": "Our Values",
            "subtitle": "What drives everything we do",
            "items": [
                {"icon": "Star", "title": "Artist First", "description": "Every decision we make puts artists first", "color": "#E53935"},
                {"icon": "ShieldCheck", "title": "Transparency", "description": "No hidden fees, no surprises", "color": "#7C4DFF"},
                {"icon": "Lightning", "title": "Innovation", "description": "Always improving our platform", "color": "#FFD700"},
                {"icon": "Users", "title": "Community", "description": "Building a family of artists", "color": "#E040FB"},
            ]
        },
        "styles": {"backgroundColor": "#0A0A0A", "textColor": "#FFFFFF", "padding": "80", "columns": "4"}
    },
    {
        "id": "blk_about_mission", "type": "text", "order": 2,
        "content": {
            "heading": "Our Mission",
            "body": "Kalmori exists to democratize music distribution. We believe every artist deserves the tools, reach, and support that were once only available to major label artists.\n\nOur platform combines AI-powered insights, seamless distribution to 150+ stores, and a vibrant community of artists and producers — all in one place."
        },
        "styles": {"backgroundColor": "#111111", "textColor": "#FFFFFF", "headingColor": "#FFFFFF", "padding": "80", "textAlign": "center", "maxWidth": "800"}
    },
    {
        "id": "blk_about_stats", "type": "stats", "order": 3,
        "content": {
            "items": [
                {"value": "150+", "label": "Stores & Platforms"},
                {"value": "100%", "label": "Artist Ownership"},
                {"value": "AI", "label": "Powered Tools"},
                {"value": "24/7", "label": "Support"},
            ]
        },
        "styles": {"backgroundColor": "#0A0A0A", "textColor": "#FFFFFF", "accentColor": "#E040FB", "padding": "60"}
    },
    {
        "id": "blk_about_cta", "type": "cta", "order": 4,
        "content": {
            "heading": "Join the Movement",
            "subtitle": "Start your journey with Kalmori today and take control of your music career.",
            "buttonText": "SIGN UP FREE",
            "buttonUrl": "/register"
        },
        "styles": {"backgroundColor": "#111111", "textColor": "#FFFFFF", "accentColor": "#E040FB", "padding": "80"}
    },
]

PRICING_SEED_BLOCKS = [
    {
        "id": "blk_pricing_hero", "type": "hero", "order": 0,
        "content": {
            "title": "Simple, Transparent Pricing",
            "subtitle": "Choose the plan that fits your career stage. No hidden fees. Keep 100% of your royalties on paid plans.",
            "buttonText": "",
            "buttonUrl": ""
        },
        "styles": {"backgroundColor": "#0A0A0A", "textColor": "#FFFFFF", "accentColor": "#E040FB", "padding": "80", "textAlign": "center"}
    },
    {
        "id": "blk_pricing_main", "type": "pricing", "order": 1,
        "content": {
            "heading": "Distribution Plans",
            "subtitle": "Every plan includes access to 150+ digital stores worldwide",
            "items": [
                {"name": "Free", "price": "$0", "period": "/forever", "features": ["All platforms", "15-20% revenue share", "Basic analytics", "Community support"], "buttonText": "Start Free", "highlighted": False},
                {"name": "Rise", "price": "$20", "period": "/year", "features": ["Up to 3 tracks", "100% royalties", "Free ISRC codes", "AI release strategy", "Fan analytics"], "buttonText": "Get Rise", "highlighted": False},
                {"name": "Pro", "price": "$75", "period": "/year", "features": ["Unlimited tracks", "100% royalties", "Free ISRC & UPC", "Priority support", "Revenue analytics", "Beat marketplace access"], "buttonText": "Go Pro", "highlighted": True},
            ]
        },
        "styles": {"backgroundColor": "#0A0A0A", "textColor": "#FFFFFF", "accentColor": "#FFD700", "padding": "80"}
    },
    {
        "id": "blk_pricing_features", "type": "features", "order": 2,
        "content": {
            "heading": "What's Included in Every Plan",
            "subtitle": "All the tools you need to succeed",
            "items": [
                {"icon": "Globe", "title": "150+ Stores", "description": "Spotify, Apple Music, YouTube, TikTok, Amazon, and more", "color": "#1DB954"},
                {"icon": "ChartLineUp", "title": "Analytics", "description": "Track your streams, revenue, and fan demographics", "color": "#7C4DFF"},
                {"icon": "ShieldCheck", "title": "Keep Your Rights", "description": "You always own 100% of your master recordings", "color": "#E040FB"},
            ]
        },
        "styles": {"backgroundColor": "#111111", "textColor": "#FFFFFF", "padding": "60", "columns": "3"}
    },
    {
        "id": "blk_pricing_cta", "type": "cta", "order": 3,
        "content": {
            "heading": "Ready to Distribute Your Music?",
            "subtitle": "Join thousands of independent artists already growing with Kalmori.",
            "buttonText": "GET STARTED FREE",
            "buttonUrl": "/register"
        },
        "styles": {"backgroundColor": "#0A0A0A", "textColor": "#FFFFFF", "accentColor": "#E040FB", "padding": "80"}
    },
]


@page_builder_router.post("/admin/pages/{slug}/seed-defaults")
async def seed_page_defaults(slug: str, request: Request):
    """Admin: Pre-populate a page with blocks matching the current website layout"""
    await require_admin(request)

    seeds = {
        "landing": ("Landing Page", LANDING_SEED_BLOCKS),
        "about": ("About Page", ABOUT_SEED_BLOCKS),
        "pricing": ("Pricing Page", PRICING_SEED_BLOCKS),
    }

    if slug not in seeds:
        raise HTTPException(status_code=400, detail=f"No seed template for page: {slug}")

    title, blocks = seeds[slug]
    now = datetime.now(timezone.utc).isoformat()

    await db.page_layouts.update_one(
        {"page_slug": slug},
        {"$set": {
            "page_slug": slug,
            "title": title,
            "blocks": copy.deepcopy(blocks),
            "published": False,
            "updated_at": now,
        }},
        upsert=True,
    )

    return {"message": f"Seeded {len(blocks)} blocks for {title}", "page_slug": slug, "block_count": len(blocks)}


@page_builder_router.post("/admin/seed-all-pages")
async def seed_all_pages(request: Request):
    """Admin: Pre-populate ALL pages with current website content"""
    await require_admin(request)
    now = datetime.now(timezone.utc).isoformat()
    results = []

    for slug, (title, blocks) in [("landing", ("Landing Page", LANDING_SEED_BLOCKS)), ("about", ("About Page", ABOUT_SEED_BLOCKS)), ("pricing", ("Pricing Page", PRICING_SEED_BLOCKS))]:
        await db.page_layouts.update_one(
            {"page_slug": slug},
            {"$set": {
                "page_slug": slug, "title": title,
                "blocks": copy.deepcopy(blocks),
                "published": False, "updated_at": now,
            }},
            upsert=True,
        )
        results.append({"slug": slug, "title": title, "blocks": len(blocks)})

    return {"message": "All pages seeded with current content", "pages": results}


# ===== FILE UPLOAD for page builder (admin only) =====
@page_builder_router.post("/files/upload")
async def upload_page_file(request: Request, file: UploadFile = File(...)):
    """Admin: Upload an image/file for use in page builder blocks"""
    await require_admin(request)
    if not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="Only image files are allowed")
    ext = file.filename.split(".")[-1] if "." in file.filename else "jpg"
    path = f"{APP_NAME}/page-builder/{uuid.uuid4().hex}.{ext}"
    data = await file.read()
    result = put_object(path, data, file.content_type)
    return {"path": result["path"], "url": result.get("url", result["path"])}


# ===== PUBLIC file serving for page builder assets =====
@page_builder_router.get("/public/files/{path:path}")
async def serve_public_file(path: str):
    """Public: Serve files uploaded via page builder (no auth required)"""
    if not path.startswith(f"{APP_NAME}/page-builder/"):
        raise HTTPException(status_code=403, detail="Access denied")
    try:
        data, content_type = get_object(path)
        return Response(content=data, media_type=content_type)
    except Exception as e:
        logger.error(f"Public file serve error: {e}")
        raise HTTPException(status_code=404, detail="File not found")


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
