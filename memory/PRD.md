# Kalmori - TuneCore Clone PRD

## Original Problem Statement
Build a TuneCore clone / high-volume digital content aggregator and B2B e-commerce platform for musicians with Authentication, Subscriptions, Object Storage, AI Features, Release/Track uploads with a professional Wizard, Distribution to 150+ platforms, Beat/Instrumental catalog, and dark premium UI.

## Architecture
- **Frontend**: React + Tailwind CSS + Shadcn/UI + Recharts + Phosphor Icons + Framer Motion
- **Backend**: FastAPI (modularized: server.py + core.py + /routes/)
- **Database**: MongoDB (15+ collections including label_artists)
- **Storage**: Emergent Object Storage | **Payments**: Stripe + PayPal
- **Auth**: JWT + Google Social Login + reCAPTCHA v2
- **AI**: OpenAI GPT-4o via Emergent LLM Key | **Email**: Resend | **PDF**: reportlab

## All Completed Features

### Core
- Auth (JWT + Google OAuth + reCAPTCHA), Responsive dark premium UI
- Multi-step sign-up (CD Baby style): Step 1 (Email/Password/Terms/reCAPTCHA), Step 2 (Name/Country/Address/Phone)
- Role Selection page (/select-role): Artist vs Label/Producer with stacked gold buttons
- Password requirements: 12+ chars, 1 number, 1 capital, no spaces
- Welcome email on sign-up (role-specific: Artist vs Label/Producer)
- Email template system with reusable email_base wrapper

### Label Dashboard (Apr 2026)
- Dedicated dashboard for Label/Producer accounts at /label
- Manage artist roster: add by email, remove, view stats per artist
- Collective analytics: total streams, revenue, releases across all managed artists
- Platform & Country breakdowns for entire roster
- Top Performers ranking with streams + revenue per artist
- Recent Releases table across all roster artists
- 5 stat cards: Artists, Total Streams, Revenue, Releases, This Week
- "Label Dashboard" nav item only visible for label_producer users

### Admin Dashboard
- Overview: 6 stat cards, Platform Streams, Top Markets, Top Artists, Monthly trend
- User Detail Page (/admin/users/:userId): Full profile editor, stats, breakdowns, releases, goals
- Submissions review, Beat Manager

### Content
- 4-tab Release Wizard with professional track form: Title/Title Version, ISRC (+ auto-generate), Dolby Atmos ISRC, ISWC, Audio Language, Production, Publisher, Preview Start/End Time, Artists (role+name), Main Contributors (Composer/Lyricist), Contributors (add/remove)
- 150 streaming platforms with region-based filtering, search, Select All

### Commerce
- Stripe subs (4 tiers) + upgrade/downgrade, Beat catalog, My Purchases, Wallet

### Analytics & AI
- DSP simulation, Fan Analytics, Revenue Analytics, Release Leaderboard, Goal Tracking & Milestones
- AI Release Strategy + Save/Compare + PDF Export, AI Smart Notifications

### Growth
- Artist Profile Public Page (/artist/:slug), Pre-Save Campaigns, Collaborations

### Landing Page
- Marketing-focused with 9 feature showcase cards + stats row

## All Pages & Routes
`/` `/login` `/register` `/select-role` `/label` `/instrumentals` `/dashboard` `/releases` `/releases/new` `/analytics` `/wallet` `/purchases` `/collaborations` `/presave-manager` `/fan-analytics` `/revenue` `/leaderboard` `/goals` `/settings` `/presave/:id` `/artist/:slug` `/spotify-canvas` `/content-id` `/admin` `/admin/submissions` `/admin/users` `/admin/users/:userId` `/admin/beats`

## Remaining Backlog
- P1: Real Spotify OAuth with API credentials
- P2: Apple Music / YouTube Music API connections
- P2: Replace simulated DSP data with real API feeds
