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
- **Email**: Resend
- **PDF**: reportlab

## All Completed Features

### Core Platform
- JWT + Google Auth + reCAPTCHA v2, Admin Dashboard, Responsive dark premium UI

### Content & Distribution
- Professional 4-tab Release Wizard, UPC auto-generation, Spotify Canvas, Content ID

### Commerce & Payments
- Stripe subscriptions (4 tiers) + upgrade/downgrade, Beat catalog + Object Storage
- Beat Purchase (4 license tiers), Download delivery, My Purchases, Wallet

### Analytics & Insights
- DSP simulation engine (8 platforms, 14 countries), Streaming Feed, CSV import, Share Your Stats

### Fan Analytics Dashboard
- Listener Growth, Top Countries, Platform Engagement, Peak Hours, Pre-save tracking

### AI Release Strategy + Save & Compare + PDF Export
- GPT-4o powered recommendations, save/compare side-by-side, branded PDF one-pager

### AI-Powered Smart Notifications
- 7-day trend analysis, categorized insights, lightning bolt badges in notification bell

### Automated Weekly Digest Emails
- Branded HTML email with stats, AI insights, releases. Preview modal, Send Now, Settings toggle

### Revenue Analytics & Royalty Calculator
- 4 summary cards, monthly trend chart, platform breakdown table, collaborator splits, what-if calculator, rate guide

### Release Performance Leaderboard (Apr 2026)
- Top 3 podium (gold/silver/bronze cards with sparkline mini-charts)
- Full ranked release list with rank number, title, genre, top platform
- 14-day sparkline SVG charts per release (green for growth, red for decline)
- Hot streak badges (3+ consecutive days of growth)
- Rising badges (momentum > 50%)
- Sort by: Total Streams, This Week, Growth Rate, Revenue, Momentum
- Filter by: All Releases, Active Only, No Streams
- Stats columns: This Week, Total, Growth%, Revenue
- Podium auto-hides when sort/filter changes from default

### Notifications & Communication
- 9 notification preferences (email + push + weekly digest)

### Collaborations, Beat Search/Filter, Social Sharing, Pre-Save Campaigns
- All fully implemented

## All Pages & Routes
`/` `/login` `/register` `/instrumentals` `/dashboard` `/releases` `/releases/new` `/analytics` `/wallet` `/purchases` `/collaborations` `/presave-manager` `/fan-analytics` `/revenue` `/leaderboard` `/settings` `/presave/:id` `/spotify-canvas` `/content-id` `/admin/*`

## Remaining Backlog
- P1: Real Spotify OAuth with API credentials (placeholder ready)
- P2: Apple Music / YouTube Music API connections
- P2: Replace simulated DSP data with real API feeds
