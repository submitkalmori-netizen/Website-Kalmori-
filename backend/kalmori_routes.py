"""
Kalmori GitHub Backend Routes - Merged from user's GitHub repository.
Contains: CMS, Shopping Cart, Credits, Social Features, Promotion Orders,
Instrumental Requests, Testimonials, Theme, Payment Methods, Public Releases,
Video Serving, reCAPTCHA, and Admin CMS endpoints.
"""
from fastapi import APIRouter, HTTPException, Depends, Request, Query, Header
from fastapi.responses import HTMLResponse, StreamingResponse, Response
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from motor.motor_asyncio import AsyncIOMotorClient
from pydantic import BaseModel, EmailStr
from typing import List, Optional, Dict
from datetime import datetime, timezone, timedelta
import os
import uuid
import logging
import random
import string
import requests
import io
import jwt
import json

logger = logging.getLogger(__name__)

# Database connection (shared URI with main app)
mongo_url = os.environ['MONGO_URL']
_client = AsyncIOMotorClient(mongo_url)
db = _client[os.environ['DB_NAME']]

# Config
STORAGE_URL = "https://integrations.emergentagent.com/objstore/api/v1/storage"
EMERGENT_KEY = os.environ.get("EMERGENT_LLM_KEY")
STRIPE_API_KEY = os.environ.get('STRIPE_API_KEY')
RESEND_API_KEY = os.environ.get('RESEND_API_KEY')
SENDER_EMAIL = os.environ.get('SENDER_EMAIL', 'onboarding@resend.dev')
KALMORI_ADMIN_EMAIL = os.environ.get('ADMIN_EMAIL', 'submitkalmori@gmail.com')
RECAPTCHA_SECRET_KEY = os.environ.get('RECAPTCHA_SECRET_KEY')
RECAPTCHA_SITE_KEY = os.environ.get('RECAPTCHA_SITE_KEY')
ADMIN_PASSWORD = os.environ.get('ADMIN_PASSWORD', 'Admin123!')
JWT_SECRET = os.environ.get('JWT_SECRET')
JWT_ALGORITHM = "HS256"

# Initialize Resend
try:
    import resend
    if RESEND_API_KEY:
        resend.api_key = RESEND_API_KEY
        logger.info("Resend email service initialized (kalmori_routes)")
except ImportError:
    resend = None
    logger.warning("Resend not installed, email notifications disabled")

# Storage key (shared with main app via init)
_storage_key = None

def _init_storage():
    global _storage_key
    if _storage_key:
        return _storage_key
    if not EMERGENT_KEY:
        return None
    try:
        resp = requests.post(f"{STORAGE_URL}/init", json={"emergent_key": EMERGENT_KEY}, timeout=30)
        resp.raise_for_status()
        _storage_key = resp.json()["storage_key"]
        return _storage_key
    except Exception as e:
        logger.error(f"Storage init failed: {e}")
        return None

def _get_object(path: str) -> tuple:
    key = _init_storage()
    if not key:
        raise HTTPException(status_code=500, detail="Storage not available")
    resp = requests.get(f"{STORAGE_URL}/objects/{path}", headers={"X-Storage-Key": key}, timeout=60)
    resp.raise_for_status()
    return resp.content, resp.headers.get("Content-Type", "application/octet-stream")

# Create the router
kalmori_router = APIRouter(prefix="/api")
security = HTTPBearer(auto_error=False)

# ==================== AUTH HELPERS ====================

