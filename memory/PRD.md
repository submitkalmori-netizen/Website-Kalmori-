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

### Label Dashboard
- Dedicated dashboard for Label/Producer accounts at /label
- Manage artist roster: add by email, remove, view stats per artist
- Collective analytics: total streams, revenue, releases across all managed artists
- Platform & Country breakdowns, Top Performers ranking, Recent Releases table
- **Royalty Splits Management**: Custom royalty split per artist (default 70/30), editable via inline editor, summary cards (Total Revenue, Artist Payouts, Label Earnings), revenue split visualization bar, split validation (must sum to 100%)

### Admin Dashboard
- Overview: 6 stat cards, Platform Streams, Top Markets, Top Artists, Monthly trend
- User Detail Page: Full profile editor, stats, breakdowns, releases, goals
- Submissions review, Beat Manager

### Content
- 4-tab Release Wizard with professional track form: Title/Version, ISRC (auto-generate), Dolby Atmos ISRC, ISWC, Audio Language, Production, Publisher, Preview Start/End, Artists, Main Contributors, Contributors
- 150 streaming platforms with region-based filtering, search, Select All

### Commerce, Analytics & AI
- Stripe subs (4 tiers), Beat catalog, Wallet, Revenue Analytics, Release Leaderboard
- AI Release Strategy + PDF Export, AI Smart Notifications
- Fan Analytics, Goal Tracking & Milestones

### Growth
- Artist Profile Public Page (/artist/:slug), Pre-Save Campaigns, Collaborations

## All Pages & Routes
`/` `/login` `/register` `/select-role` `/label` `/instrumentals` `/dashboard` `/releases` `/releases/new` `/analytics` `/wallet` `/purchases` `/collaborations` `/presave-manager` `/fan-analytics` `/revenue` `/leaderboard` `/goals` `/settings` `/presave/:id` `/artist/:slug` `/spotify-canvas` `/content-id` `/admin` `/admin/submissions` `/admin/users` `/admin/users/:userId` `/admin/beats`

## Remaining Backlog
- P1: Real Spotify OAuth with API credentials
- P2: Apple Music / YouTube Music API connections
- P2: Replace simulated DSP data with real API feeds
