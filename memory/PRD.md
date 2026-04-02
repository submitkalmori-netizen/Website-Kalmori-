# TuneDrop / Kalmori - Product Requirements Document

## Overview
TuneCore clone / high-volume digital content aggregator for musicians. React Web App matching "Kalmori" React Native design.

## Tech Stack
Frontend: React + Tailwind + Shadcn/UI | Backend: FastAPI + Motor + MongoDB | Auth: JWT (cookies+Bearer) + Google OAuth | Payments: Stripe + PayPal | Storage: Emergent Object Storage | AI: OpenAI GPT-4o (Emergent LLM Key) | Email: Resend

## Architecture
```
/app/backend/
├── server.py            # Core routes (auth, releases, tracks, admin, wallet, analytics, AI, payments)
├── kalmori_routes.py    # GitHub routes (CMS, Cart, Credits, Social, Testimonials, Theme, etc.)
├── routes/
│   ├── ai_routes.py     # AI features (metadata, descriptions, insights)
│   ├── email_routes.py  # Password reset, email notifications
│   ├── paypal_routes.py # PayPal payment integration
│   └── content_routes.py # Spotify Canvas + YouTube Content ID
└── tests/

/app/frontend/src/
├── App.js               # Routes, AuthContext, CartProvider
├── services/api.js      # Centralized API service (port of mobile api.ts)
├── context/CartContext.jsx
├── components/          # PublicLayout, DashboardLayout, AdminLayout, GlobalFooter
└── pages/               # 20+ pages
```

## ALL Completed Features

### Core Platform
- [x] JWT dual auth (cookies + Bearer token) + Google OAuth + inactivity timeout
- [x] Extended user profile (user_role, country, state, town, post_code)
- [x] Release CRUD with cover art upload, Track CRUD with audio upload
- [x] Distribution to 150+ stores (simulated), Distribution status tracking
- [x] Stripe payment processing + webhooks
- [x] Wallet system (balance, earnings, withdrawals)
- [x] Notifications system, Subscription plans
- [x] Admin dashboard (stats, submissions review, user management)
- [x] Ingestion/Review engine (pending → approved → distributed)
- [x] Split payments (track-level royalty splits)

### Kalmori GitHub Merge
- [x] CMS (slides, pricing, legal pages, full page editor, instrumentals)
- [x] Shopping Cart (CRUD + Stripe checkout)
- [x] Credits system, Payment Methods (PayPal/bank + set-default)
- [x] Social features (follow/unfollow, followers/following lists)
- [x] Testimonials (CRUD + admin approval), Theme settings
- [x] Promotion Orders, Instrumental Requests (with email notifications)
- [x] Stats, Genres, Transactions, Streaming Analytics endpoints
- [x] Video serving, reCAPTCHA, Public releases

### AI Features [Apr 2, 2026]
- [x] AI metadata suggestions (genre, mood, tags, BPM via GPT-4o)
- [x] AI-generated release descriptions
- [x] AI analytics insights (strategic recommendations)

### Advanced Analytics Dashboard [Apr 2, 2026]
- [x] Overview tab (streams/revenue charts, stats cards)
- [x] Audience Map tab (world map visualization, top countries)
- [x] TikTok UGC tab (sound usage tracking, trend direction)
- [x] Platforms tab (pie chart, platform details with revenue)
- [x] "Get AI Insights" button for strategic recommendations

### PayPal Integration [Apr 2, 2026]
- [x] PayPal config endpoint
- [x] Create/capture PayPal orders (sandbox simulation when no keys)
- [x] Order status tracking

### Email Notifications & Password Reset [Apr 2, 2026]
- [x] Forgot password (send reset link via Resend)
- [x] Reset password (verify token + update password)
- [x] Change password (authenticated)
- [x] Email templates for release approved/rejected, payment received
- [x] Reset Password page at /reset-password
- [x] "Forgot your password?" link on login page

### Spotify Canvas [Apr 2, 2026]
- [x] Canvas specs display (format, resolution, duration)
- [x] Create canvas per release
- [x] Upload MP4 video to Object Storage (max 20MB, 9:16)
- [x] Submit for Spotify review
- [x] Canvas management page with status tracking

### YouTube Content ID [Apr 2, 2026]
- [x] Register releases for Content ID
- [x] Asset ID generation
- [x] Policy management (monetize/track/block)
- [x] How-it-works explainer
- [x] Content ID management page

### Landing Page TuneCore Redesign [Apr 2, 2026]
- [x] TuneCore "Letter Layout" typography-forward design applied
- [x] KALMORI animated logo preserved in pink/purple
- [x] All original content sections preserved
- [x] "Need Beats or Instrumentals?" section restored with matching design

### Beat Audio Previews [Apr 2, 2026]
- [x] Beat catalog on Instrumentals/Leasing page
- [x] Play/pause toggle with animated waveform bars
- [x] Genre, BPM, key, mood, duration display
- [x] 6 demo beats (Trap, R&B, Hip-Hop, Afrobeats, Gospel, Pop)

### Backend Modularization [Apr 2, 2026]
- [x] New routes in /app/backend/routes/ (ai, email, paypal, content)
- [x] Centralized API service on frontend

### Frontend Pages (20+)
Landing, Login, Register, ResetPassword, Dashboard, Releases, ReleaseDetail, CreateRelease, Analytics, Wallet, Settings, SpotifyCanvas, ContentId, Admin, AdminSubmissions, AdminUsers, Pricing, Services, About, Contact, Promoting, Publishing, Stores, Instrumentals, Terms, Privacy

## MOCKED Integrations (require API keys to go live)
- PayPal: SANDBOX SIMULATION mode (set PAYPAL_CLIENT_ID + PAYPAL_CLIENT_SECRET in .env)
- Resend Email: SKIPPED when no API key (set RESEND_API_KEY in .env)

## Testing
- iteration_7: 100% (27/27) - Kalmori routes merge
- iteration_8: 100% (16/16) - Auth & service layer
- iteration_9: 100% (28/28) - api.ts port
- iteration_10: 93% backend + 100% frontend - All new features
- iteration_11: 100% (11/11) backend + 100% frontend - Back buttons, Object Storage, Stripe verified
