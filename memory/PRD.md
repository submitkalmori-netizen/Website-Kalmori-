# TuneDrop / Kalmori - Product Requirements Document

## Overview
A TuneCore clone / high-volume digital content aggregator and B2B e-commerce platform for musicians. Built as a React Web Application matching the user's existing "Kalmori" React Native Expo app design.

## Tech Stack
- **Frontend**: React + Tailwind CSS + Shadcn/UI
- **Backend**: FastAPI (Python) + Motor (async MongoDB)
- **Database**: MongoDB
- **Auth**: Dual (JWT cookies + Bearer token with localStorage) + Google OAuth (Emergent)
- **Payments**: Stripe (via Emergent Integrations)
- **Storage**: Emergent Object Storage
- **Email**: Resend (optional, via env var)

## Architecture
```
/app/
├── backend/
│   ├── server.py          # Main backend (auth, releases, tracks, admin, wallet, AI, etc.)
│   ├── kalmori_routes.py  # GitHub-merged routes (CMS, Cart, Credits, Social, Stats, Genres, etc.)
│   ├── tests/             # Pytest tests (iteration 9: 28 tests)
│   ├── requirements.txt
│   └── .env
├── frontend/
│   ├── src/
│   │   ├── App.js                    # Routes, AuthContext, CartProvider
│   │   ├── services/api.js           # Exact port of GitHub api.ts (all endpoint methods)
│   │   ├── context/CartContext.jsx    # Cart state management
│   │   ├── components/               # PublicLayout, AdminLayout, DashboardLayout, GlobalFooter
│   │   └── pages/                    # 15+ pages
│   └── .env
└── memory/ (PRD.md, test_credentials.md)
```

## Completed Features

### Frontend
- [x] Landing Page, Pricing, Services, Stores, Contact, About, Promoting, Publishing, Instrumentals, Terms, Privacy
- [x] PublicLayout with slide-out menu matching Kalmori exactly
- [x] Admin Dashboard, User Dashboard, Auth pages
- [x] **API Service** (`services/api.js`) - Exact 1:1 port of GitHub `api.ts` [Apr 2, 2026]
- [x] **AuthContext** - Bearer token + localStorage + 30min inactivity timeout [Apr 2, 2026]
- [x] **CartContext** - Cart state management [Apr 2, 2026]

### Backend - Core (server.py)
- [x] Dual auth (cookies + Bearer), Extended UserCreate fields
- [x] Release/Track CRUD, Distribution, Payments, Wallet, Analytics, AI features
- [x] Notifications, Subscriptions, Admin dashboard, Ingestion/Review, Split payments

### Backend - Kalmori Routes (kalmori_routes.py)
- [x] CMS (slides, pricing, legal, full pages, instrumentals)
- [x] Shopping Cart (CRUD + Stripe checkout)
- [x] Credits system, Payment Methods (with set-default), Extended Wallet/Withdrawals
- [x] Social features (follow/unfollow, followers/following lists)
- [x] Testimonials, Theme, Promotion Orders, Instrumental Requests
- [x] **Stats endpoint** (`/api/stats`) [Apr 2, 2026]
- [x] **Genres endpoint** (`/api/genres`) [Apr 2, 2026]
- [x] **Transactions endpoint** (`/api/transactions`) [Apr 2, 2026]
- [x] **Set-default payment method** (`/api/payment-methods/{id}/set-default`) [Apr 2, 2026]
- [x] **Streaming analytics** (`/api/analytics/streaming/{userId}`) [Apr 2, 2026]
- [x] **Followers/Following lists** (`/api/artists/{id}/followers`, `/following`) [Apr 2, 2026]
- [x] **Withdrawals v2** (`/api/withdrawals` POST/GET) [Apr 2, 2026]
- [x] Public releases, Video serving, reCAPTCHA

## Upcoming Tasks (P1)
- [ ] AI Features integration using Emergent LLM Key
- [ ] Advanced Analytics Dashboard (Audience Map, TikTok UGC)
- [ ] Email notifications & password reset
- [ ] PayPal payment integration

## Future Tasks (P2)
- [ ] Beat audio previews on Leasing page
- [ ] Backend modularization
- [ ] YouTube Content ID / Spotify Canvas

## Testing
- iteration_7: 100% (27/27) - Kalmori routes merge
- iteration_8: 100% (16/16) - Auth & service layer
- iteration_9: 100% (28/28) - api.ts port + new endpoints
