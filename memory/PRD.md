# Kalmori — TuneCore Clone / Digital Music Distribution Platform

## Problem Statement
Build a TuneCore clone / high-volume digital content aggregator and B2B e-commerce platform for musicians. Core requirements include Authentication, Subscriptions, Object Storage for high-res files, AI Features, Artist/User management, Release/Track uploads, Distribution store management, Beat Marketplace, and strict Kalmori white-labeling. Must include Admin-only Elementor-style Page Builder, Client Revenue Dashboards, and full admin control.

## Architecture
- **Frontend**: React + Tailwind CSS + Shadcn/UI + Framer Motion + @dnd-kit
- **Backend**: FastAPI (Python) + MongoDB
- **Payments**: Stripe + PayPal
- **Storage**: Emergent Object Storage
- **AI**: Emergent LLM Key (OpenAI)
- **Email**: Resend API (support@kalmori.org)
- **Auth**: JWT + Google OAuth (Emergent)
- **DSP**: Spotify Web API (spotipy)
- **PDF**: reportlab
- **Audio**: pydub + ffmpeg
- **QR**: qrcode

## Key Credentials
- Admin: submitkalmori@gmail.com / Admin123!
- Secondary Admin: admin@kalmori.com / Admin123!
- Spotify Client ID: f3d8dbd3c4f441efa5ca51edd0d455b1

## Implemented Features (All Tested & Verified)
1. Auth (JWT + Google OAuth + reCAPTCHA + Password Reset)
2. Subscription Plans (Free/Pro/Label) with Stripe Checkout
3. Release/Track Wizard (4-tab flow with audio upload)
4. Distribution Management (store selection, status tracking)
5. Fan Analytics Dashboard
6. AI Release Strategy (Emergent LLM)
7. Save & Compare Strategies + PDF Export
8. AI Smart Notifications + Weekly Digest Emails (Resend)
9. Revenue Analytics & Royalty Calculator
10. Release Performance Leaderboard
11. Goal Tracking & Milestones
12. Artist Public Profile (link-in-bio, QR codes, theme colors)
13. Beat Marketplace (4-tier licensing, watermarking)
14. Digital Contracts & E-Signatures
15. Collaboration Hub + In-App Messaging
16. Producer Royalty Split System
17. Admin Payout Dashboard
18. **Admin Page Builder V1** — Drag-and-drop visual editor, 12 block types
19. **Admin Page Builder V2** — Custom CSS, Image uploads, Block duplication, Multi-page (Landing/About/Pricing)
20. **Page Builder Auto-Seeding** — Pages pre-populate with current site content (14 Landing, 5 About, 4 Pricing blocks) — *Apr 2026*
21. **Spotify DSP OAuth Integration** — Real artist data, top tracks, albums, related artists — *Apr 2026*
22. **Admin User Cleanup** — Endpoint to delete all non-admin users and related data — *Apr 2026*

## Remaining / Future Tasks
- P0: User must add redirect URI to Spotify Developer Dashboard (DONE)
- P0: Deploy to kalmori.org (Save to Github)
- P2: Further server.py refactoring (analytics, purchases → /routes/)
- P3: Apple Music / YouTube Music integration
