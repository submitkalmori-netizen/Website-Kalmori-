# TuneDrop (Kalmori) - Music Distribution Platform PRD

## Original Problem Statement
Build a TuneCore-like music distribution platform that manages the lifecycle of music from upload to distribution across hundreds of digital service providers (DSPs). The frontend must match the user's existing "Kalmori" React Native Expo app design but built as a React Web Application for custom domain support.

## Architecture
- **Frontend**: React 19 + Tailwind CSS + Shadcn UI + Phosphor Icons
- **Backend**: FastAPI (Python)
- **Database**: MongoDB
- **Storage**: Emergent Object Storage
- **Payments**: Stripe integration
- **Auth**: JWT + Google OAuth (Emergent Managed)
- **AI**: GPT-5.2 via Emergent LLM Key

## User Personas
1. **Independent Artist** - Uploads and distributes music
2. **Admin** - Manages platform, reviews submissions, manages users
3. **Visitor** - Browses public pages, views pricing, requests beats

## What's Been Implemented

### Phase 1 - Foundation
- [x] Landing page with Kalmori design (hero, animations, typewriter)
- [x] JWT authentication (register/login/logout)
- [x] Google OAuth integration (Emergent Managed)
- [x] Dashboard with stats and Recharts charts
- [x] Release management with UPC codes
- [x] Track management with ISRC codes
- [x] Audio file upload & streaming (Object Storage)
- [x] Cover art upload
- [x] Distribution store selection (10 DSPs)
- [x] Stripe payment checkout
- [x] Analytics with Recharts (simulated data)
- [x] Wallet & withdrawal system
- [x] Settings & profile editing
- [x] AI-powered description generation (GPT-5.2)
- [x] Subscription plans system

### Phase 2 - Admin & Ingestion
- [x] Ingestion & Review Engine (pending_review -> approved/rejected)
- [x] Split Payments Engine (collaborator % splits per track)
- [x] Admin Dashboard (platform stats, revenue, plan distribution)
- [x] Admin Submissions Review (paginated queue, approve/reject modal)
- [x] Admin User Management (search, edit role/plan/status)
- [x] Admin Route Protection + Audit logging
- [x] Admin Notification Bell (real-time pending count)

### Phase 3 - Full GitHub Port (All Public Pages)
- [x] Shared PublicLayout with slide-out menu (exact GitHub design)
- [x] Shared GlobalFooter component
- [x] Pricing page (Free/Unlimited Single/Album plans)
- [x] Our Services page (Distribution, Analytics, Promotion, Publishing)
- [x] About Us page (Mission, Values, CTA)
- [x] Contact/Support page (Contact info + form)
- [x] Promoting page (Channels + 3 promo packages)
- [x] Publishing page (Services, stats, sign-up popup)
- [x] Stores page (12 DSPs: Spotify, Apple Music, Deezer, YouTube, Amazon, TikTok, Tidal, Pandora, SoundCloud, Instagram, Audiomack, Boomplay)
- [x] Leasing/Instrumentals page (4 license tiers + custom beat request form)
- [x] Terms & Conditions page (12 sections)
- [x] Privacy Policy page (11 sections)
- [x] All pages share KALMORI header, animated color cycling, scroll-to-top

## P0/P1/P2 Features Remaining

### P0 (Critical)
- [ ] PayPal payment integration
- [ ] Full E2E ingestion test (artist uploads -> admin reviews)

### P1 (Important)
- [ ] Advanced Analytics Dashboard (Audience Map, TikTok UGC trends)
- [ ] Email notifications for review results
- [ ] Password reset flow

### P2 (Nice to have)
- [ ] Video file uploads
- [ ] YouTube Content ID / Spotify Canvas
- [ ] Backend modularization (split server.py)

## Database Collections
users, releases, tracks, distributions, submissions, splits, royalties, wallets, withdrawals, notifications, admin_actions, payment_transactions, artist_profiles

## Key API Endpoints
- Auth: /api/auth/login, /api/auth/register, /api/auth/session
- Releases: /api/releases, /api/releases/{id}, /api/releases/{id}/cover
- Tracks: /api/tracks, /api/tracks/{id}/audio, /api/tracks/{id}/stream
- Distribution: /api/distributions/submit/{id}
- Admin: /api/admin/dashboard, /api/admin/submissions, /api/admin/users
- Splits: /api/splits, /api/splits/{track_id}
- Payments: /api/payments/checkout
- AI: /api/ai/metadata-suggestions, /api/ai/generate-description

## Frontend Routes
/, /login, /register, /dashboard, /releases, /releases/new, /releases/:id, /analytics, /wallet, /settings, /admin, /admin/submissions, /admin/users, /pricing, /services, /about, /contact, /promoting, /publishing, /stores, /leasing, /instrumentals, /terms, /privacy
