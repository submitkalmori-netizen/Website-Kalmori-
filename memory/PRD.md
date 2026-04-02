# Kalmori - TuneCore Clone PRD

## Original Problem Statement
Build a TuneCore clone / high-volume digital content aggregator and B2B e-commerce platform for musicians. Core requirements include Authentication, Subscriptions (Stripe/PayPal), Object Storage for high-res files, AI Features, Artist/User management, Release/Track uploads (with a Wizard), Distribution store management, and a Beat/Instrumental catalog for leasing and purchasing. The frontend must match the user's existing "Kalmori" React Native Expo app UI with a dark, premium aesthetic.

## Architecture
- **Frontend**: React + Tailwind CSS + Shadcn/UI + Recharts
- **Backend**: FastAPI (modularized: server.py + core.py + /routes/)
- **Database**: MongoDB
- **Storage**: Emergent Object Storage
- **Payments**: Stripe + PayPal
- **Auth**: JWT (Cookie + Bearer) + Google Social Login + reCAPTCHA v2
- **AI**: OpenAI via Emergent LLM Key
- **Email**: Resend (configured with real API key)

## Completed Features

### Phase 1 - Core Platform
- [x] JWT + Google Auth with reCAPTCHA v2 registration
- [x] User/Artist management (Legal Name, Stage Name, Country)
- [x] Admin Dashboard with role-based access
- [x] Dark premium UI matching Kalmori mobile app
- [x] Responsive design (mobile + desktop)

### Phase 2 - Content & Distribution
- [x] 5-step Release Wizard (metadata, tracks, stores, pricing, review)
- [x] Track upload with Object Storage
- [x] Distribution store management
- [x] Spotify Canvas & Content ID pages

### Phase 3 - Commerce & Payments
- [x] Subscription plans (Free/Rising Star/Pro/Label) with Stripe
- [x] Beat/Instrumental catalog with CRUD + Object Storage
- [x] Admin Beat Manager
- [x] Beat Purchase Checkout (Stripe) with 4 license tiers
- [x] Beat download delivery after purchase
- [x] "My Purchases" page with download buttons

### Phase 4 - Analytics & Insights
- [x] Real-time Streaming Data Ingestion (simulated from 8 DSPs, 14 countries)
- [x] Analytics Overview with Streams + Revenue charts
- [x] Platform Breakdown (8 platforms)
- [x] Live Streaming Feed
- [x] AI-powered analytics insights
- [x] DSP Data CSV Import
- [x] Share Your Stats social cards with milestones

### Phase 5 - Notifications & Communication
- [x] Push Notifications (bell with unread count, dropdown panel)
- [x] Notification preferences (8 toggles: email + push per category)
- [x] Email receipts via Resend (configured with real API key)
- [x] Beat purchase + subscription receipt email templates

### Phase 6 - Collaborations
- [x] Collaborator invite system (by email)
- [x] Accept/Decline invitations
- [x] Royalty split configuration per release (max 100%)
- [x] Collaborator management dashboard
- [x] Email notifications for invitations
- [x] Release collaborator view

### Phase 7 - Backend Architecture
- [x] Backend modularization (server.py + core.py + /routes/)
- [x] Route modules: ai, email, paypal, content, beats, collab

## Key DB Collections
- `users`, `releases`, `tracks`, `beats`, `beat_purchases`
- `stream_events`, `notifications`, `notification_preferences`
- `collaborations`, `receipts`, `wallets`, `subscriptions`

## Key API Endpoints
- Auth: `/api/auth/register`, `/api/auth/login`
- Beats: `/api/beats`, `/api/beats/{id}/stream`
- Purchases: `/api/purchases`, `/api/purchases/{id}/download`
- Payments: `/api/payments/create-subscription-checkout`, `/api/payments/create-beat-checkout`
- Analytics: `/api/analytics/overview`, `/api/analytics/chart-data`, `/api/analytics/platform-breakdown`, `/api/analytics/live-feed`, `/api/analytics/import`
- Stats: `/api/stats/milestones`, `/api/stats/share-card`
- Notifications: `/api/notifications`, `/api/notifications/unread-count`, `/api/notifications/read-all`
- Settings: `/api/settings/notification-preferences`
- Collaborations: `/api/collaborations`, `/api/collaborations/invite`, `/api/collaborations/{id}/accept`, `/api/collaborations/{id}/decline`, `/api/collaborations/{id}/split`, `/api/collaborations/release/{id}`
- Releases: `/api/releases`, Release Wizard

## 3rd Party Integrations
- Stripe (Payments) — System Environment Key
- PayPal (Payments) — User API Key
- Google reCAPTCHA v2 — User-provided keys
- OpenAI (AI Features) — Emergent LLM Key
- Emergent Object Storage — Emergent Integrations
- Emergent Google Auth — Emergent Integrations
- Resend (Email) — CONFIGURED with real API key

## Remaining Backlog
- [ ] Real DSP API integration (replace simulated data with actual Spotify/Apple feeds)
- [ ] Advanced search/filter on beat catalog
- [ ] Social sharing deep links
