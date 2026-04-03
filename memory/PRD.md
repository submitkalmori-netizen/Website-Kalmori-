# Kalmori - TuneCore Clone PRD

## Original Problem Statement
Build a TuneCore clone / high-volume digital content aggregator and B2B e-commerce platform for musicians with Authentication, Subscriptions, Object Storage, AI Features, Release/Track uploads with a professional Wizard, Distribution to 150+ platforms, Beat/Instrumental catalog, and dark premium UI.

## Architecture
- **Frontend**: React + Tailwind CSS + Shadcn/UI + Recharts + Phosphor Icons + Framer Motion
- **Backend**: FastAPI (modularized: server.py + core.py + /routes/)
- **Database**: MongoDB (15+ collections incl. import_schedules)
- **Storage**: Emergent Object Storage | **Payments**: Stripe + PayPal
- **Auth**: JWT + Google Social Login + reCAPTCHA v2
- **AI**: OpenAI GPT-4o via Emergent LLM Key | **Email**: Resend | **PDF**: reportlab
- **File Parsing**: openpyxl (XLSX), pdfplumber (PDF), csv (CSV)

## Route Files
- `server.py` (~2,400 lines) - Auth, Artist, Release, Track, Distribution, Payments, Wallet, Analytics, Revenue Export (CSV/PDF), Goals, Notifications, Fan Analytics, Spotify, Artist Public Profile
- `routes/admin_routes.py` - Admin Dashboard, Users, Submissions, Analytics, Royalty Import (CSV/XLSX/PDF) with auto-notifications, Distributor Templates, Reconciliation (with bulk actions), Import Schedules
- `routes/label_routes.py` - Label Dashboard, Roster, Royalty Splits, Payout Export (Kalmori-branded)
- `routes/ai_routes.py` - AI Strategy, Smart Insights, PDF Export
- `routes/email_routes.py` - Email templates, Digest
- `routes/beats_routes.py` - Beat catalog CRUD
- `routes/collab_routes.py` - Collaborations
- `routes/paypal_routes.py` - PayPal payments
- `routes/content_routes.py` - Content ID, Spotify Canvas

## All Completed Features

### Core
- Auth (JWT + Google OAuth + reCAPTCHA), Responsive dark premium UI
- Multi-step sign-up (CD Baby style), Role Selection (/select-role), Welcome emails
- Both Artist AND Producer roles have identical access to all client-facing features

### Label Dashboard
- Dedicated dashboard at /label with 3 tabs: Overview, Royalty Splits, Payouts
- Roster management, Collective analytics, Platform & Country breakdowns
- Royalty Splits per artist, Kalmori-branded Payout Reports (CSV & PDF)

### Admin Dashboard
- Overview stats, Platform Analytics, User Detail Page, Submissions review, Beat Manager
- **Multi-Format Royalty Import** (Admin-only): CSV, Excel (.xlsx), PDF
- **Distributor Template Manager**: CRUD for column mappings
- **Smart Royalty Reconciliation**: Duplicate detection, discrepancy flagging
- **Bulk Reconciliation Actions**: One-click resolve duplicates (keep latest/highest/delete all), bulk assign unmatched entries to artist/producer with auto-notifications
- **Auto-Notification on Import**: All matched users get in-app + email notifications
- **Import Schedules**: Weekly/monthly recurring import reminders with template + artist assignment, overdue detection, pause/resume

### White-Label Branding
- All client-facing exports/emails say "Kalmori Distribution" — never the real distributor

### Content & Commerce
- 4-tab Release Wizard, 150 streaming platforms, Stripe subs, Beat catalog, Wallet

### Analytics & AI
- Revenue Analytics with Kalmori Distribution integration + Revenue Export (CSV/PDF)
- Release Leaderboard, AI Release Strategy + PDF Export, AI Smart Notifications
- Fan Analytics, Goal Tracking & Milestones

### Growth
- Artist Profile Public Page, Pre-Save Campaigns, Collaborations

## All Pages & Routes
`/` `/login` `/register` `/select-role` `/label` `/instrumentals` `/dashboard` `/releases` `/releases/new` `/analytics` `/wallet` `/purchases` `/collaborations` `/presave-manager` `/fan-analytics` `/revenue` `/leaderboard` `/goals` `/settings` `/presave/:id` `/artist/:slug` `/spotify-canvas` `/content-id` `/admin` `/admin/submissions` `/admin/users` `/admin/users/:userId` `/admin/beats` `/admin/royalty-import`

## Remaining Backlog
- P1: Real Spotify OAuth with API credentials (user has developer account)
- P2: Apple Music / YouTube Music API connections
- P2: Replace simulated DSP data with real API feeds