async def _get_current_user_bearer(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Auth via Bearer token (Kalmori mobile pattern)"""
    if not credentials:
        raise HTTPException(status_code=401, detail="Not authenticated")
    try:
        token = credentials.credentials
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        user_id = payload.get("sub")
        if not user_id:
            raise HTTPException(status_code=401, detail="Invalid token")
        user = await db.users.find_one({"id": user_id})
        if not user:
            raise HTTPException(status_code=401, detail="User not found")
        return user
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")

async def _get_current_user_flexible(request: Request):
    """Flexible auth: supports both cookies and Bearer token"""
    token = request.cookies.get("access_token")
    if not token:
        auth_header = request.headers.get("Authorization", "")
        if auth_header.startswith("Bearer "):
            token = auth_header[7:]
    if not token:
        raise HTTPException(status_code=401, detail="Not authenticated")
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        user_id = payload.get("sub")
        if not user_id:
            raise HTTPException(status_code=401, detail="Invalid token")
        user = await db.users.find_one({"id": user_id})
        if not user:
            raise HTTPException(status_code=401, detail="User not found")
        return user
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")

def _verify_admin_key(admin_key: str):
    if admin_key != ADMIN_PASSWORD:
        raise HTTPException(status_code=403, detail="Invalid admin credentials")
    return True

# ==================== EMAIL HELPER ====================

async def send_email_notification(to_email: str, subject: str, html_content: str):
    """Send email notification via Resend"""
    if not resend or not RESEND_API_KEY:
        logger.warning(f"Email not sent (no Resend config): {subject}")
        return
    try:
        params = {
            "from": f"Kalmori <{SENDER_EMAIL}>",
            "to": [to_email],
            "subject": subject,
            "html": html_content
        }
        resend.Emails.send(params)
        logger.info(f"Email sent to {to_email}: {subject}")
    except Exception as e:
        logger.error(f"Failed to send email: {e}")

# ==================== KALMORI CODE GENERATORS ====================

def generate_kalmori_isrc() -> str:
    country = "US"
    registrant = "KLM"
    year = str(datetime.now().year)[-2:]
    designation = ''.join(random.choices(string.digits, k=5))
    return f"{country}-{registrant}-{year}-{designation}"

def generate_kalmori_upc() -> str:
    prefix = "850"
    product = ''.join(random.choices(string.digits, k=8))
    code = prefix + product
    check_digit = str((10 - (sum(int(d) * (3 if i % 2 else 1) for i, d in enumerate(code)) % 10)) % 10)
    return code + check_digit

# ==================== RECAPTCHA VERIFICATION ====================

async def verify_recaptcha(token: str) -> bool:
    if not RECAPTCHA_SECRET_KEY:
        return True
    try:
        response = requests.post(
            'https://www.google.com/recaptcha/api/siteverify',
            data={'secret': RECAPTCHA_SECRET_KEY, 'response': token},
            timeout=10
        )
        result = response.json()
        return result.get('success', False)
    except Exception as e:
        logger.error(f"reCAPTCHA verification error: {e}")
        return False

# ==================== CMS MODELS ====================

class CMSSlide(BaseModel):
    id: Optional[str] = None
    image_url: str
    title: Optional[str] = ""
    subtitle: Optional[str] = ""
    order: int = 0
    active: bool = True

class CMSSlidesUpdate(BaseModel):
    admin_key: str
    slides: List[CMSSlide]

class CMSPricingPlan(BaseModel):
    id: str
    name: str
    price: float
    period: str = "/year"
    description: str
    features: List[str]
    badge: Optional[str] = None
    badge_color: Optional[str] = None
    highlight: bool = False
    order: int = 0

class CMSPricingUpdate(BaseModel):
    admin_key: str
    plans: List[CMSPricingPlan]

class CMSPageSection(BaseModel):
    section_id: str
    title: Optional[str] = ""
    subtitle: Optional[str] = ""
    content: Optional[str] = ""
    items: Optional[List[Dict]] = None

class CMSPageUpdate(BaseModel):
    admin_key: str
    sections: List[CMSPageSection]

class CMSLegalUpdate(BaseModel):
    admin_key: str
    title: str
    content: str
    last_updated: Optional[str] = None

class CMSStyle(BaseModel):
    backgroundColor: Optional[str] = "#000000"
    textColor: Optional[str] = "#ffffff"
    accentColor: Optional[str] = "#E040FB"
    secondaryColor: Optional[str] = "#7C4DFF"
    fontSize: Optional[str] = "16"
    fontWeight: Optional[str] = "normal"
    padding: Optional[str] = "20"
    borderRadius: Optional[str] = "0"
    borderColor: Optional[str] = "transparent"
    animation: Optional[str] = "none"

class CMSButton(BaseModel):
    text: str
    link: str
    backgroundColor: Optional[str] = "#E040FB"
    textColor: Optional[str] = "#ffffff"
    borderRadius: Optional[str] = "8"
    animation: Optional[str] = "none"

class CMSFullPageUpdate(BaseModel):
    admin_key: str
    page_name: Optional[str] = None
    meta_title: Optional[str] = None
    meta_description: Optional[str] = None
    sections: List[Dict]
    global_style: Optional[Dict] = None

# ==================== CART MODELS ====================

class CartItem(BaseModel):
    item_type: str
    plan_name: str
    plan_id: str
    years: int = 1
    price_per_year: float
    total_price: float
    features: List[str] = []
    metadata: Optional[Dict] = None

class CartItemResponse(BaseModel):
    id: str
    user_id: str
    item_type: str
    plan_name: str
    plan_id: str
    years: int
    price_per_year: float
    total_price: float
    features: List[str]
    metadata: Optional[Dict]
    added_at: datetime

class CartResponse(BaseModel):
    items: List[CartItemResponse]
    subtotal: float
    item_count: int

# ==================== CREDIT MODELS ====================

class CreditPurchaseRequest(BaseModel):
    package_id: str
    credits: int
    price: float

# ==================== PAYMENT METHOD MODELS ====================

class PaymentMethodCreate(BaseModel):
    method_type: str  # "paypal" or "bank"
    paypal_email: Optional[str] = None
    bank_name: Optional[str] = None
    account_holder: Optional[str] = None
    account_number: Optional[str] = None
    routing_number: Optional[str] = None

class PaymentMethodResponse(BaseModel):
    id: str
    user_id: str
    method_type: str
    paypal_email: Optional[str] = None
    bank_name: Optional[str] = None
    account_holder: Optional[str] = None
    account_number_last4: Optional[str] = None
    is_default: bool = False
    created_at: datetime

# ==================== WALLET/WITHDRAWAL MODELS ====================

class KalmoriWalletResponse(BaseModel):
    available_balance: float
    pending_balance: float
    total_earned: float
    total_withdrawn: float
    credits: int = 0

class KalmoriWithdrawalRequest(BaseModel):
    amount: float
    payment_method_id: str

class KalmoriWithdrawalResponse(BaseModel):
    id: str
    user_id: str
    amount: float
    payment_method_id: str
    payment_method_type: str
    status: str
    created_at: datetime
    processed_at: Optional[datetime] = None

# ==================== THEME MODEL ====================

class ThemeSettings(BaseModel):
    primary_color: str = "#E53935"
    secondary_color: str = "#000000"
    accent_color: str = "#FFD700"
    background_style: str = "dark"

# ==================== PROMOTION & INSTRUMENTAL MODELS ====================

class PromotionOrderRequest(BaseModel):
    artist_name: str
    email: str
    phone: Optional[str] = None
    song_title: str
    song_link: Optional[str] = None
    services: List[str] = []
    email_marketing: List[str] = []
    social_media_marketing: List[str] = []
    additional_notes: Optional[str] = None

class InstrumentalRequest(BaseModel):
    artist_name: str
    email: str
    phone: Optional[str] = None
    genre: str
    license_type: str
    tempo_range: Optional[str] = None
    mood: Optional[str] = None
    reference_tracks: Optional[str] = None
    budget: Optional[str] = None
    additional_notes: Optional[str] = None

# ==================== TESTIMONIAL MODELS ====================

class TestimonialCreate(BaseModel):
    name: str
    role: str
    quote: str
    image_url: Optional[str] = None
    rating: int = 5

class TestimonialResponse(BaseModel):
    id: str
    name: str
    role: str
    quote: str
    image_url: Optional[str] = None
    rating: int
    approved: bool
    created_at: datetime

# ==================== PROMOTION CHECKOUT MODEL ====================

class PromotionCheckoutRequest(BaseModel):
    package_id: str
    package_name: str
    amount: float

# ==================== DEFAULT CMS DATA ====================

DEFAULT_SLIDES = [
    {
        "id": "slide_1",
        "image_url": "https://customer-assets.emergentagent.com/job_9d65d3d0-8e4c-4ca7-97e3-3472b806edee/artifacts/0u0wegwo_vecteezy_ai-generated-a-professional-music-studio-with-a-large-mixing_36053665.jpeg",
        "title": "", "subtitle": "", "order": 0, "active": True
    },
    {
        "id": "slide_2",
        "image_url": "https://customer-assets.emergentagent.com/job_9d65d3d0-8e4c-4ca7-97e3-3472b806edee/artifacts/m7208zu9_vecteezy_microphone-in-the-studio-ready-to-record-voice-and-music_2220450.jpg",
        "title": "", "subtitle": "", "order": 1, "active": True
    },
    {
        "id": "slide_3",
        "image_url": "https://customer-assets.emergentagent.com/job_9d65d3d0-8e4c-4ca7-97e3-3472b806edee/artifacts/5izlaeot_vecteezy_professional-microphone-on-stage-in-a-bar-in-the-pink-rays_46833147.jpg",
        "title": "", "subtitle": "", "order": 2, "active": True
    }
]

DEFAULT_PRICING_PLANS = [
    {
        "id": "unlimited_single", "name": "Single", "price": 20.0, "period": "/year",
        "description": "Unlimited releases for 1-5 years (up to 3 tracks per release)",
        "features": ["Up to 3 tracks per release", "Choose 1-5 year subscription", "100% royalties", "All streaming platforms", "Free ISRC codes", "Analytics dashboard"],
        "badge": "UNLIMITED", "badge_color": "red", "highlight": False, "order": 0
    },
    {
        "id": "unlimited_ep", "name": "EP", "price": 35.0, "period": "/year",
        "description": "4-6 tracks per release",
        "features": ["4-6 tracks per release", "Choose 1-5 year subscription", "100% royalties", "All streaming platforms", "Free ISRC codes", "Analytics dashboard"],
        "badge": "UNLIMITED", "badge_color": "red", "highlight": False, "order": 1
    },
    {
        "id": "unlimited_album", "name": "Album", "price": 75.0, "period": "/year",
        "description": "7+ tracks per release",
        "features": ["7+ tracks per release", "Choose 1-5 year subscription", "100% royalties", "All streaming platforms", "Free ISRC & UPC codes", "Priority support"],
        "badge": "BEST DEAL", "badge_color": "gold", "highlight": True, "order": 2
    },
    {
        "id": "free_plan", "name": "Start Free", "price": 0.0, "period": "",
        "description": "15-20% revenue share",
        "features": ["No upfront cost", "15% rev share (singles)", "20% rev share (albums)", "All platforms included", "Basic analytics"],
        "badge": "FREE", "badge_color": "green", "highlight": False, "order": 3
    }
]

DEFAULT_INSTRUMENTALS_CONTENT = {
    "heroTitle": "Need Beats or Instrumentals?",
    "heroSubtitle": "Professional Production Services",
    "heroDescription": "Can't make your own beats? No problem! Get professional instrumentals with full rights or lease options.",
    "heroFeatures": [
        "Exclusive Rights Available", "Affordable Lease Options",
        "All Genres: Hip-Hop, R&B, Afrobeats, Dancehall", "Custom Beats on Request"
    ],
    "whyChooseTitle": "WHY CHOOSE US",
    "whyChooseItems": [
        {"icon": "musical-notes", "title": "Industry Quality", "description": "Professional studio-quality beats mixed and mastered to perfection"},
        {"icon": "flash", "title": "Fast Delivery", "description": "Get your beats delivered within 24-48 hours after purchase"},
        {"icon": "shield-checkmark", "title": "100% Original", "description": "All beats are original compositions with no samples"},
        {"icon": "headset", "title": "Support", "description": "Direct communication with the producer for revisions"}
    ],
    "licenseTiers": [
        {"id": "basic_lease", "name": "Basic Lease", "price": 29.99, "description": "Perfect for demos and mixtapes",
         "features": ["MP3 File (320kbps)", "Up to 5,000 streams", "Non-exclusive license", "Credit required"], "color": "#7C4DFF"},
        {"id": "premium_lease", "name": "Premium Lease", "price": 79.99, "description": "For serious releases",
         "features": ["WAV + MP3 Files", "Up to 50,000 streams", "Trackouts included", "Non-exclusive license", "Credit required"],
         "popular": True, "color": "#E040FB"},
        {"id": "unlimited_lease", "name": "Unlimited Lease", "price": 149.99, "description": "Maximum flexibility",
         "features": ["WAV + MP3 + Stems", "Unlimited streams", "Music video rights", "Non-exclusive license", "Credit required"], "color": "#FF4081"},
        {"id": "exclusive", "name": "Exclusive Rights", "price": 499.99, "description": "Full ownership",
         "features": ["All files + Stems", "Unlimited usage", "Full ownership", "Beat removed from catalog", "No credit required"], "color": "#FFD700"}
    ],
    "ctaTitle": "Ready to Get Started?",
    "ctaDescription": "Request a custom beat or browse our catalog"
}

DEFAULT_PAGE_STRUCTURES = {
    "homepage": {
        "page_name": "Homepage",
        "meta_title": "Kalmori - Your Music, Your Way",
        "meta_description": "Distribute your music to 150+ streaming platforms worldwide",
        "global_style": {"backgroundColor": "#000000", "textColor": "#ffffff", "accentColor": "#E040FB", "secondaryColor": "#7C4DFF"},
        "sections": [
            {"id": "hero", "type": "hero", "visible": True, "order": 0, "title": "YOUR MUSIC", "subtitle": "YOUR WAY",
             "content": "Distribute your music to 150+ streaming platforms worldwide. Keep 100% of your royalties.",
             "buttons": [{"text": "GET STARTED", "link": "/register", "backgroundColor": "#E040FB", "textColor": "#ffffff"},
                         {"text": "VIEW PRICING", "link": "/pricing", "backgroundColor": "transparent", "textColor": "#E040FB"}],
             "style": {"backgroundColor": "#000000", "textColor": "#ffffff", "animation": "fade"}},
            {"id": "platforms", "type": "platforms", "visible": True, "order": 1, "title": "DISTRIBUTE TO 150+ PLATFORMS",
             "items": [{"name": "Spotify", "icon": "musical-notes", "color": "#1DB954"}, {"name": "Apple Music", "icon": "logo-apple", "color": "#ffffff"},
                       {"name": "YouTube", "icon": "logo-youtube", "color": "#FF0000"}, {"name": "TikTok", "icon": "logo-tiktok", "color": "#ffffff"},
                       {"name": "Amazon", "icon": "logo-amazon", "color": "#FF9900"}, {"name": "Deezer", "icon": "disc", "color": "#FF0092"}],
             "style": {"backgroundColor": "#0a0a0a", "textColor": "#ffffff"}},
            {"id": "features", "type": "features", "visible": True, "order": 2, "title": "WHY CHOOSE KALMORI",
             "items": [{"icon": "cash-outline", "title": "100% Royalties", "description": "Keep all your earnings with our premium plans"},
                       {"icon": "globe-outline", "title": "Global Distribution", "description": "Reach fans on 150+ platforms worldwide"},
                       {"icon": "analytics-outline", "title": "Real-time Analytics", "description": "Track your streams and revenue instantly"},
                       {"icon": "shield-checkmark-outline", "title": "Rights Protection", "description": "Your music, your rights, always protected"}],
             "style": {"backgroundColor": "#000000", "textColor": "#ffffff"}},
            {"id": "cta", "type": "cta", "visible": True, "order": 3, "title": "READY TO START?",
             "subtitle": "Join thousands of artists distributing with Kalmori",
             "buttons": [{"text": "START FREE", "link": "/register", "backgroundColor": "#E040FB", "textColor": "#ffffff"}],
             "style": {"backgroundColor": "#111111", "textColor": "#ffffff"}}
        ]
    },
    "about": {
        "page_name": "About Us", "meta_title": "About Kalmori - Our Story",
        "sections": [
            {"id": "hero", "type": "hero", "visible": True, "order": 0, "title": "ABOUT KALMORI", "subtitle": "Empowering Artists Worldwide",
             "content": "We believe every artist deserves to be heard.", "style": {"backgroundColor": "#000000", "textColor": "#ffffff"}},
            {"id": "mission", "type": "text", "visible": True, "order": 1, "title": "OUR MISSION",
             "content": "To democratize music distribution and empower artists to reach their full potential.", "style": {"backgroundColor": "#0a0a0a", "textColor": "#ffffff"}},
            {"id": "values", "type": "features", "visible": True, "order": 2, "title": "OUR VALUES",
             "items": [{"icon": "heart-outline", "title": "Artist First", "description": "Every decision we make puts artists first"},
                       {"icon": "shield-outline", "title": "Transparency", "description": "No hidden fees, no surprises"},
                       {"icon": "flash-outline", "title": "Innovation", "description": "Always improving our platform"},
                       {"icon": "people-outline", "title": "Community", "description": "Building a family of artists"}],
             "style": {"backgroundColor": "#000000", "textColor": "#ffffff"}}
        ]
    },
    "services": {
        "page_name": "Our Services", "meta_title": "Kalmori Services",
        "sections": [
            {"id": "hero", "type": "hero", "visible": True, "order": 0, "title": "OUR SERVICES", "subtitle": "Everything You Need to Succeed",
             "style": {"backgroundColor": "#000000", "textColor": "#ffffff"}},
            {"id": "distribution", "type": "service", "visible": True, "order": 1, "title": "MUSIC DISTRIBUTION",
             "content": "Get your music on Spotify, Apple Music, and 150+ platforms worldwide.",
             "items": [{"text": "150+ streaming platforms"}, {"text": "Keep 100% royalties"}, {"text": "Free ISRC codes"}, {"text": "Real-time analytics"}],
             "buttons": [{"text": "START DISTRIBUTING", "link": "/pricing", "backgroundColor": "#E040FB"}],
             "style": {"backgroundColor": "#0a0a0a", "textColor": "#ffffff"}},
            {"id": "promotion", "type": "service", "visible": True, "order": 2, "title": "MUSIC PROMOTION",
             "content": "Boost your reach with our promotion services.",
             "items": [{"text": "Playlist pitching"}, {"text": "Social media campaigns"}, {"text": "Press coverage"}, {"text": "Influencer marketing"}],
             "buttons": [{"text": "PROMOTE YOUR MUSIC", "link": "/promoting", "backgroundColor": "#7C4DFF"}],
             "style": {"backgroundColor": "#000000", "textColor": "#ffffff"}}
        ]
    },
    "contact": {
        "page_name": "Contact Us", "meta_title": "Contact Kalmori",
        "sections": [
            {"id": "hero", "type": "hero", "visible": True, "order": 0, "title": "CONTACT US", "subtitle": "We're Here to Help",
             "style": {"backgroundColor": "#000000", "textColor": "#ffffff"}},
            {"id": "info", "type": "contact_info", "visible": True, "order": 1,
             "items": [{"icon": "mail-outline", "title": "Email", "content": "support@kalmori.org"},
                       {"icon": "call-outline", "title": "Phone", "content": "+1 (555) 123-4567"},
                       {"icon": "location-outline", "title": "Address", "content": "123 Music Street, Los Angeles, CA 90001"}],
             "style": {"backgroundColor": "#0a0a0a", "textColor": "#ffffff"}}
        ]
    },
    "promoting": {
        "page_name": "Promotion Services", "meta_title": "Kalmori Promotion",
        "sections": [
            {"id": "hero", "type": "hero", "visible": True, "order": 0, "title": "PROMOTION SERVICES", "subtitle": "Get Your Music Heard",
             "content": "Professional promotion services to boost your music career.", "style": {"backgroundColor": "#000000", "textColor": "#ffffff"}},
            {"id": "packages", "type": "pricing", "visible": True, "order": 1, "title": "PROMOTION PACKAGES",
             "items": [{"name": "Starter", "price": 99, "features": ["Social media promotion", "Basic playlist pitching", "1 week campaign"]},
                       {"name": "Professional", "price": 299, "features": ["Advanced playlist pitching", "Press outreach", "2 week campaign", "Analytics report"]},
                       {"name": "Premium", "price": 599, "features": ["VIP playlist placement", "Full press campaign", "Influencer marketing", "4 week campaign", "Dedicated manager"]}],
             "style": {"backgroundColor": "#0a0a0a", "textColor": "#ffffff"}}
        ]
    },
    "publishing": {
        "page_name": "Publishing Services", "meta_title": "Kalmori Publishing",
        "sections": [
            {"id": "hero", "type": "hero", "visible": True, "order": 0, "title": "PUBLISHING SERVICES", "subtitle": "Protect & Monetize Your Music",
             "content": "Comprehensive publishing services.", "style": {"backgroundColor": "#000000", "textColor": "#ffffff"}},
            {"id": "services", "type": "features", "visible": True, "order": 1, "title": "WHAT WE OFFER",
             "items": [{"icon": "document-text-outline", "title": "Copyright Registration", "description": "Protect your original works"},
                       {"icon": "cash-outline", "title": "Royalty Collection", "description": "Collect all your publishing royalties"},
                       {"icon": "sync-outline", "title": "Sync Licensing", "description": "Get your music in TV, films & ads"},
                       {"icon": "globe-outline", "title": "Global Administration", "description": "Worldwide rights management"}],
             "style": {"backgroundColor": "#0a0a0a", "textColor": "#ffffff"}}
        ]
    },
    "stores": {
        "page_name": "Distribution Stores", "meta_title": "Kalmori Stores - 150+ Platforms",
        "sections": [
            {"id": "hero", "type": "hero", "visible": True, "order": 0, "title": "150+ STORES", "subtitle": "Your Music Everywhere",
             "content": "We distribute to all major streaming platforms and digital stores worldwide.",
             "style": {"backgroundColor": "#000000", "textColor": "#ffffff"}},
            {"id": "stores_list", "type": "grid", "visible": True, "order": 1, "title": "ALL PLATFORMS",
             "items": [{"name": "Spotify"}, {"name": "Apple Music"}, {"name": "YouTube Music"}, {"name": "Amazon Music"}, {"name": "TikTok"}, {"name": "Deezer"}],
             "style": {"backgroundColor": "#0a0a0a", "textColor": "#ffffff"}}
        ]
    }
}

# ==================== CMS INITIALIZATION ====================

async def init_cms_content():
    """Initialize default CMS content if not exists"""
    slides = await db.cms_slides.find_one({"_id": "hero_slides"})
    if not slides:
        await db.cms_slides.insert_one({"_id": "hero_slides", "slides": DEFAULT_SLIDES, "updated_at": datetime.now(timezone.utc)})
        logger.info("Initialized default hero slides")

    pricing = await db.cms_pricing.find_one({"_id": "pricing_plans"})
    if not pricing:
        await db.cms_pricing.insert_one({"_id": "pricing_plans", "plans": DEFAULT_PRICING_PLANS, "updated_at": datetime.now(timezone.utc)})
        logger.info("Initialized default pricing plans")

    terms = await db.cms_legal.find_one({"_id": "terms"})
    if not terms:
        await db.cms_legal.insert_one({
            "_id": "terms", "title": "Terms & Conditions",
            "content": "# Terms and Conditions\n\nWelcome to Kalmori. By using our services, you agree to these terms...\n\n## 1. Acceptance of Terms\n\nBy accessing or using Kalmori's music distribution services, you agree to be bound by these Terms and Conditions.\n\n## 2. Service Description\n\nKalmori provides music distribution services to digital streaming platforms worldwide.\n\n## 3. User Responsibilities\n\nYou are responsible for ensuring you have all necessary rights to the music you distribute.\n\n## 4. Payment Terms\n\nPayment is required before distribution begins.\n\n## 5. Intellectual Property\n\nYou retain all rights to your music. Kalmori only acquires distribution rights.\n\n## 6. Termination\n\nEither party may terminate this agreement with 30 days notice.\n\n## 7. Contact\n\nFor questions, contact us at support@kalmori.org",
            "last_updated": datetime.now(timezone.utc).strftime("%B %d, %Y"), "updated_at": datetime.now(timezone.utc)
        })
        logger.info("Initialized terms and conditions")

    privacy = await db.cms_legal.find_one({"_id": "privacy"})
    if not privacy:
        await db.cms_legal.insert_one({
            "_id": "privacy", "title": "Privacy Policy",
            "content": "# Privacy Policy\n\nYour privacy is important to us at Kalmori.\n\n## 1. Information We Collect\n\nWe collect information you provide directly.\n\n## 2. How We Use Your Information\n\nWe use your information to provide our services.\n\n## 3. Information Sharing\n\nWe share your information with streaming platforms as necessary.\n\n## 4. Data Security\n\nWe implement industry-standard security measures.\n\n## 5. Your Rights\n\nYou have the right to access, correct, or delete your personal information.\n\n## 6. Cookies\n\nWe use cookies to improve your experience.\n\n## 7. Contact\n\nFor privacy concerns, contact us at privacy@kalmori.org",
            "last_updated": datetime.now(timezone.utc).strftime("%B %d, %Y"), "updated_at": datetime.now(timezone.utc)
        })
        logger.info("Initialized privacy policy")

# ==================== PUBLIC RELEASES ====================

@kalmori_router.get("/public-releases")
async def get_public_releases():
    """Get public releases - featured/showcase releases that are live"""
    pipeline = [
        {"$match": {"status": {"$in": ["distributed", "live"]}}},
        {"$sort": {"created_at": -1}},
        {"$limit": 50},
        {"$lookup": {"from": "tracks", "localField": "id", "foreignField": "release_id", "as": "tracks_data"}},
        {"$addFields": {"track_count": {"$size": "$tracks_data"}}},
        {"$project": {"tracks_data": 0, "_id": 0}}
    ]
    releases = await db.releases.aggregate(pipeline).to_list(50)
    return releases

# ==================== CMS PUBLIC ENDPOINTS ====================

@kalmori_router.get("/cms/slides")
async def get_cms_slides():
    slides_doc = await db.cms_slides.find_one({"_id": "hero_slides"})
    if not slides_doc:
        return {"slides": DEFAULT_SLIDES}
    return {"slides": slides_doc.get("slides", DEFAULT_SLIDES)}

@kalmori_router.get("/cms/hero-videos")
async def get_hero_video_urls():
    return {"videos": [{"id": 1, "path": "kalmori/videos/hero_video_1.mp4"}, {"id": 2, "path": "kalmori/videos/hero_video_2.mp4"}]}

@kalmori_router.get("/cms/pricing")
async def get_cms_pricing():
    pricing_doc = await db.cms_pricing.find_one({"_id": "pricing_plans"})
    if not pricing_doc:
        return {"plans": DEFAULT_PRICING_PLANS}
    return {"plans": pricing_doc.get("plans", DEFAULT_PRICING_PLANS)}

@kalmori_router.get("/cms/legal/{page_id}")
async def get_cms_legal(page_id: str):
    if page_id not in ["terms", "privacy"]:
        raise HTTPException(status_code=404, detail="Page not found")
    legal_doc = await db.cms_legal.find_one({"_id": page_id})
    if not legal_doc:
        raise HTTPException(status_code=404, detail="Content not found")
    return {"page_id": page_id, "title": legal_doc.get("title", ""), "content": legal_doc.get("content", ""), "last_updated": legal_doc.get("last_updated", "")}

@kalmori_router.get("/cms/pages")
async def get_all_cms_pages():
    return {"pages": [
        {"id": "slides", "name": "Hero Slides", "description": "Homepage slideshow images"},
        {"id": "pricing", "name": "Pricing Plans", "description": "Pricing page plans and features"},
        {"id": "terms", "name": "Terms & Conditions", "description": "Legal terms page"},
        {"id": "privacy", "name": "Privacy Policy", "description": "Privacy policy page"},
        {"id": "homepage", "name": "Homepage", "description": "Homepage content sections"},
        {"id": "promoting", "name": "Promoting", "description": "Promotion services page"},
        {"id": "publishing", "name": "Publishing", "description": "Publishing services page"},
        {"id": "services", "name": "Our Services", "description": "Services overview page"},
        {"id": "about", "name": "About Us", "description": "About page content"},
        {"id": "contact", "name": "Contact", "description": "Contact page information"}
    ]}

@kalmori_router.get("/cms/page/{page_id}")
async def get_full_page_content(page_id: str):
    page_doc = await db.cms_full_pages.find_one({"_id": page_id})
    if not page_doc:
        if page_id in DEFAULT_PAGE_STRUCTURES:
            return DEFAULT_PAGE_STRUCTURES[page_id]
        raise HTTPException(status_code=404, detail="Page not found")
    return {k: v for k, v in page_doc.items() if k != "_id"}

@kalmori_router.get("/cms/instrumentals")
async def get_instrumentals_content():
    content_doc = await db.cms_instrumentals.find_one({"_id": "instrumentals_page"})
    if not content_doc:
        return DEFAULT_INSTRUMENTALS_CONTENT
    return {k: v for k, v in content_doc.items() if k != "_id"}

# ==================== VIDEO SERVING ====================

@kalmori_router.get("/videos/{video_path:path}")
@kalmori_router.head("/videos/{video_path:path}")
async def serve_video(video_path: str, request: Request):
    try:
        full_path = f"kalmori/videos/{video_path}"
        data, content_type = _get_object(full_path)
        file_size = len(data)
        if request.method == "HEAD":
            return Response(headers={"Accept-Ranges": "bytes", "Content-Length": str(file_size), "Content-Type": "video/mp4", "Cache-Control": "public, max-age=31536000"})
        range_header = request.headers.get("range")
        if range_header:
            try:
                range_start, range_end = range_header.replace("bytes=", "").split("-")
                range_start = int(range_start) if range_start else 0
                range_end = int(range_end) if range_end else file_size - 1
                range_start = max(0, min(range_start, file_size - 1))
                range_end = max(range_start, min(range_end, file_size - 1))
                content_length = range_end - range_start + 1
                return StreamingResponse(io.BytesIO(data[range_start:range_end + 1]), status_code=206, media_type="video/mp4",
                    headers={"Accept-Ranges": "bytes", "Content-Range": f"bytes {range_start}-{range_end}/{file_size}", "Content-Length": str(content_length), "Cache-Control": "public, max-age=31536000"})
            except Exception:
                pass
        return StreamingResponse(io.BytesIO(data), media_type="video/mp4",
            headers={"Accept-Ranges": "bytes", "Content-Length": str(file_size), "Cache-Control": "public, max-age=31536000"})
    except Exception as e:
        logger.error(f"Error serving video {video_path}: {e}")
        raise HTTPException(status_code=404, detail="Video not found")

# ==================== CMS ADMIN ENDPOINTS ====================

@kalmori_router.get("/admin/cms/slides")
async def admin_get_slides(admin_key: str = None):
    if not admin_key or admin_key != ADMIN_PASSWORD:
        raise HTTPException(status_code=403, detail="Invalid admin credentials")
    slides_doc = await db.cms_slides.find_one({"_id": "hero_slides"})
    if not slides_doc:
        await init_cms_content()
        slides_doc = await db.cms_slides.find_one({"_id": "hero_slides"})
    return {"slides": slides_doc.get("slides", DEFAULT_SLIDES), "updated_at": slides_doc.get("updated_at")}

@kalmori_router.put("/admin/cms/slides")
async def admin_update_slides(update: CMSSlidesUpdate):
    _verify_admin_key(update.admin_key)
    await db.cms_slides.update_one({"_id": "hero_slides"},
        {"$set": {"slides": [slide.model_dump() for slide in update.slides], "updated_at": datetime.now(timezone.utc)}}, upsert=True)
    return {"success": True, "message": f"Updated {len(update.slides)} slides"}

@kalmori_router.get("/admin/cms/pricing")
async def admin_get_pricing(admin_key: str = None):
    if not admin_key or admin_key != ADMIN_PASSWORD:
        raise HTTPException(status_code=403, detail="Invalid admin credentials")
    pricing_doc = await db.cms_pricing.find_one({"_id": "pricing_plans"})
    if not pricing_doc:
        await init_cms_content()
        pricing_doc = await db.cms_pricing.find_one({"_id": "pricing_plans"})
    return {"plans": pricing_doc.get("plans", DEFAULT_PRICING_PLANS), "updated_at": pricing_doc.get("updated_at")}

@kalmori_router.put("/admin/cms/pricing")
async def admin_update_pricing(update: CMSPricingUpdate):
    _verify_admin_key(update.admin_key)
    await db.cms_pricing.update_one({"_id": "pricing_plans"},
        {"$set": {"plans": [plan.model_dump() for plan in update.plans], "updated_at": datetime.now(timezone.utc)}}, upsert=True)
    return {"success": True, "message": f"Updated {len(update.plans)} pricing plans"}

@kalmori_router.get("/admin/cms/legal/{page_id}")
async def admin_get_legal(page_id: str, admin_key: str = None):
    if not admin_key or admin_key != ADMIN_PASSWORD:
        raise HTTPException(status_code=403, detail="Invalid admin credentials")
    if page_id not in ["terms", "privacy"]:
        raise HTTPException(status_code=404, detail="Page not found")
    legal_doc = await db.cms_legal.find_one({"_id": page_id})
    if not legal_doc:
        await init_cms_content()
        legal_doc = await db.cms_legal.find_one({"_id": page_id})
    return {"page_id": page_id, "title": legal_doc.get("title", ""), "content": legal_doc.get("content", ""), "last_updated": legal_doc.get("last_updated", ""), "updated_at": legal_doc.get("updated_at")}

@kalmori_router.put("/admin/cms/legal/{page_id}")
async def admin_update_legal(page_id: str, update: CMSLegalUpdate):
    _verify_admin_key(update.admin_key)
    if page_id not in ["terms", "privacy"]:
        raise HTTPException(status_code=404, detail="Page not found")
    await db.cms_legal.update_one({"_id": page_id},
        {"$set": {"title": update.title, "content": update.content, "last_updated": update.last_updated or datetime.now(timezone.utc).strftime("%B %d, %Y"), "updated_at": datetime.now(timezone.utc)}}, upsert=True)
    return {"success": True, "message": f"Updated {page_id} page"}

@kalmori_router.get("/admin/cms/instrumentals")
async def admin_get_instrumentals_content(admin_key: str = None):
    if not admin_key or admin_key != ADMIN_PASSWORD:
        raise HTTPException(status_code=403, detail="Invalid admin credentials")
    content_doc = await db.cms_instrumentals.find_one({"_id": "instrumentals_page"})
    if not content_doc:
        return DEFAULT_INSTRUMENTALS_CONTENT
    return {k: v for k, v in content_doc.items() if k != "_id"}

@kalmori_router.put("/admin/cms/instrumentals")
async def admin_update_instrumentals_content(update: dict, admin_key: str = None):
    if not admin_key or admin_key != ADMIN_PASSWORD:
        raise HTTPException(status_code=403, detail="Invalid admin credentials")
    update_data = {k: v for k, v in update.items() if k != "admin_key"}
    update_data["updated_at"] = datetime.now(timezone.utc)
    await db.cms_instrumentals.update_one({"_id": "instrumentals_page"}, {"$set": update_data}, upsert=True)
    return {"success": True, "message": "Instrumentals page content updated"}

@kalmori_router.get("/admin/cms/page/{page_id}")
async def admin_get_page_content(page_id: str, admin_key: str = None):
    if not admin_key or admin_key != ADMIN_PASSWORD:
        raise HTTPException(status_code=403, detail="Invalid admin credentials")
    page_doc = await db.cms_pages.find_one({"_id": page_id})
    if not page_doc:
        return {"page_id": page_id, "page_name": page_id.replace("_", " ").title(), "sections": [], "updated_at": None}
    return {"page_id": page_id, "page_name": page_doc.get("page_name", page_id), "sections": page_doc.get("sections", []), "updated_at": page_doc.get("updated_at")}

@kalmori_router.put("/admin/cms/page/{page_id}")
async def admin_update_page_content(page_id: str, update: CMSPageUpdate):
    _verify_admin_key(update.admin_key)
    await db.cms_pages.update_one({"_id": page_id},
        {"$set": {"page_name": page_id.replace("_", " ").title(), "sections": [section.model_dump() for section in update.sections], "updated_at": datetime.now(timezone.utc)}}, upsert=True)
    return {"success": True, "message": f"Updated {page_id} page content"}

@kalmori_router.get("/admin/cms/fullpage/{page_id}")
async def admin_get_full_page(page_id: str, admin_key: str = None):
    if not admin_key or admin_key != ADMIN_PASSWORD:
        raise HTTPException(status_code=403, detail="Invalid admin credentials")
    page_doc = await db.cms_full_pages.find_one({"_id": page_id})
    if not page_doc:
        if page_id in DEFAULT_PAGE_STRUCTURES:
            default = DEFAULT_PAGE_STRUCTURES[page_id].copy()
            default["page_id"] = page_id
            return default
        return {"page_id": page_id, "page_name": page_id.replace("_", " ").title(), "sections": [],
                "global_style": {"backgroundColor": "#000000", "textColor": "#ffffff", "accentColor": "#E040FB"}, "updated_at": None}
    return {k: v for k, v in page_doc.items() if k != "_id"}

@kalmori_router.put("/admin/cms/fullpage/{page_id}")
async def admin_update_full_page(page_id: str, update: CMSFullPageUpdate):
    _verify_admin_key(update.admin_key)
    update_data = {"sections": update.sections, "updated_at": datetime.now(timezone.utc)}
    if update.page_name:
        update_data["page_name"] = update.page_name
    if update.meta_title:
        update_data["meta_title"] = update.meta_title
    if update.meta_description:
        update_data["meta_description"] = update.meta_description
    if update.global_style:
        update_data["global_style"] = update.global_style
    await db.cms_full_pages.update_one({"_id": page_id}, {"$set": update_data}, upsert=True)
    return {"success": True, "message": f"Updated {page_id} page"}

@kalmori_router.get("/admin/cms/all-pages")
async def admin_get_all_pages(admin_key: str = None):
    if not admin_key or admin_key != ADMIN_PASSWORD:
        raise HTTPException(status_code=403, detail="Invalid admin credentials")
    return {"pages": [
        {"id": "homepage", "name": "Homepage", "icon": "home-outline", "description": "Main landing page"},
        {"id": "pricing", "name": "Pricing", "icon": "pricetag-outline", "description": "Pricing plans page"},
        {"id": "about", "name": "About Us", "icon": "information-circle-outline", "description": "About the company"},
        {"id": "services", "name": "Services", "icon": "briefcase-outline", "description": "Services overview"},
        {"id": "promoting", "name": "Promotion", "icon": "megaphone-outline", "description": "Promotion services"},
        {"id": "publishing", "name": "Publishing", "icon": "document-outline", "description": "Publishing services"},
        {"id": "stores", "name": "Stores", "icon": "storefront-outline", "description": "Distribution platforms"},
        {"id": "contact", "name": "Contact", "icon": "mail-outline", "description": "Contact information"},
        {"id": "terms", "name": "Terms & Conditions", "icon": "document-text-outline", "description": "Legal terms"},
        {"id": "privacy", "name": "Privacy Policy", "icon": "shield-outline", "description": "Privacy policy"}
    ]}

# ==================== ADMIN RELEASES (admin_key based) ====================

@kalmori_router.get("/admin/releases-list")
async def admin_get_all_releases(admin_key: str = Query(...)):
    """Admin: Get all releases across all artists"""
    _verify_admin_key(admin_key)
    pipeline = [
        {"$sort": {"created_at": -1}},
        {"$limit": 100},
        {"$lookup": {"from": "tracks", "localField": "id", "foreignField": "release_id", "as": "tracks_data"}},
        {"$addFields": {"track_count": {"$size": "$tracks_data"}}},
        {"$project": {"tracks_data": 0, "_id": 0}}
    ]
    releases = await db.releases.aggregate(pipeline).to_list(100)
    return releases

# ==================== SHOPPING CART ====================

@kalmori_router.get("/cart", response_model=CartResponse)
async def get_cart(request: Request):
    current_user = await _get_current_user_flexible(request)
    cart_items = await db.cart.find({"user_id": current_user["id"]}).sort("added_at", -1).to_list(50)
    subtotal = sum(item.get("total_price", 0) for item in cart_items)
    items = [CartItemResponse(
        id=item["id"], user_id=item["user_id"], item_type=item["item_type"],
        plan_name=item["plan_name"], plan_id=item["plan_id"], years=item.get("years", 1),
        price_per_year=item["price_per_year"], total_price=item["total_price"],
        features=item.get("features", []), metadata=item.get("metadata"),
        added_at=item["added_at"]
    ) for item in cart_items]
    return CartResponse(items=items, subtotal=subtotal, item_count=len(items))

@kalmori_router.post("/cart/add", response_model=CartItemResponse)
async def add_to_cart(item: CartItem, request: Request):
    current_user = await _get_current_user_flexible(request)
    existing = await db.cart.find_one({"user_id": current_user["id"], "plan_id": item.plan_id})
    if existing:
        await db.cart.update_one({"id": existing["id"]}, {"$set": {"years": item.years, "total_price": item.total_price, "updated_at": datetime.now(timezone.utc)}})
        updated = await db.cart.find_one({"id": existing["id"]})
        return CartItemResponse(id=updated["id"], user_id=updated["user_id"], item_type=updated["item_type"],
            plan_name=updated["plan_name"], plan_id=updated["plan_id"], years=updated.get("years", 1),
            price_per_year=updated["price_per_year"], total_price=updated["total_price"],
            features=updated.get("features", []), metadata=updated.get("metadata"), added_at=updated["added_at"])

    cart_item_id = str(uuid.uuid4())
    cart_item = {
        "id": cart_item_id, "user_id": current_user["id"], "item_type": item.item_type,
        "plan_name": item.plan_name, "plan_id": item.plan_id, "years": item.years,
        "price_per_year": item.price_per_year, "total_price": item.total_price,
        "features": item.features, "metadata": item.metadata, "added_at": datetime.now(timezone.utc)
    }
    await db.cart.insert_one(cart_item)
    return CartItemResponse(**cart_item)

@kalmori_router.put("/cart/{item_id}")
async def update_cart_item(item_id: str, years: int, request: Request):
    current_user = await _get_current_user_flexible(request)
    cart_item = await db.cart.find_one({"id": item_id, "user_id": current_user["id"]})
    if not cart_item:
        raise HTTPException(status_code=404, detail="Cart item not found")
    if years < 1 or years > 5:
        raise HTTPException(status_code=400, detail="Years must be between 1 and 5")
    new_total = cart_item["price_per_year"] * years
    await db.cart.update_one({"id": item_id}, {"$set": {"years": years, "total_price": new_total, "updated_at": datetime.now(timezone.utc)}})
    return {"message": "Cart item updated", "new_total": new_total}

@kalmori_router.delete("/cart/{item_id}")
async def remove_from_cart(item_id: str, request: Request):
    current_user = await _get_current_user_flexible(request)
    result = await db.cart.delete_one({"id": item_id, "user_id": current_user["id"]})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Cart item not found")
    return {"message": "Item removed from cart"}

@kalmori_router.delete("/cart")
async def clear_cart(request: Request):
    current_user = await _get_current_user_flexible(request)
    await db.cart.delete_many({"user_id": current_user["id"]})
    return {"message": "Cart cleared"}

@kalmori_router.get("/cart/count")
async def get_cart_count(request: Request):
    current_user = await _get_current_user_flexible(request)
    count = await db.cart.count_documents({"user_id": current_user["id"]})
    return {"count": count}

@kalmori_router.post("/cart/checkout")
async def checkout_cart(origin_url: str, request: Request):
    from emergentintegrations.payments.stripe.checkout import StripeCheckout, CheckoutSessionRequest
    current_user = await _get_current_user_flexible(request)
    cart_items = await db.cart.find({"user_id": current_user["id"]}).to_list(50)
    if not cart_items:
        raise HTTPException(status_code=400, detail="Cart is empty")
    total_amount = sum(item.get("total_price", 0) for item in cart_items)
    if total_amount <= 0:
        order_id = str(uuid.uuid4())
        await db.orders.insert_one({"id": order_id, "user_id": current_user["id"], "items": [{k:v for k,v in i.items() if k != '_id'} for i in cart_items],
            "total_amount": 0, "payment_status": "free", "status": "completed", "created_at": datetime.now(timezone.utc)})
        await db.cart.delete_many({"user_id": current_user["id"]})
        return {"checkout_url": f"{origin_url}/dashboard?order=success&order_id={order_id}", "session_id": f"free_{order_id}", "is_free": True}

    webhook_url = f"{origin_url}/api/webhook/stripe-cart"
    stripe_checkout = StripeCheckout(api_key=STRIPE_API_KEY, webhook_url=webhook_url)
    cart_order_id = str(uuid.uuid4())
    success_url = f"{origin_url}/dashboard?order=success&session_id={{CHECKOUT_SESSION_ID}}"
    cancel_url = f"{origin_url}/cart?payment=cancelled"
    checkout_request = CheckoutSessionRequest(amount=float(total_amount), currency="usd", success_url=success_url, cancel_url=cancel_url,
        metadata={"cart_order_id": cart_order_id, "user_id": current_user["id"], "item_count": str(len(cart_items))})
    session = await stripe_checkout.create_checkout_session(checkout_request)
    await db.orders.insert_one({"id": cart_order_id, "user_id": current_user["id"], "session_id": session.session_id,
        "items": [{k:v for k,v in i.items() if k != '_id'} for i in cart_items], "total_amount": total_amount,
        "payment_status": "pending", "status": "pending", "created_at": datetime.now(timezone.utc)})
    return {"checkout_url": session.url, "session_id": session.session_id, "is_free": False}

@kalmori_router.post("/webhook/stripe-cart")
async def stripe_cart_webhook(request: Request):
    from emergentintegrations.payments.stripe.checkout import StripeCheckout
    body = await request.body()
    signature = request.headers.get("Stripe-Signature")
    stripe_checkout = StripeCheckout(api_key=STRIPE_API_KEY, webhook_url="")
    try:
        event = await stripe_checkout.handle_webhook(body, signature)
        if event.payment_status == "paid":
            order = await db.orders.find_one({"session_id": event.session_id})
            if order:
                await db.orders.update_one({"id": order["id"]}, {"$set": {"payment_status": "paid", "status": "completed", "paid_at": datetime.now(timezone.utc)}})
                await db.cart.delete_many({"user_id": order["user_id"]})
                await db.notifications.insert_one({"id": str(uuid.uuid4()), "user_id": order["user_id"], "type": "payment",
                    "message": f"Your order has been processed successfully. Total: ${order['total_amount']:.2f}",
                    "read": False, "created_at": datetime.now(timezone.utc).isoformat()})
        return {"received": True}
    except Exception as e:
        logger.error(f"Cart webhook error: {e}")
        raise HTTPException(status_code=400, detail=str(e))

# ==================== PROMOTION CHECKOUT ====================

@kalmori_router.post("/payments/create-promotion-checkout")
async def create_promotion_checkout(promo_req: PromotionCheckoutRequest, http_request: Request):
    from emergentintegrations.payments.stripe.checkout import StripeCheckout, CheckoutSessionRequest
    current_user = await _get_current_user_flexible(http_request)
    origin_url = str(http_request.base_url).rstrip('/')
    webhook_url = f"{origin_url}api/webhook/stripe"
    stripe_checkout = StripeCheckout(api_key=STRIPE_API_KEY, webhook_url=webhook_url)
    promotion_order_id = str(uuid.uuid4())
    success_url = f"{origin_url}/dashboard?promotion=success&order_id={promotion_order_id}"
    cancel_url = f"{origin_url}/promoting?payment=cancelled"
    checkout_request = CheckoutSessionRequest(amount=float(promo_req.amount), currency="usd", success_url=success_url, cancel_url=cancel_url,
        metadata={"order_id": promotion_order_id, "package_id": promo_req.package_id, "package_name": promo_req.package_name, "user_id": current_user["id"], "order_type": "promotion"})
    session = await stripe_checkout.create_checkout_session(checkout_request)
    await db.promotion_orders.insert_one({"id": promotion_order_id, "session_id": session.session_id, "user_id": current_user["id"],
        "user_email": current_user.get("email"), "package_id": promo_req.package_id, "package_name": promo_req.package_name,
        "amount": promo_req.amount, "currency": "usd", "payment_status": "pending", "order_status": "pending_payment", "created_at": datetime.now(timezone.utc)})
    return {"checkout_url": session.url, "session_id": session.session_id, "order_id": promotion_order_id}

# ==================== KALMORI WALLET (Extended) ====================

@kalmori_router.get("/kalmori-wallet", response_model=KalmoriWalletResponse)
async def get_kalmori_wallet(request: Request):
    current_user = await _get_current_user_flexible(request)
    wallet = await db.wallets.find_one({"user_id": current_user["id"]})
    if not wallet:
        wallet = {"user_id": current_user["id"], "available_balance": 0.0, "pending_balance": 0.0,
                  "total_earned": 0.0, "total_withdrawn": 0.0, "credits": 0, "created_at": datetime.now(timezone.utc)}
        await db.wallets.insert_one(wallet)
    user = await db.users.find_one({"id": current_user["id"]})
    user_credits = int(user.get("wallet_balance", 0)) if user else 0
    return KalmoriWalletResponse(
        available_balance=wallet.get("available_balance", wallet.get("balance", 0.0)),
        pending_balance=wallet.get("pending_balance", 0.0),
        total_earned=wallet.get("total_earned", wallet.get("total_earnings", 0.0)),
        total_withdrawn=wallet.get("total_withdrawn", 0.0),
        credits=wallet.get("credits", 0) + user_credits
    )

# ==================== CREDITS SYSTEM ====================

@kalmori_router.get("/credits")
async def get_credits(request: Request):
    current_user = await _get_current_user_flexible(request)
    wallet = await db.wallets.find_one({"user_id": current_user["id"]})
    user = await db.users.find_one({"id": current_user["id"]})
    wallet_credits = wallet.get("credits", 0) if wallet else 0
    user_credits = int(user.get("wallet_balance", 0)) if user else 0
    return {"credits": wallet_credits + user_credits, "wallet_credits": wallet_credits, "bonus_credits": user_credits}

# ==================== PAYMENT METHODS ====================

@kalmori_router.get("/payment-methods", response_model=List[PaymentMethodResponse])
async def get_payment_methods(request: Request):
    current_user = await _get_current_user_flexible(request)
    methods = await db.payment_methods.find({"user_id": current_user["id"]}).to_list(20)
    return [PaymentMethodResponse(
        id=m["id"], user_id=m["user_id"], method_type=m["method_type"],
        paypal_email=m.get("paypal_email"), bank_name=m.get("bank_name"),
        account_holder=m.get("account_holder"), account_number_last4=m.get("account_number_last4"),
        is_default=m.get("is_default", False), created_at=m["created_at"]
    ) for m in methods]

@kalmori_router.post("/payment-methods", response_model=PaymentMethodResponse)
async def add_payment_method(data: PaymentMethodCreate, request: Request):
    current_user = await _get_current_user_flexible(request)
    method_id = str(uuid.uuid4())
    existing_count = await db.payment_methods.count_documents({"user_id": current_user["id"]})
    is_default = existing_count == 0
    method = {"id": method_id, "user_id": current_user["id"], "method_type": data.method_type, "is_default": is_default, "created_at": datetime.now(timezone.utc)}
    if data.method_type == "paypal":
        if not data.paypal_email:
            raise HTTPException(status_code=400, detail="PayPal email is required")
        method["paypal_email"] = data.paypal_email
    elif data.method_type == "bank":
        if not all([data.bank_name, data.account_holder, data.account_number]):
            raise HTTPException(status_code=400, detail="Bank details are required")
        method["bank_name"] = data.bank_name
        method["account_holder"] = data.account_holder
        method["account_number"] = data.account_number
        method["account_number_last4"] = data.account_number[-4:]
        method["routing_number"] = data.routing_number
    await db.payment_methods.insert_one(method)
    return PaymentMethodResponse(id=method["id"], user_id=method["user_id"], method_type=method["method_type"],
        paypal_email=method.get("paypal_email"), bank_name=method.get("bank_name"),
        account_holder=method.get("account_holder"), account_number_last4=method.get("account_number_last4"),
        is_default=method["is_default"], created_at=method["created_at"])

@kalmori_router.delete("/payment-methods/{method_id}")
async def delete_payment_method(method_id: str, request: Request):
    current_user = await _get_current_user_flexible(request)
    method = await db.payment_methods.find_one({"id": method_id, "user_id": current_user["id"]})
    if not method:
        raise HTTPException(status_code=404, detail="Payment method not found")
    await db.payment_methods.delete_one({"id": method_id})
    if method.get("is_default"):
        another = await db.payment_methods.find_one({"user_id": current_user["id"]})
        if another:
            await db.payment_methods.update_one({"id": another["id"]}, {"$set": {"is_default": True}})
    return {"message": "Payment method deleted"}

# ==================== KALMORI WITHDRAWALS ====================

@kalmori_router.post("/kalmori-withdrawals", response_model=KalmoriWithdrawalResponse)
async def request_kalmori_withdrawal(data: KalmoriWithdrawalRequest, request: Request):
    current_user = await _get_current_user_flexible(request)
    payment_method = await db.payment_methods.find_one({"id": data.payment_method_id, "user_id": current_user["id"]})
    if not payment_method:
        raise HTTPException(status_code=404, detail="Payment method not found")
    wallet = await db.wallets.find_one({"user_id": current_user["id"]})
    avail = wallet.get("available_balance", wallet.get("balance", 0)) if wallet else 0
    if not wallet or avail < data.amount:
        raise HTTPException(status_code=400, detail="Insufficient balance")
    if data.amount < 10:
        raise HTTPException(status_code=400, detail="Minimum withdrawal is $10")
    withdrawal_id = str(uuid.uuid4())
    withdrawal = {"id": withdrawal_id, "user_id": current_user["id"], "amount": data.amount, "payment_method_id": data.payment_method_id,
                  "payment_method_type": payment_method["method_type"], "status": "pending", "created_at": datetime.now(timezone.utc), "processed_at": None}
    await db.withdrawals.insert_one(withdrawal)
    await db.wallets.update_one({"user_id": current_user["id"]}, {"$inc": {"available_balance": -data.amount, "pending_balance": data.amount}})
    return KalmoriWithdrawalResponse(**withdrawal)

@kalmori_router.get("/kalmori-withdrawals", response_model=List[KalmoriWithdrawalResponse])
async def get_kalmori_withdrawals(request: Request):
    current_user = await _get_current_user_flexible(request)
    withdrawals = await db.withdrawals.find({"user_id": current_user["id"]}).sort("created_at", -1).to_list(50)
    return [KalmoriWithdrawalResponse(**w) for w in withdrawals]

# ==================== ANALYTICS (Chart Data) ====================

@kalmori_router.get("/analytics/chart-data")
async def get_chart_data(days: int = 7, request: Request = None):
    current_user = await _get_current_user_flexible(request)
    user_id = current_user["id"]
    # Aggregate stream_events for this user over the given days
    cutoff = (datetime.now(timezone.utc) - timedelta(days=days)).isoformat()
    pipeline = [
        {"$match": {"artist_id": user_id, "timestamp": {"$gte": cutoff}}},
        {"$group": {
            "_id": {"$substr": ["$timestamp", 0, 10]},
            "plays": {"$sum": 1},
            "revenue": {"$sum": "$revenue"},
        }},
        {"$sort": {"_id": 1}},
    ]
    results = await db.stream_events.aggregate(pipeline).to_list(days + 1)
    date_map = {r["_id"]: {"plays": r["plays"], "revenue": round(r["revenue"], 2)} for r in results}
    data = []
    for i in range(days):
        date = datetime.now(timezone.utc) - timedelta(days=days - 1 - i)
        key = date.strftime("%Y-%m-%d")
        label = date.strftime("%b %d")
        entry = date_map.get(key, {"plays": 0, "revenue": 0.0})
        data.append({"date": label, "plays": entry["plays"], "revenue": entry["revenue"]})
    return data

@kalmori_router.get("/analytics/platform-breakdown")
async def get_platform_breakdown(request: Request):
    current_user = await _get_current_user_flexible(request)
    user_id = current_user["id"]
    pipeline = [
        {"$match": {"artist_id": user_id}},
        {"$group": {
            "_id": "$platform",
            "streams": {"$sum": 1},
            "revenue": {"$sum": "$revenue"},
        }},
        {"$sort": {"streams": -1}},
    ]
    results = await db.stream_events.aggregate(pipeline).to_list(20)
    platform_colors = {
        "Spotify": "#1DB954", "Apple Music": "#FC3C44", "YouTube Music": "#FF0000",
        "Amazon Music": "#FF9900", "Tidal": "#00FFFF", "TikTok": "#010101",
        "Deezer": "#A238FF", "SoundCloud": "#FF5500", "Pandora": "#005483", "Other": "#888888"
    }
    if not results:
        return [{"name": k, "streams": 0, "revenue": 0.0, "percentage": 0, "color": v} for k, v in list(platform_colors.items())[:6]]
    total = sum(r["streams"] for r in results)
    return [{
        "name": r["_id"] or "Other",
        "streams": r["streams"],
        "revenue": round(r["revenue"], 2),
        "percentage": round((r["streams"] / total) * 100, 1) if total > 0 else 0,
        "color": platform_colors.get(r["_id"], "#888888"),
    } for r in results]

@kalmori_router.get("/analytics/live-feed")
async def get_live_feed(request: Request, limit: int = 20):
    """Get recent streaming events as a live feed"""
    current_user = await _get_current_user_flexible(request)
    events = await db.stream_events.find(
        {"artist_id": current_user["id"]}, {"_id": 0}
    ).sort("timestamp", -1).limit(limit).to_list(limit)
    return {"events": events, "total": len(events)}

# ==================== THEME ====================

@kalmori_router.get("/theme")
async def get_theme(request: Request):
    current_user = await _get_current_user_flexible(request)
    theme = await db.themes.find_one({"user_id": current_user["id"]})
    if not theme:
        theme = {"user_id": current_user["id"], "theme": {"primary_color": "#E53935", "secondary_color": "#000000", "accent_color": "#FFD700", "background_style": "dark"}, "updated_at": datetime.now(timezone.utc)}
        await db.themes.insert_one(theme)
    theme.pop("_id", None)
    return theme

@kalmori_router.put("/theme")
async def update_theme(theme_data: ThemeSettings, request: Request):
    current_user = await _get_current_user_flexible(request)
    await db.themes.update_one({"user_id": current_user["id"]}, {"$set": {"theme": theme_data.model_dump(), "updated_at": datetime.now(timezone.utc)}}, upsert=True)
    return {"message": "Theme updated"}

# ==================== SOCIAL/FOLLOWER ====================

@kalmori_router.post("/artists/{artist_id}/follow")
async def follow_artist(artist_id: str, request: Request):
    current_user = await _get_current_user_flexible(request)
    if artist_id == current_user["id"]:
        raise HTTPException(status_code=400, detail="Cannot follow yourself")
    existing = await db.followers.find_one({"follower_id": current_user["id"], "following_id": artist_id})
    if existing:
        raise HTTPException(status_code=400, detail="Already following this artist")
    await db.followers.insert_one({"id": str(uuid.uuid4()), "follower_id": current_user["id"], "following_id": artist_id, "created_at": datetime.now(timezone.utc)})
    await db.notifications.insert_one({"id": str(uuid.uuid4()), "user_id": artist_id, "type": "follower",
        "message": f"{current_user.get('artist_name', current_user.get('name', 'Someone'))} started following you",
        "read": False, "created_at": datetime.now(timezone.utc).isoformat()})
    return {"message": "Successfully followed artist"}

@kalmori_router.delete("/artists/{artist_id}/follow")
async def unfollow_artist(artist_id: str, request: Request):
    current_user = await _get_current_user_flexible(request)
    result = await db.followers.delete_one({"follower_id": current_user["id"], "following_id": artist_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Not following this artist")
    return {"message": "Successfully unfollowed artist"}

@kalmori_router.get("/artists/{artist_id}/follower-count")
async def get_follower_count(artist_id: str):
    count = await db.followers.count_documents({"following_id": artist_id})
    return {"follower_count": count}

@kalmori_router.get("/artists/{artist_id}/is-following")
async def check_following(artist_id: str, request: Request):
    current_user = await _get_current_user_flexible(request)
    existing = await db.followers.find_one({"follower_id": current_user["id"], "following_id": artist_id})
    return {"is_following": existing is not None}

# ==================== PROMOTION ORDERS ====================

@kalmori_router.post("/orders/promotion-service")
async def create_promotion_order(order: PromotionOrderRequest):
    order_id = str(uuid.uuid4())
    order_data = {"id": order_id, "artist_name": order.artist_name, "email": order.email, "phone": order.phone,
        "song_title": order.song_title, "song_link": order.song_link, "services": order.services,
        "email_marketing": order.email_marketing, "social_media_marketing": order.social_media_marketing,
        "additional_notes": order.additional_notes, "status": "pending", "created_at": datetime.now(timezone.utc)}
    await db.promotion_orders.insert_one(order_data)
    services_str = ", ".join(order.services) if order.services else "None selected"
    email_html = f"""<html><body style="font-family:Arial;background:#1a1a1a;color:#fff;padding:40px;">
    <div style="max-width:600px;margin:0 auto;background:#000;border-radius:16px;overflow:hidden;">
    <div style="background:linear-gradient(90deg,#E040FB,#7C4DFF);padding:30px;text-align:center;">
    <h1 style="color:white;margin:0;">NEW PROMOTION ORDER</h1></div>
    <div style="padding:30px;">
    <p><strong>Artist:</strong> {order.artist_name}</p>
    <p><strong>Email:</strong> {order.email}</p>
    <p><strong>Song:</strong> {order.song_title}</p>
    <p><strong>Services:</strong> {services_str}</p>
    <p><strong>Notes:</strong> {order.additional_notes or 'None'}</p>
    </div></div></body></html>"""
    await send_email_notification(KALMORI_ADMIN_EMAIL, f"New Promotion Order: {order.song_title} by {order.artist_name}", email_html)
    return {"message": "Order submitted successfully", "order_id": order_id}

# ==================== INSTRUMENTAL REQUESTS ====================

@kalmori_router.post("/orders/instrumental-request")
async def create_instrumental_request(req: InstrumentalRequest):
    request_id = str(uuid.uuid4())
    request_data = {"id": request_id, "artist_name": req.artist_name, "email": req.email, "phone": req.phone,
        "genre": req.genre, "license_type": req.license_type, "tempo_range": req.tempo_range,
        "mood": req.mood, "reference_tracks": req.reference_tracks, "budget": req.budget,
        "additional_notes": req.additional_notes, "status": "pending", "created_at": datetime.now(timezone.utc)}
    await db.instrumental_requests.insert_one(request_data)
    email_html = f"""<html><body style="font-family:Arial;background:#1a1a1a;color:#fff;padding:40px;">
    <div style="max-width:600px;margin:0 auto;background:#000;border-radius:16px;overflow:hidden;">
    <div style="background:linear-gradient(90deg,#7C4DFF,#E040FB);padding:30px;text-align:center;">
    <h1 style="color:white;margin:0;">NEW INSTRUMENTAL REQUEST</h1></div>
    <div style="padding:30px;">
    <p><strong>Artist:</strong> {req.artist_name}</p>
    <p><strong>Email:</strong> {req.email}</p>
    <p><strong>Genre:</strong> {req.genre}</p>
    <p><strong>License:</strong> {req.license_type.upper()}</p>
    <p><strong>Budget:</strong> {req.budget or 'Not specified'}</p>
    <p><strong>Notes:</strong> {req.additional_notes or 'None'}</p>
    </div></div></body></html>"""
    await send_email_notification(KALMORI_ADMIN_EMAIL, f"New Instrumental Request: {req.genre} - {req.license_type.upper()}", email_html)
    return {"message": "Request submitted successfully", "request_id": request_id}

# ==================== TESTIMONIALS ====================

@kalmori_router.get("/testimonials", response_model=List[TestimonialResponse])
async def get_testimonials():
    testimonials = await db.testimonials.find({"approved": True}).sort("created_at", -1).to_list(20)
    return [TestimonialResponse(id=t["id"], name=t["name"], role=t["role"], quote=t["quote"],
        image_url=t.get("image_url"), rating=t.get("rating", 5), approved=t.get("approved", True),
        created_at=t["created_at"]) for t in testimonials]

@kalmori_router.post("/testimonials", response_model=TestimonialResponse)
async def create_testimonial(testimonial: TestimonialCreate, request: Request):
    current_user = await _get_current_user_flexible(request)
    testimonial_id = str(uuid.uuid4())
    testimonial_data = {"id": testimonial_id, "user_id": current_user["id"], "name": testimonial.name,
        "role": testimonial.role, "quote": testimonial.quote, "image_url": testimonial.image_url,
        "rating": testimonial.rating, "approved": False, "created_at": datetime.now(timezone.utc)}
    await db.testimonials.insert_one(testimonial_data)
    return TestimonialResponse(id=testimonial_id, name=testimonial.name, role=testimonial.role,
        quote=testimonial.quote, image_url=testimonial.image_url, rating=testimonial.rating,
        approved=False, created_at=testimonial_data["created_at"])

@kalmori_router.get("/admin/testimonials")
async def get_all_testimonials(admin_key: str = Query(...)):
    _verify_admin_key(admin_key)
    testimonials = await db.testimonials.find().sort("created_at", -1).to_list(100)
    return [{"id": t["id"], "user_id": t.get("user_id"), "name": t["name"], "role": t["role"],
             "quote": t["quote"], "image_url": t.get("image_url"), "rating": t.get("rating", 5),
             "approved": t.get("approved", False), "created_at": t["created_at"]} for t in testimonials]

@kalmori_router.put("/admin/testimonials/{testimonial_id}/approve")
async def approve_testimonial(testimonial_id: str, admin_key: str = Query(...)):
    _verify_admin_key(admin_key)
    testimonial = await db.testimonials.find_one({"id": testimonial_id})
    if not testimonial:
        raise HTTPException(status_code=404, detail="Testimonial not found")
    new_status = not testimonial.get("approved", False)
    await db.testimonials.update_one({"id": testimonial_id}, {"$set": {"approved": new_status}})
    return {"message": f"Testimonial {'approved' if new_status else 'disapproved'}", "approved": new_status}

@kalmori_router.delete("/admin/testimonials/{testimonial_id}")
async def delete_testimonial(testimonial_id: str, admin_key: str = Query(...)):
    _verify_admin_key(admin_key)
    result = await db.testimonials.delete_one({"id": testimonial_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Testimonial not found")
    return {"message": "Testimonial deleted"}

@kalmori_router.post("/admin/testimonials")
async def create_testimonial_admin(testimonial: TestimonialCreate, admin_key: str = Query(...)):
    _verify_admin_key(admin_key)
    testimonial_id = str(uuid.uuid4())
    testimonial_data = {"id": testimonial_id, "user_id": "admin", "name": testimonial.name,
        "role": testimonial.role, "quote": testimonial.quote, "image_url": testimonial.image_url,
        "rating": testimonial.rating, "approved": True, "created_at": datetime.now(timezone.utc)}
    await db.testimonials.insert_one(testimonial_data)
    return {"id": testimonial_id, "name": testimonial.name, "role": testimonial.role,
            "quote": testimonial.quote, "approved": True, "created_at": testimonial_data["created_at"]}

# ==================== RECAPTCHA PAGE ====================

@kalmori_router.get("/recaptcha-page", response_class=HTMLResponse)
async def get_recaptcha_page():
    site_key = RECAPTCHA_SITE_KEY or '6LflLJssAAAAAFaNfs6CNID-KgooQL8H0PETF1Aj'
    html_content = f'''<!DOCTYPE html>
<html><head><title>reCAPTCHA Verification</title>
<script src="https://www.google.com/recaptcha/api.js?render=explicit" async defer></script>
<style>body{{margin:0;display:flex;justify-content:center;align-items:center;min-height:100vh;background:#f5f5f5;font-family:Arial}}
.container{{text-align:center;padding:40px}}.success{{color:green;display:none}}.error{{color:red;display:none}}
.show{{display:block}}</style></head>
<body><div class="container">
<h2>Security Verification</h2><p>Complete the check below</p>
<div id="loading">Loading reCAPTCHA...</div>
<div id="g-recaptcha"></div>
<div id="success" class="success">Verified!</div>
<div id="error" class="error">Verification failed.</div>
</div>
<script>
var widgetId;
function onloadCallback(){{
try{{widgetId=grecaptcha.render('g-recaptcha',{{'sitekey':'{site_key}','callback':onSuccess,'expired-callback':onExpired,'error-callback':onError,'theme':'light','size':'normal'}});
document.getElementById('loading').style.display='none';}}catch(e){{document.getElementById('error').textContent='Failed to load';document.getElementById('error').classList.add('show');}}}}
function onSuccess(token){{document.getElementById('g-recaptcha').style.display='none';document.getElementById('success').classList.add('show');
if(window.ReactNativeWebView){{setTimeout(function(){{window.ReactNativeWebView.postMessage(JSON.stringify({{type:'success',token:token}}));}},800);}}}}
function onExpired(){{document.getElementById('error').textContent='Expired. Try again.';document.getElementById('error').classList.add('show');}}
function onError(){{document.getElementById('error').textContent='Error. Try again.';document.getElementById('error').classList.add('show');}}
</script>
<script src="https://www.google.com/recaptcha/api.js?onload=onloadCallback&render=explicit" async defer></script>
</body></html>'''
    return HTMLResponse(content=html_content)

# ==================== ROOT ENDPOINT ====================

@kalmori_router.get("/kalmori-info")
async def kalmori_root():
    return {"message": "Kalmori Music Distribution API", "version": "2.0.0"}

# ==================== STATS & GENRES ====================

@kalmori_router.get("/stats")
async def get_stats(request: Request):
    current_user = await _get_current_user_flexible(request)
    releases_count = await db.releases.count_documents({"artist_id": current_user["id"]})
    tracks_count = await db.tracks.count_documents({"artist_id": current_user["id"]})
    wallet = await db.wallets.find_one({"user_id": current_user["id"]})
    total_earnings = wallet.get("total_earned", wallet.get("total_earnings", 0.0)) if wallet else 0.0
    follower_count = await db.followers.count_documents({"following_id": current_user["id"]})
    return {
        "total_releases": releases_count,
        "total_tracks": tracks_count,
        "total_earnings": total_earnings,
        "total_streams": 0,
        "total_downloads": 0,
        "follower_count": follower_count
    }

@kalmori_router.get("/genres")
async def get_genres():
    return [
        "Hip-Hop/Rap", "R&B/Soul", "Pop", "Rock", "Electronic", "Jazz",
        "Classical", "Country", "Reggae", "Afrobeats", "Latin", "Dancehall",
        "Gospel", "Blues", "Folk", "Indie", "Metal", "Punk", "Alternative",
        "World", "Soundtrack", "Ambient", "Lo-fi", "Trap", "Drill", "Grime"
    ]

# ==================== TRANSACTIONS ====================

@kalmori_router.get("/transactions")
async def get_transactions(request: Request):
    current_user = await _get_current_user_flexible(request)
    transactions = await db.transactions.find(
        {"user_id": current_user["id"]}
    ).sort("created_at", -1).to_list(100)
    for t in transactions:
        t.pop("_id", None)
    return transactions

# ==================== SET DEFAULT PAYMENT METHOD ====================

@kalmori_router.put("/payment-methods/{method_id}/set-default")
async def set_default_payment_method(method_id: str, request: Request):
    current_user = await _get_current_user_flexible(request)
    method = await db.payment_methods.find_one({"id": method_id, "user_id": current_user["id"]})
    if not method:
        raise HTTPException(status_code=404, detail="Payment method not found")
    await db.payment_methods.update_many(
        {"user_id": current_user["id"]}, {"$set": {"is_default": False}}
    )
    await db.payment_methods.update_one(
        {"id": method_id}, {"$set": {"is_default": True}}
    )
    return {"message": "Default payment method updated"}

# ==================== STREAMING ANALYTICS ====================

@kalmori_router.get("/analytics/streaming/{user_id}")
async def get_streaming_analytics(user_id: str, request: Request):
    await _get_current_user_flexible(request)
    releases = await db.releases.find({"artist_id": user_id}).to_list(100)
    total_streams = sum(r.get("total_streams", 0) for r in releases)
    total_revenue = sum(r.get("total_revenue", 0.0) for r in releases)
    platforms = [
        {"name": "Spotify", "streams": 0, "revenue": 0.0, "color": "#1DB954"},
        {"name": "Apple Music", "streams": 0, "revenue": 0.0, "color": "#FC3C44"},
        {"name": "YouTube Music", "streams": 0, "revenue": 0.0, "color": "#FF0000"},
        {"name": "Amazon Music", "streams": 0, "revenue": 0.0, "color": "#FF9900"},
        {"name": "TikTok", "streams": 0, "revenue": 0.0, "color": "#010101"},
        {"name": "Tidal", "streams": 0, "revenue": 0.0, "color": "#00FFFF"}
    ]
    return {
        "total_streams": total_streams,
        "total_revenue": total_revenue,
        "platforms": platforms,
        "top_tracks": [],
        "monthly_data": []
    }

# ==================== FOLLOWERS & FOLLOWING LISTS ====================

@kalmori_router.get("/artists/{artist_id}/followers")
async def get_followers_list(artist_id: str):
    followers = await db.followers.find({"following_id": artist_id}).sort("created_at", -1).to_list(100)
    result = []
    for f in followers:
        user = await db.users.find_one({"id": f["follower_id"]})
        if user:
            result.append({
                "id": user["id"],
                "name": user.get("name", ""),
                "artist_name": user.get("artist_name", ""),
                "avatar_url": user.get("avatar_url"),
                "followed_at": f.get("created_at")
            })
    return result

@kalmori_router.get("/artists/{artist_id}/following")
async def get_following_list(artist_id: str):
    following = await db.followers.find({"follower_id": artist_id}).sort("created_at", -1).to_list(100)
    result = []
    for f in following:
        user = await db.users.find_one({"id": f["following_id"]})
        if user:
            result.append({
                "id": user["id"],
                "name": user.get("name", ""),
                "artist_name": user.get("artist_name", ""),
                "avatar_url": user.get("avatar_url"),
                "followed_at": f.get("created_at")
            })
    return result

# ==================== WITHDRAWALS (matching api.ts path) ====================

@kalmori_router.post("/withdrawals")
async def request_withdrawal_v2(request: Request):
    current_user = await _get_current_user_flexible(request)
    body = await request.json()
    amount = body.get("amount", 0)
    payment_method_id = body.get("payment_method_id")
    if not payment_method_id:
        raise HTTPException(status_code=400, detail="Payment method ID required")
    payment_method = await db.payment_methods.find_one({"id": payment_method_id, "user_id": current_user["id"]})
    if not payment_method:
        raise HTTPException(status_code=404, detail="Payment method not found")
    wallet = await db.wallets.find_one({"user_id": current_user["id"]})
    avail = wallet.get("available_balance", wallet.get("balance", 0)) if wallet else 0
    if not wallet or avail < amount:
        raise HTTPException(status_code=400, detail="Insufficient balance")
    if amount < 10:
        raise HTTPException(status_code=400, detail="Minimum withdrawal is $10")
    withdrawal_id = str(uuid.uuid4())
    withdrawal = {
        "id": withdrawal_id, "user_id": current_user["id"], "amount": amount,
        "payment_method_id": payment_method_id, "payment_method_type": payment_method["method_type"],
        "status": "pending", "created_at": datetime.now(timezone.utc), "processed_at": None
    }
    await db.withdrawals.insert_one(withdrawal)
    await db.wallets.update_one(
        {"user_id": current_user["id"]},
        {"$inc": {"available_balance": -amount, "pending_balance": amount}}
    )
    withdrawal.pop("_id", None)
    return withdrawal

@kalmori_router.get("/withdrawals")
async def get_withdrawals_v2(request: Request):
    current_user = await _get_current_user_flexible(request)
    withdrawals = await db.withdrawals.find({"user_id": current_user["id"]}).sort("created_at", -1).to_list(50)
    for w in withdrawals:
        w.pop("_id", None)
    return withdrawals
