# Kalmori - TuneCore Clone PRD

## Original Problem Statement
Build a TuneCore clone / high-volume digital content aggregator and B2B e-commerce platform for musicians with Authentication, Subscriptions, Object Storage, AI Features, Release/Track uploads with a professional Wizard, Distribution to 37+ platforms, Beat/Instrumental catalog, and dark premium UI.

## Architecture
- **Frontend**: React + Tailwind CSS + Shadcn/UI + Recharts + Phosphor Icons
- **Backend**: FastAPI (modularized: server.py + core.py + /routes/)
- **Database**: MongoDB (15+ collections including saved_strategies)
- **Storage**: Emergent Object Storage
- **Payments**: Stripe + PayPal
- **Auth**: JWT + Google Social Login + reCAPTCHA v2
- **AI**: OpenAI via Emergent LLM Key
- **Email**: Resend (configured)
- **PDF**: reportlab (server-side PDF generation)

## All Completed Features

### Core Platform
- JWT + Google Auth + reCAPTCHA v2, Admin Dashboard, Responsive dark premium UI

### Content & Distribution
- Professional 4-tab Release Wizard (General Info, Tracks & Assets, Territory with 37 platforms, Summary with validation)
- UPC auto-generation, Copyright/Production lines, Booklet uploads, Volume management, Compilation support
- Spotify Canvas, Content ID pages

### Commerce & Payments
- Stripe subscriptions (4 tiers) + upgrade/downgrade, Beat catalog + Object Storage
- Beat Purchase (4 license tiers), Download delivery, My Purchases page, Wallet system

### Analytics & Insights
- Realistic DSP simulation engine (8 platforms, 14 countries, peak hours, growth curves, weekend boosts)
- Live Streaming Feed, Platform Breakdown, AI-powered insights, CSV import
- Share Your Stats social cards with milestone tracking

### Fan Analytics Dashboard
- Listener Growth chart (30 days), Top Listener Countries with flag emojis
- Platform Engagement donut chart, Peak Listening Hours bar chart
- Pre-save subscriber tracking, campaign analytics

### AI Release Strategy (Apr 2026)
- AI-powered release strategy recommendations using OpenAI GPT-4o
- Analyzes fan analytics: geography, peak hours, platform engagement, pre-save subs
- Returns: optimal release day/time, platform tactics, geographic targeting, pre-release timeline, promotion tips
- UI section at bottom of Fan Analytics page with input fields and results display
- Fallback strategy when AI unavailable

### Save & Compare Strategies (Apr 2026)
- Save generated strategies with custom labels to MongoDB
- View all saved strategies in a scrollable panel
- Delete saved strategies with confirmation toast
- Compare mode: select any 2 strategies for side-by-side comparison
- Compare view: Best Day, Best Time, Streams Analyzed, Top Platform, Top Country, Est. First Week, Platform Priorities, Timeline Steps

### Strategy Export to PDF (Apr 2026)
- Server-side PDF generation using reportlab with Kalmori branding
- Branded one-pager: header, artist info, optimal release window, platform strategy, geographic targeting, pre-release timeline, promotion tips, confidence note, footer
- Export from current strategy results or from any saved strategy card
- PDF filename: Kalmori_Strategy_{label}_{date}.pdf
- Direct browser download via blob URL

### Notifications & Communication
- Push Notifications (bell + dropdown + 30s polling)
- 8 notification preferences (email + push toggles)
- Resend email receipts (beat + subscription + collaboration templates)

### Collaborations
- Invite system, Accept/Decline, Royalty split management, Email + in-app notifications

### Beat Catalog Search/Filter
- Search by name/genre/mood/tags, Genre/Mood/Key/BPM range/Price filters
- Sort: newest, price, BPM. Share buttons on beat cards

### Social Sharing
- OG Meta Tags (Open Graph + Twitter Cards) in index.html
- Public share endpoints for beats, releases, artists

### Pre-Save Campaigns
- Campaign manager, Public landing pages with countdown timer
- Spotify/Apple Music/YouTube links, Email subscriptions, Subscriber tracking

### Integrations
- Spotify for Artists connection placeholder (OAuth-ready)
- Apple Music, YouTube Music — Coming Soon badges
- Settings > Integrations tab

### Backend Architecture
- Modularized: server.py + core.py + /routes/ (ai, email, paypal, content, beats, collab)

## All Pages & Routes
`/` `/login` `/register` `/instrumentals` `/dashboard` `/releases` `/releases/new` `/analytics` `/wallet` `/purchases` `/collaborations` `/presave-manager` `/fan-analytics` `/settings` `/presave/:id` `/spotify-canvas` `/content-id` `/admin/*`

## Remaining Backlog
- P1: Real Spotify OAuth with API credentials (placeholder ready)
- P2: Apple Music / YouTube Music API connections
- P2: Replace simulated DSP data with real API feeds once user provides DSP developer credentials
