# TuneDrop (Kalmori) - Music Distribution Platform PRD

## Original Problem Statement
Build a TuneCore-like music distribution platform that manages the lifecycle of music from upload to distribution across hundreds of digital service providers (DSPs). The frontend must match the user's existing "Kalmori" React Native Expo app design but built as a React Web Application.

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

## Core Requirements
- User authentication (JWT + Google OAuth)
- Artist profile management
- Release creation with UPC generation
- Track management with ISRC codes
- Audio/Video file uploads (Object Storage)
- Cover art uploads
- Distribution to 150+ DSPs (simulated)
- Ingestion & Review Engine (admin approval flow)
- Split Payments Engine (collaborator management)
- Admin Panel (platform stats, submission review, user management)
- Royalty tracking & analytics
- Subscription plans (Free/Rise/Pro)
- Wallet & withdrawals
- AI-powered descriptions & metadata suggestions

## What's Been Implemented

### Phase 1 - Foundation (April 2026)
- [x] Landing page with Kalmori design (hero, animations, pricing)
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
- [x] AI analytics insights
- [x] Subscription plans system

### Phase 2 - Admin & Ingestion (April 2026)
- [x] **Ingestion & Review Engine** - Distribution submit creates "pending_review" status. Admin approves/rejects before going live.
- [x] **Split Payments Engine** - Add collaborators per track with percentage splits (validated to <= 100%)
- [x] **Admin Dashboard** - Platform stats (users, releases, submissions, revenue, plans)
- [x] **Admin Submissions Review** - Paginated queue with filters, review modal (approve/reject with notes)
- [x] **Admin User Management** - Search, edit role/plan/status, suspend users
- [x] **Admin Route Protection** - AdminRoute component, 403 for non-admin API access
- [x] **Admin Panel sidebar link** - Visible only for admin role users
- [x] **Audit logging** - Admin actions recorded in admin_actions collection

## P0/P1/P2 Features Remaining

### P0 (Critical)
- [ ] PayPal payment integration
- [ ] Full ingestion flow E2E test (with audio + cover art uploaded)

### P1 (Important)
- [ ] Advanced Analytics Dashboard (Audience Map, TikTok UGC trends)
- [ ] Email notifications for review results
- [ ] Password reset flow
- [ ] YouTube Content ID integration
- [ ] Spotify Canvas support

### P2 (Nice to have)
- [ ] Video file uploads
- [ ] Collaborative releases
- [ ] Mobile-responsive admin panel improvements
- [ ] Backend modularization (split server.py into route files)

## Database Collections
- `users` - User accounts with role, plan, status
- `releases` - Music releases with UPC, status (draft/pending_review/distributed/rejected)
- `tracks` - Individual tracks with ISRC, audio URLs
- `distributions` - Store distribution records per release
- `submissions` - Ingestion queue for admin review
- `splits` - Collaborator split agreements per track
- `royalties` - Earnings data
- `wallets` - User balances
- `withdrawals` - Withdrawal requests
- `notifications` - User/admin notifications
- `admin_actions` - Audit log of admin decisions
- `payment_transactions` - Stripe payment records
- `artist_profiles` - Extended artist profile data

## Key API Endpoints
- Auth: `/api/auth/login`, `/api/auth/register`, `/api/auth/session` (Google)
- Releases: `/api/releases`, `/api/releases/{id}`, `/api/releases/{id}/cover`
- Tracks: `/api/tracks`, `/api/tracks/{id}/audio`, `/api/tracks/{id}/stream`
- Distribution: `/api/distributions/submit/{id}`, `/api/distributions/{id}`
- Admin: `/api/admin/dashboard`, `/api/admin/submissions`, `/api/admin/users`
- Splits: `/api/splits`, `/api/splits/{track_id}`
- Payments: `/api/payments/checkout`, `/api/payments/status/{id}`
- AI: `/api/ai/metadata-suggestions`, `/api/ai/generate-description`, `/api/ai/analytics-insights`
