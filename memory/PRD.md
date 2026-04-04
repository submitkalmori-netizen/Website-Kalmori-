# Kalmori - TuneCore Clone PRD

## Original Problem Statement
Build a TuneCore clone / high-volume digital content aggregator and B2B e-commerce platform for musicians with Authentication, Subscriptions, Object Storage, AI Features, Release/Track uploads with a professional Wizard, Distribution to 150+ platforms, Beat/Instrumental catalog, and dark premium UI.

## Architecture
- **Frontend**: React + Tailwind CSS + Shadcn/UI + Recharts + Phosphor Icons + Framer Motion
- **Backend**: FastAPI (modularized: server.py + core.py + /routes/)
- **Database**: MongoDB (18+ collections)
- **Storage**: Emergent Object Storage | **Payments**: Stripe + PayPal
- **Auth**: JWT + Google Social Login + reCAPTCHA v2 + Email Verification
- **AI**: OpenAI GPT-4o via Emergent LLM Key | **Email**: Resend | **PDF**: reportlab

## UI Color Theme
- **Landing page & site-wide buttons**: Purple/Pink/Magenta animated gradient (#7C4DFF -> #E040FB -> #FF4081)
- **Login & Register pages only**: Blue-to-Purple animated gradient (#0095FF -> #7468F8)
- **Button pairs**: First = filled animated, Second = outline with animated border

## Subscription Tiers
| Plan | Price | Revenue Share | Releases | Features |
|------|-------|---------------|----------|----------|
| Free | $0 | 20% taken | 1/year | Basic distribution, analytics, support |
| Rise | $9.99/mo | 10% taken | Unlimited | + Revenue dashboard, Fan Analytics, Goals, Priority support |
| Pro | $19.99/mo | 0% (keep 100%) | Unlimited | ALL features: AI Strategy, Content ID, Spotify Canvas, Leaderboard, Pre-Save, Collaborations, Dedicated support |

## All Completed Features

### Core Auth & Emails
- JWT + Google OAuth + reCAPTCHA + Email Verification (24h token)
- Welcome emails (Artist/Producer differentiated), Admin sign-up notifications
- Resend verification endpoint

### Email Domain Management (P3 — DONE Apr 2026)
- Admin page at /admin/email-settings for custom domain configuration
- Add domain via Resend API, view DNS records, copy values
- Verify domain, activate as sender (updates SENDER_EMAIL)
- Currently using test domain (onboarding@resend.dev), admin can switch to custom

### Subscription & Plan Gating
- 3-tier subscription system (Free/Rise/Pro) with Stripe checkout
- DistroKid-style pricing page with revenue share comparison bars
- Sidebar feature gating: lock icons, plan badges, upgrade CTA

### Admin Dashboard
- Overview stats, Users, Submissions, Beat Manager
- Multi-Format Royalty Import (CSV/XLSX/PDF) with auto-notifications
- Distributor Templates, Reconciliation with Bulk Actions
- Import Schedules (weekly/monthly reminders)
- Marketing Campaigns: create, preview, send to targeted audiences
- Lead Follow-Up: abandoned draft tracking, individual/bulk reminders
- Email Domain Settings: custom domain management via Resend API

### Client Features (Artist + Producer parity)
- Revenue Analytics with Kalmori integration + Revenue Export (CSV/PDF)
- Release Leaderboard, AI Release Strategy + PDF Export, AI Smart Notifications
- Fan Analytics, Goal Tracking & Milestones
- 4-tab Release Wizard, 150+ platforms, Beat catalog, Wallet
- Artist Profile Public Page, Pre-Save Campaigns, Collaborations

### UI/UX Dark Theme (Apr 2026)
- Landing page: Purple/pink animated gradient text and buttons
- Login & Register pages: Blue-to-purple animated gradient (#0095FF -> #7468F8)
- Button pairs: filled animated + outline animated border
- Kalmori Artist Agreement page (Artist + Producer/Label tabs)
- Footer KALMORI logo: animated purple/pink with glow
- 'Made with Emergent' badge hidden

## All Pages & Routes
`/` `/login` `/register` `/select-role` `/verify-email` `/pricing` `/label` `/instrumentals` `/dashboard` `/releases` `/releases/new` `/analytics` `/wallet` `/purchases` `/collaborations` `/presave-manager` `/fan-analytics` `/revenue` `/leaderboard` `/goals` `/settings` `/presave/:id` `/artist/:slug` `/spotify-canvas` `/content-id` `/admin` `/admin/submissions` `/admin/users` `/admin/users/:userId` `/admin/beats` `/admin/royalty-import` `/admin/campaigns` `/admin/leads` `/admin/email-settings` `/agreement`

## Remaining Backlog
- P1: Real Spotify OAuth with API credentials (user has developer account)
- P2: Apple Music / YouTube Music API connections
- P2: Replace simulated DSP data with real API feeds
