# Kalmori - TuneCore Clone PRD

## Original Problem Statement
Build a TuneCore clone / high-volume digital content aggregator and B2B e-commerce platform for musicians with Authentication, Subscriptions, Object Storage, AI Features, Release/Track uploads with a professional Wizard, Distribution to 37+ platforms, Beat/Instrumental catalog, and dark premium UI.

## Architecture
- **Frontend**: React + Tailwind CSS + Shadcn/UI + Recharts + Phosphor Icons
- **Backend**: FastAPI (modularized: server.py + core.py + /routes/)
- **Database**: MongoDB (15+ collections)
- **Storage**: Emergent Object Storage
- **Payments**: Stripe + PayPal
- **Auth**: JWT + Google Social Login + reCAPTCHA v2
- **AI**: OpenAI GPT-4o via Emergent LLM Key
- **Email**: Resend (configured with API key)
- **PDF**: reportlab (server-side generation)

## All Completed Features

### Core Platform
- JWT + Google Auth + reCAPTCHA v2, Admin Dashboard, Responsive dark premium UI

### Content & Distribution
- Professional 4-tab Release Wizard, UPC auto-generation, Spotify Canvas, Content ID

### Commerce & Payments
- Stripe subscriptions (4 tiers) + upgrade/downgrade, Beat catalog + Object Storage
- Beat Purchase (4 license tiers), Download delivery, My Purchases, Wallet

### Analytics & Insights
- DSP simulation engine (8 platforms, 14 countries), Streaming Feed, CSV import
- Share Your Stats social cards

### Fan Analytics Dashboard
- Listener Growth, Top Countries, Platform Engagement, Peak Hours
- Pre-save tracking, campaign analytics

### AI Release Strategy
- GPT-4o powered recommendations: optimal day/time, platform tactics, geographic targeting, timeline, tips

### Save & Compare Strategies
- Save with labels, view/delete, compare 2 side-by-side

### Strategy Export to PDF
- Branded Kalmori PDF one-pager via reportlab

### AI-Powered Smart Notifications
- 7-day trend analysis: country growth, platform shifts, peak hours
- GPT-4o generates categorized insights (growth/geographic/platform/timing/campaign)
- Lightning bolt badges in notification bell

### Automated Weekly Digest Emails (Apr 2026)
- Branded HTML email with: gradient header, 3-column stats (this week/last week/growth %), top markets table, top platforms table, AI insights with colored borders, release status badges, pre-save count, CTA button
- Preview modal on Fan Analytics page to see email before sending
- Send Now button for immediate delivery via Resend
- Digest history tracking (digest_log collection)
- "Weekly Performance Digest" toggle in Settings > Notifications
- Endpoints: POST /api/digest/send, POST /api/digest/preview, GET /api/digest/history

### Notifications & Communication
- Push Notifications (bell + dropdown + 30s polling)
- 9 notification preferences (email + push toggles + weekly digest)
- Resend email receipts

### Collaborations, Beat Search/Filter, Social Sharing, Pre-Save Campaigns
- All fully implemented

## All Pages & Routes
`/` `/login` `/register` `/instrumentals` `/dashboard` `/releases` `/releases/new` `/analytics` `/wallet` `/purchases` `/collaborations` `/presave-manager` `/fan-analytics` `/settings` `/presave/:id` `/spotify-canvas` `/content-id` `/admin/*`

## Remaining Backlog
- P1: Real Spotify OAuth with API credentials (placeholder ready)
- P2: Apple Music / YouTube Music API connections
- P2: Replace simulated DSP data with real API feeds
