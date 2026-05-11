# WorkNow – Full Project Documentation

> **Find Work. Find Workers. Instantly.**

---

## Table of Contents

1. [Problem Statement](#1-problem-statement)
2. [Our Solution](#2-our-solution)
3. [Application Overview](#3-application-overview)
4. [System Architecture](#4-system-architecture)
5. [Tech Stack](#5-tech-stack)
6. [Project Structure](#6-project-structure)
7. [Backend Services](#7-backend-services)
8. [Frontend Pages](#8-frontend-pages)
9. [Database Schema](#9-database-schema)
10. [Application Workflows](#10-application-workflows)
11. [API Reference](#11-api-reference)
12. [Infrastructure & Ports](#12-infrastructure--ports)
13. [Environment Variables](#13-environment-variables)
14. [Getting Started](#14-getting-started)
15. [Testing](#15-testing)

---

## 1. Problem Statement

### The Challenge

**Students** in India and similar markets face a major gap between their availability and income opportunities:

- Students have **free hours between classes**, weekends, and vacation periods but lack access to legitimate, short-term, on-demand work.
- Traditional job portals (Naukri, LinkedIn) target full-time employment — they are **not designed for hourly or task-based gigs**.
- Platforms like Swiggy/Zomato only offer delivery roles. There is **no platform for general skill-based student gigs** (moving help, tutoring, event staffing, cleaning, etc.).
- Students lack a **verified identity layer** — employers cannot trust unverified strangers for home/office tasks.

**Employers** (homeowners, small businesses, event organizers) face the opposite problem:

- They need **temporary, on-demand help** (a few hours to a few days) but cannot justify hiring full-time staff.
- Finding reliable short-term workers is done through word-of-mouth or informal WhatsApp groups — **unreliable and slow**.
- There is **no escrow or payment protection** — paying strangers upfront is risky.
- **No way to verify** if a worker is genuinely a student or has the right skills.

### Root Cause

There is **no dedicated, trusted marketplace** that:
- Connects students with nearby employers in real time
- Verifies student identity via KYC documents
- Handles payments safely through an integrated wallet
- Matches workers to jobs intelligently by location + skills

---

## 2. Our Solution

**WorkNow** is a production-grade, mobile-first **gig marketplace** built specifically for students and local employers.

### How WorkNow Solves Each Problem

| Problem | WorkNow Solution |
|---------|-----------------|
| Students can't find flexible gigs | Map-based job feed showing gigs within 5 km of the student's live location |
| Employers can't find verified workers | KYC verification system (Aadhar, PAN, Student ID, Selfie) with admin review |
| Trust gap between strangers | Verified badge system + rating system after each completed gig |
| No smart worker–job matching | Geo-radius search (5 km) + skill-tag filtering powered by the Matching Service |
| Risky cash payments | Integrated wallet with Razorpay top-up; funds transferred only on job completion |
| No real-time communication | Push notifications via Firebase FCM + SMS via MSG91 for critical alerts |
| Workers miss nearby opportunities | Event-driven alerts: new job posted → matching workers notified instantly |

### Key Value Propositions

- 🎓 **For Students (Workers):** Find nearby gigs, get verified, earn money directly to your wallet, withdraw anytime.
- 🏢 **For Employers:** Post a job in minutes, see verified nearby workers, pay safely through escrow-style wallet transfers.
- ⚡ **For Both:** Real-time notifications, transparent transaction history, mobile-first design.

---

## 3. Application Overview

WorkNow has two distinct user experiences on a single platform:

### Worker (Student) Journey
1. Sign up with phone number → receive OTP
2. Complete profile: name, skills, location
3. Upload KYC documents → get verified
4. Open app → see nearby jobs on a map
5. Apply to a job → employer reviews and hires
6. Complete the task → get paid to wallet
7. Withdraw earnings or keep in wallet for future use

### Employer Journey
1. Sign up with phone number → receive OTP
2. Complete employer profile
3. Top up wallet via Razorpay
4. Post a gig: title, description, location, budget, required skills
5. Receive applications from nearby matched workers
6. Review applicant profiles + verification status
7. Hire a worker → track job progress
8. Mark job as complete → payment auto-transfers to worker

---

## 4. System Architecture

WorkNow is a **monorepo** (Turborepo) with a Next.js frontend and **6 independently deployable NestJS microservices** orchestrated via Docker Compose.

```
┌────────────────────────────────────────────────────────────┐
│                        CLIENT LAYER                        │
│              Mobile Browser / Web Browser                  │
└────────────────────┬───────────────────────────────────────┘
                     │
┌────────────────────▼───────────────────────────────────────┐
│               FRONTEND  (Next.js 14 · Port 3000)           │
│  Splash · Login · Worker App · Employer App                │
└──┬──────┬──────┬──────┬──────┬─────────────────────────────┘
   │      │      │      │      │
   ▼      ▼      ▼      ▼      ▼
 Auth   User   Job   Payment  Match
:3001  :3002  :3003  :3004   :3006
                                     Notification :3005
                                     (event-driven only)

All services communicate asynchronously via Google Cloud Pub/Sub
All services persist to isolated PostgreSQL databases
Auth & Matching use Redis for OTP/session/geo caching
```

### Event-Driven Communication (Pub/Sub Topics)

| Publisher | Event | Subscriber(s) |
|-----------|-------|--------------|
| Job Service | `job.created` | Matching Service, Notification Service |
| Job Service | `application.submitted` | Notification Service |
| Job Service | `job.completed` | Payment Service, Notification Service |
| Payment Service | `payment.completed` | Notification Service |
| User Service | `user.verified` | Notification Service |

---

## 5. Tech Stack

| Layer | Technology | Purpose |
|-------|-----------|---------|
| **Frontend** | Next.js 14, React 18, TypeScript | App framework (App Router) |
| **Styling** | Tailwind CSS 3 | Utility-first UI styling |
| **Maps** | React-Leaflet + OpenStreetMap | Job location display on map |
| **Location Input** | Google Maps Places API | Autocomplete for job location entry |
| **Auth (Client)** | NextAuth.js | Session management |
| **Backend Framework** | NestJS + TypeScript | All 6 microservices |
| **ORM** | Prisma ORM | Type-safe database access |
| **Database** | PostgreSQL 15 | Persistent storage (one DB per service) |
| **Cache / OTP** | Redis 7 | OTP TTL (5 min), worker geo-cache |
| **Message Bus** | Google Cloud Pub/Sub (emulated) | Async inter-service events |
| **Payments** | Razorpay | Wallet top-up & payment verification |
| **Push Notifications** | Firebase Cloud Messaging (FCM) | Mobile & web push alerts |
| **SMS** | MSG91 | OTP delivery & payment alerts |
| **Monorepo** | Turborepo | Parallel builds & dev tasks |
| **Containerisation** | Docker + Docker Compose | Local infrastructure orchestration |

---

## 6. Project Structure

```
work_now-/
├── frontend/                        # Next.js 14 App Router application
│   ├── src/
│   │   ├── app/
│   │   │   ├── page.tsx             # Animated splash / landing screen
│   │   │   ├── login/               # Phone + OTP login flow
│   │   │   ├── worker/              # Worker (student) experience
│   │   │   │   ├── home/            # Map-based job feed
│   │   │   │   ├── job/             # Job detail & apply
│   │   │   │   ├── tasks/           # Active & past gigs
│   │   │   │   ├── wallet/          # Earnings & balance
│   │   │   │   └── profile/         # Profile editor & KYC upload
│   │   │   └── customer/            # Employer experience
│   │   │       ├── home/            # Dashboard
│   │   │       ├── post-job/        # Create a new gig
│   │   │       ├── tasks/           # Manage posted jobs
│   │   │       ├── wallet/          # Top-up & payment history
│   │   │       └── profile/         # Employer profile
│   │   ├── components/              # Shared UI components (LeafletMap, LocationPicker…)
│   │   └── lib/                     # API clients & utilities
│   └── package.json
│
├── backend/
│   ├── services/
│   │   ├── auth/                    # Identity & OTP service (Port 3001)
│   │   ├── user/                    # Profile & KYC service (Port 3002)
│   │   ├── job/                     # Gig CRUD service (Port 3003)
│   │   ├── payment/                 # Wallet & Razorpay service (Port 3004)
│   │   ├── notification/            # FCM & SMS delivery (Port 3005)
│   │   └── matching/                # Geo-based matching (Port 3006)
│   ├── shared/                      # Shared lib: Prisma client, logger, types
│   ├── docker-compose.yml           # Full-stack orchestration
│   ├── turbo.json                   # Turborepo pipeline config
│   └── package.json
│
├── APPLICATION_FLOW.md
├── INSTALL_GUIDE.md
├── DOCUMENTATION.md                 # ← This file
└── README.md
```

---

## 7. Backend Services

### 🔐 Auth Service — Port `3001`

Handles all identity and authentication.

**Responsibilities:**
- Phone-based **OTP login** (6-digit code, 5-minute TTL stored in Redis)
- Issues **JWT access tokens** (15 min) and **refresh tokens** (7 days)
- Auto-creates a user account on first successful OTP verification
- Role assignment: `WORKER` or `EMPLOYER` at sign-up time

**Key Files:**
- `auth.service.ts` — OTP generation, JWT issuance, token refresh
- `auth.controller.ts` — REST endpoints
- `otp.service.ts` — Redis-backed OTP storage and validation

**Flow:**
```
POST /auth/send-otp   { phone, countryCode }   → OTP stored in Redis (TTL 300s)
POST /auth/verify-otp { phone, otp, role }     → { accessToken, refreshToken, expiresIn }
POST /auth/refresh    { refreshToken }          → New token pair
```

**Database:** `worknow_auth` — `User { id, phone, role, lastLoginAt }`  
**Cache:** Redis — key `otp:{phone}` with 300s TTL

---

### 👤 User Service — Port `3002`

Single source of truth for all profile data.

**Responsibilities:**
- Create & update `UserProfile` (name, bio, avatar, skills, location)
- Upload & manage **KYC / Verification Documents**
- Track `walletBalance` (`Decimal(10,2)`)
- Verification workflow: `PENDING → VERIFIED / REJECTED`
- Real-time **presence** tracking (`isOnline`)
- Rating system — average from `totalRatings` counter

**Data Models:**

| Model | Key Fields |
|-------|-----------|
| `UserProfile` | `userId`, `name`, `role`, `skills[]`, `locationLat/Lng`, `walletBalance`, `verificationStatus`, `rating` |
| `VerificationDocument` | `type` (AADHAR / PAN / STUDENT_ID / SELFIE), `url`, `status` |

**Database:** `worknow_user`

---

### 💼 Job Service — Port `3003`

Manages the full gig lifecycle.

**Responsibilities:**
- CRUD for job postings (title, description, location, budget, skills)
- Job status machine: `OPEN → ASSIGNED → IN_PROGRESS → COMPLETED`
- Manages worker applications
- Publishes Pub/Sub events: `job.created`, `application.submitted`, `job.completed`

**Database:** `worknow_job`

---

### 📍 Matching Service — Port `3006`

The intelligence layer connecting workers to jobs.

**Responsibilities:**
- Subscribes to `job.created` events from Pub/Sub
- **Geo-radius search** (default **5 km**) using worker location cached in Redis
- **Skill matching** — filters workers whose skill tags overlap with job requirements
- Returns up to **10 ranked worker matches** per job

**Config:**
```
GEO_RADIUS_KM=5
MAX_WORKERS_PER_JOB=10
```

---

### 💳 Payment Service — Port `3004`

Handles all money movement.

**Responsibilities:**
- **Wallet top-up** via Razorpay (create order → verify webhook → credit balance)
- **Job payment** — transfers funds from employer wallet to worker wallet on completion
- All transactions logged in `Transaction` table
- Validates Razorpay webhook signatures (HMAC-SHA256)
- Publishes `payment.completed` to Pub/Sub

**Database:** `worknow_payment`

---

### 🔔 Notification Service — Port `3005`

Delivers all user-facing alerts.

**Responsibilities:**
- Subscribes to: `job.created`, `application.submitted`, `payment.completed`
- Sends **FCM push notifications** to mobile & web
- Sends **SMS via MSG91** for critical alerts
- Stores notification history in DB

**Database:** `worknow_notification`

---

## 8. Frontend Pages

| Route | Role | Description |
|-------|------|-------------|
| `/` | Both | Animated splash screen with ambient gradient |
| `/login` | Both | Phone entry + OTP verification |
| `/worker/home` | Worker | Map view of nearby gigs (React-Leaflet) |
| `/worker/job` | Worker | Job detail view + application form |
| `/worker/tasks` | Worker | Active & completed task history |
| `/worker/wallet` | Worker | Earnings, balance, transaction history |
| `/worker/profile` | Worker | Profile editor, KYC doc upload, verification status |
| `/customer/home` | Employer | Dashboard with posted jobs overview |
| `/customer/post-job` | Employer | New gig creation form |
| `/customer/tasks` | Employer | Manage jobs, review applicants, hire/reject |
| `/customer/wallet` | Employer | Top up wallet, payment history |
| `/customer/profile` | Employer | Employer profile management |

### Key UI Components

- **`LeafletMap.tsx`** — Interactive map using OpenStreetMap tiles. Renders worker's GPS position and nearby job markers.
- **`LocationPicker.tsx`** — Google Maps Places autocomplete for job location entry when posting a gig.

---

## 9. Database Schema

Each microservice owns its own **isolated PostgreSQL database**. Below is the User Service schema (most complex):

```
UserProfile
───────────────────────────────────────
id                  String   PK  (cuid)
userId              String   UNIQUE  ← refers to Auth service
name                String
email               String?
avatarUrl           String?
bio                 String?
role                String   (EMPLOYER | WORKER)
verificationStatus  Enum     (PENDING | VERIFIED | REJECTED)
rating              Float    default 0
totalRatings        Int      default 0
skills              String[]
locationLat         Float?
locationLng         Float?
locationCity        String?
isOnline            Boolean  default false
walletBalance       Decimal(10,2)  default 0
createdAt           DateTime
updatedAt           DateTime

VerificationDocument  (many per UserProfile)
───────────────────────────────────────
id          String   PK
profileId   String   FK → UserProfile
type        String   (AADHAR | PAN | STUDENT_ID | SELFIE)
url         String
status      String   (PENDING | VERIFIED | REJECTED)
createdAt   DateTime
```

---

## 10. Application Workflows

### 1. Registration & Onboarding

```
User enters phone number
    └─► Frontend → POST /auth/send-otp
    └─► Auth Service generates OTP → stores in Redis (300s TTL)
User enters 6-digit OTP
    └─► Frontend → POST /auth/verify-otp { phone, otp, role }
    └─► Auth validates OTP → upserts User record in DB
    └─► Returns { accessToken, refreshToken }
    └─► Frontend → POST /users/profile (creates profile)
    └─► Redirects to Worker or Employer home
```

### 2. Job Posting & Matching

```
Employer fills job form (title, location, budget, skills)
    └─► Frontend → POST /jobs
    └─► Job Service saves job → publishes job.created to Pub/Sub
    └─► Matching Service receives event
            → geo-radius search (5km) in Redis
            → skill-tag filter
            → ranked list of up to 10 workers
    └─► Notification Service receives event
            → FCM push to matched workers: "New job near you!"
Worker sees job on map → applies
    └─► Frontend → POST /jobs/:id/apply
    └─► Job Service publishes application.submitted
    └─► Notification Service → FCM push to employer: "New application received"
```

### 3. Hiring & Payment Flow

```
Employer reviews applicants → hires a worker
    └─► PATCH /jobs/:id/hire/:workerId
    └─► Job status: OPEN → ASSIGNED → IN_PROGRESS

Worker completes the task → Employer marks done
    └─► PATCH /jobs/:id/complete
    └─► Job Service publishes job.completed
    └─► Payment Service transfers funds: employer wallet → worker wallet
    └─► Transaction logged in DB
    └─► Both parties notified via FCM
```

### 4. Wallet Top-Up

```
Employer clicks "Add Money"
    └─► Frontend → POST /payments/order { amount }
    └─► Payment Service → creates Razorpay order → returns order_id
    └─► Frontend opens Razorpay payment modal
    └─► User pays → Razorpay webhook fires → POST /payments/webhook
    └─► Payment Service verifies HMAC signature
    └─► Employer walletBalance credited
```

---

## 11. API Reference

### Auth Service (`localhost:3001`)

| Method | Endpoint | Body | Response |
|--------|----------|------|----------|
| `POST` | `/auth/send-otp` | `{ phone, countryCode }` | `{ message }` |
| `POST` | `/auth/verify-otp` | `{ phone, otp, role }` | `{ accessToken, refreshToken, expiresIn }` |
| `POST` | `/auth/refresh` | `{ refreshToken }` | `{ accessToken, refreshToken, expiresIn }` |
| `GET` | `/health` | — | `{ status: "ok" }` |

### User Service (`localhost:3002`)

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/users/profile` | Create user profile |
| `GET` | `/users/profile/:id` | Get profile (with verification docs) |
| `PATCH` | `/users/profile/:id` | Update profile fields |
| `PATCH` | `/users/profile/:id/location` | Update live location |
| `POST` | `/users/profile/:id/docs` | Upload verification document |
| `GET` | `/health` | Health check |

### Job Service (`localhost:3003`)

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/jobs` | Create a new job/gig |
| `GET` | `/jobs` | List jobs (with filters) |
| `GET` | `/jobs/:id` | Get job details |
| `PATCH` | `/jobs/:id` | Update job |
| `POST` | `/jobs/:id/apply` | Apply to a job (worker) |
| `PATCH` | `/jobs/:id/hire/:workerId` | Hire a specific worker |
| `PATCH` | `/jobs/:id/complete` | Mark job as complete |

### Payment Service (`localhost:3004`)

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/payments/order` | Create Razorpay order |
| `POST` | `/payments/verify` | Verify payment & credit wallet |
| `POST` | `/payments/webhook` | Razorpay webhook handler |
| `GET` | `/payments/transactions` | List wallet transactions |

### Matching Service (`localhost:3006`)

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/matching/jobs` | Get nearby jobs (`?lat=&lng=`) |
| `GET` | `/matching/workers/:jobId` | Get matched workers for a job |

---

## 12. Infrastructure & Ports

| Service | Container | Host Port |
|---------|-----------|-----------|
| PostgreSQL | `worknow-postgres` | `5432` |
| Redis | `worknow-redis` | `6379` |
| Pub/Sub Emulator | `worknow-pubsub` | `8085` |
| Auth Service | `worknow-auth` | `3001` |
| User Service | `worknow-user` | `3002` |
| Job Service | `worknow-job` | `3003` |
| Payment Service | `worknow-payment` | `3004` |
| Notification Service | `worknow-notification` | `3005` |
| Matching Service | `worknow-matching` | `3006` |
| Frontend (Next.js) | _(local)_ | `3000` |

All services are connected via a Docker bridge network `worknow-net`.

---

## 13. Environment Variables

### Backend (`backend/.env`)

```env
# PostgreSQL (per service — replace <service>)
DATABASE_URL=postgresql://worknow:worknow@localhost:5432/worknow_<service>

# Redis
REDIS_URL=redis://localhost:6379

# Auth
JWT_SECRET=your-secret-key
JWT_EXPIRY=15m
JWT_REFRESH_EXPIRY=7d
OTP_TTL_SECONDS=300

# GCP Pub/Sub (emulated locally)
PUBSUB_EMULATOR_HOST=localhost:8085
GCP_PROJECT_ID=worknow-dev

# Razorpay (Payment Service)
RAZORPAY_KEY_ID=rzp_test_xxx
RAZORPAY_KEY_SECRET=your_secret
RAZORPAY_WEBHOOK_SECRET=webhook_secret

# Firebase (Notification Service)
FCM_PROJECT_ID=your-firebase-project
FCM_CLIENT_EMAIL=service-account@project.iam.gserviceaccount.com
FCM_PRIVATE_KEY="-----BEGIN RSA PRIVATE KEY-----\n..."

# SMS
SMS_API_KEY=msg91_api_key
SMS_SENDER_ID=WRKSNW
```

### Frontend (`frontend/.env.local`)

```env
NEXT_PUBLIC_AUTH_SERVICE_URL=http://localhost:3001
NEXT_PUBLIC_USER_SERVICE_URL=http://localhost:3002
NEXT_PUBLIC_JOB_SERVICE_URL=http://localhost:3003
NEXT_PUBLIC_GOOGLE_MAPS_API_KEY=your_google_maps_key
NEXT_PUBLIC_SUPABASE_URL=https://xxx.supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=your_anon_key
```

---

## 14. Getting Started

### Prerequisites

| Tool | Version |
|------|---------|
| Node.js | `>= 20.0.0` |
| npm | `>= 10.0.0` |
| Docker & Docker Compose | Latest |
| Git | Latest |

### Installation

```bash
# 1. Clone the repository
git clone https://github.com/aayash317-svg/work_now-.git
cd work_now-

# 2. Install backend dependencies
cd backend
npm install

# 3. Install frontend dependencies
cd ../frontend
npm install
```

### Running the Application

```bash
# Step 1 — Start infrastructure (PostgreSQL, Redis, Pub/Sub)
cd backend
npm run docker:up

# Step 2 — Run DB migrations for each service
cd backend/services/auth       && npx prisma migrate dev --name init
cd backend/services/user       && npx prisma migrate dev --name init
cd backend/services/job        && npx prisma migrate dev --name init
cd backend/services/payment    && npx prisma migrate dev --name init
cd backend/services/notification && npx prisma migrate dev --name init

# Step 3 — Start all backend services (Turborepo runs all 6 in parallel)
cd backend
npm run dev

# Step 4 — Start the frontend
cd frontend
npm run dev
# → http://localhost:3000
```

### Useful Commands

```bash
npm run docker:logs    # View container logs
npm run docker:down    # Stop all containers
npm run migrate:dev    # Run all migrations
npm run lint           # Lint all packages
npm run typecheck      # Type-check all packages
npm run test           # Run all unit tests
```

---

## 15. Testing

```bash
# Unit tests (all services)
cd backend && npm run test

# CI mode — no watch, with coverage
cd backend && npm run test:ci

# Sequential safe run (for CI pipelines)
cd backend && npm run test:all
```

**Testing strategy:**
- **Unit tests** — NestJS services mocked with `jest-mock-extended` for Prisma
- **Integration tests** — Docker-based PostgreSQL with full migration run
- **Contract tests** — OpenAPI schema validation against live REST responses

---

## Related Documents

| Document | Description |
|----------|-------------|
| [README.md](./README.md) | Quick-start overview |
| [APPLICATION_FLOW.md](./APPLICATION_FLOW.md) | End-to-end user journey diagrams |
| [INSTALL_GUIDE.md](./INSTALL_GUIDE.md) | Step-by-step environment setup |
| [Prisma Schema Doc](./backend/services/user/PRISMA_SCHEMA_DOC.md) | Full DB schema, CRUD examples, security notes |

---

*Built with ❤️ for students who hustle. — WorkNow Team © 2026*
