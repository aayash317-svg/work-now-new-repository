# WorkNow – Student Gig Marketplace

> **Find Work. Find Workers. Instantly.**

WorkNow is a production-grade, **micro-service marketplace** that connects **student freelancers (Workers)** with **Employers** for short-term gigs. Built with a modern TypeScript stack, it features phone-based OTP authentication, location-aware job matching, an integrated wallet, KYC verification, and real-time push notifications.

---

## 📑 Table of Contents

1. [Overview](#overview)
2. [Architecture](#architecture)
3. [Tech Stack](#tech-stack)
4. [Project Structure](#project-structure)
5. [Backend Services Deep Dive](#backend-services-deep-dive)
6. [Frontend Deep Dive](#frontend-deep-dive)
7. [Database Schema](#database-schema)
8. [Application Workflows](#application-workflows)
9. [Infrastructure & Ports](#infrastructure--ports)
10. [Environment Variables](#environment-variables)
11. [Getting Started](#getting-started)
12. [Running the Application](#running-the-application)
13. [Mobile Access](#mobile-access)
14. [API Reference](#api-reference)
15. [Testing](#testing)
16. [Documentation](#documentation)

---

## Overview

WorkNow solves the problem of students finding flexible, short-term local gigs while giving small employers a fast way to hire verified student talent. The platform is split into two experiences:

| Role | What they do |
|------|-------------|
| **Worker** (Student) | Browse nearby gigs on a map, apply, complete tasks, get paid to their wallet |
| **Employer** (Customer) | Post jobs with location & budget, review applicants, hire, mark completion, pay |

---

## Architecture

The application is a **monorepo** (`Turborepo`) containing a Next.js frontend and six independently deployable NestJS microservices orchestrated via Docker Compose.

```mermaid
flowchart TD
    subgraph Client
        Mobile[📱 Mobile Browser]
        Web[🖥️ Web Browser]
    end

    subgraph Frontend["Frontend (Next.js :3000)"]
        Splash[Splash / Landing]
        Login[Login - OTP]
        WorkerApp[Worker App]
        EmployerApp[Employer App]
    end

    subgraph Backend["Backend Microservices"]
        Auth["🔐 Auth Service :3001"]
        User["👤 User Service :3002"]
        Job["💼 Job Service :3003"]
        Pay["💳 Payment Service :3004"]
        Notif["🔔 Notification Service :3005"]
        Match["📍 Matching Service :3006"]
    end

    subgraph Infra["Infrastructure"]
        PG[(PostgreSQL :5432)]
        Redis[(Redis :6379)]
        PubSub[GCP Pub/Sub Emulator :8085]
    end

    subgraph External["External APIs"]
        Razorpay[Razorpay]
        FCM[Firebase FCM]
        MSG91[MSG91 SMS]
    end

    Mobile & Web --> Frontend
    Frontend --> Auth
    Frontend --> User
    Frontend --> Job
    Frontend --> Pay
    Frontend --> Match

    Auth --> Redis
    Auth --> PG
    User --> PG
    User --> PubSub
    Job --> PG
    Job --> PubSub
    Match --> Redis
    Match --> PubSub
    Pay --> PG
    Pay --> PubSub
    Notif --> PubSub
    Notif --> FCM
    Notif --> MSG91
    Pay --> Razorpay
```

### Event-Driven Communication

Services communicate asynchronously through **Google Cloud Pub/Sub** (emulated locally). For example:
- `Job Service` publishes a `job.created` event → `Matching Service` picks it up and finds nearby workers.
- `Job Service` publishes `application.created` → `Notification Service` sends a push to the employer.
- `Payment Service` publishes `payment.completed` → `Notification Service` alerts the worker.

---

## Tech Stack

| Layer | Technology | Purpose |
|-------|-----------|---------|
| **Frontend** | Next.js 14, React 18, TypeScript | App framework |
| **Styling** | Tailwind CSS 3, Material Symbols | UI & icons |
| **Maps** | React-Leaflet, Google Maps API | Job location display |
| **Auth (Client)** | NextAuth.js, Supabase JS | Session & auth flow |
| **Backend Framework** | NestJS, TypeScript | All 6 microservices |
| **ORM** | Prisma ORM | Database access |
| **Database** | PostgreSQL 15 | Persistent storage |
| **Cache / OTP Store** | Redis 7 | OTP TTL, sessions, geo data |
| **Message Bus** | Google Cloud Pub/Sub (emulated) | Async inter-service events |
| **Payments** | Razorpay | Wallet top-up & payouts |
| **Push Notifications** | Firebase Cloud Messaging (FCM) | Mobile push alerts |
| **SMS** | MSG91 | OTP delivery |
| **Monorepo** | Turborepo | Parallel builds & tasks |
| **Containerisation** | Docker, Docker Compose | Local infra orchestration |

---

## Project Structure

```
work_now-/
├── frontend/                   # Next.js 14 application
│   ├── src/
│   │   ├── app/
│   │   │   ├── page.tsx        # Splash / landing screen
│   │   │   ├── login/          # OTP phone login
│   │   │   ├── worker/         # Worker experience
│   │   │   │   ├── home/       # Job map feed
│   │   │   │   ├── job/        # Job detail & apply
│   │   │   │   ├── tasks/      # Active & past gigs
│   │   │   │   ├── wallet/     # Earnings & balance
│   │   │   │   └── profile/    # Profile & KYC status
│   │   │   └── customer/       # Employer experience
│   │   │       ├── home/       # Dashboard
│   │   │       ├── post-job/   # Create a new gig
│   │   │       ├── tasks/      # Posted jobs management
│   │   │       ├── wallet/     # Payment & top-up
│   │   │       └── profile/    # Employer profile
│   │   ├── components/         # Shared UI components
│   │   └── lib/                # API clients, utilities
│   └── package.json
│
├── backend/
│   ├── services/
│   │   ├── auth/               # Identity & OTP service
│   │   ├── user/               # Profile & KYC service
│   │   ├── job/                # Gig CRUD service
│   │   ├── matching/           # Geo-based matching service
│   │   ├── payment/            # Wallet & Razorpay service
│   │   └── notification/       # FCM & SMS delivery service
│   ├── shared/                 # Shared TypeScript lib (Prisma, logger, types)
│   ├── docker-compose.yml      # Full stack orchestration
│   ├── turbo.json              # Turborepo pipeline config
│   └── package.json
│
├── APPLICATION_FLOW.md         # User journey documentation
├── INSTALL_GUIDE.md            # Step-by-step install guide
└── README.md                   # This file
```

---

## Backend Services Deep Dive

### 🔐 Auth Service — Port `3001`

Handles all identity and authentication concerns.

**Responsibilities:**
- Phone-based **OTP login** (6-digit, 5-minute TTL stored in Redis)
- Issues **JWT access tokens** (15 min) and **refresh tokens** (7 days)
- Upserts user records on first login (creates account automatically)
- Role assignment: `WORKER` or `EMPLOYER` at registration time

**Key Flows:**
```
POST /auth/send-otp   { phone, countryCode }  → OTP generated & stored in Redis
POST /auth/verify-otp { phone, otp, role }    → Returns { accessToken, refreshToken, expiresIn }
POST /auth/refresh    { refreshToken }         → Issues new token pair
```

**Internal DB:** `worknow_auth` (PostgreSQL) — stores `User { id, phone, role, lastLoginAt }`  
**Cache:** Redis — OTP key with 300s TTL

---

### 👤 User Service — Port `3002`

Single source of truth for all profile data.

**Responsibilities:**
- Create & update **UserProfile** (name, bio, avatar, skills, location)
- Manage **KYC / Verification Documents** (Aadhar, PAN, Student ID, Selfie)
- Track **wallet balance** (`Decimal(10,2)` precision)
- **Verification workflow**: `PENDING → VERIFIED / REJECTED` (admin review)
- Real-time **presence** tracking (`isOnline` flag)
- **Rating system**: average rating computed from `totalRatings` counter

**Data Models:**

| Model | Key Fields |
|-------|-----------|
| `UserProfile` | `userId` (auth ref), `name`, `role`, `skills[]`, `locationLat/Lng`, `walletBalance`, `verificationStatus`, `rating` |
| `VerificationDocument` | `type` (AADHAR/PAN/STUDENT_ID/SELFIE), `url`, `status` |

**Internal DB:** `worknow_user` (PostgreSQL)

---

### 💼 Job Service — Port `3003`

Manages the entire gig lifecycle.

**Responsibilities:**
- CRUD for job postings (title, description, location, budget, required skills)
- Tracks job status: `OPEN → ASSIGNED → IN_PROGRESS → COMPLETED`
- Manages applications from workers
- Publishes events to Pub/Sub: `job.created`, `application.submitted`, `job.completed`
- Communicates with `User Service` to validate employers and `Matching Service` to trigger worker search

**Internal DB:** `worknow_job` (PostgreSQL)

---

### 📍 Matching Service — Port `3006`

The intelligence layer that connects workers to jobs.

**Responsibilities:**
- Listens for `job.created` events via Pub/Sub
- Performs **geo-radius search** (default: **5 km radius**) using worker location data from Redis
- Applies **skill matching** — filters workers whose skill tags overlap with job requirements
- Returns ranked list of up to **10 workers per job**
- Caches active worker locations in Redis for fast proximity lookups

**Config:**
```
GEO_RADIUS_KM=5
MAX_WORKERS_PER_JOB=10
```

---

### 💳 Payment Service — Port `3004`

Handles all money movement.

**Responsibilities:**
- **Wallet top-up** via Razorpay (creates order → verifies webhook → credits balance)
- **Job payment** — transfers funds from employer wallet to worker wallet on job completion
- All transactions logged in `Transaction` table
- Validates Razorpay webhook signatures for security
- Publishes `payment.completed` events to Pub/Sub

**Internal DB:** `worknow_payment` (PostgreSQL)

---

### 🔔 Notification Service — Port `3005`

Delivers all user-facing alerts.

**Responsibilities:**
- Subscribes to Pub/Sub topics: `job.created`, `application.submitted`, `payment.completed`, etc.
- Sends **FCM push notifications** to mobile/web browsers
- Sends **SMS via MSG91** for critical alerts (e.g., OTP fallback, payment confirmation)
- Stores notification history in DB

**Internal DB:** `worknow_notification` (PostgreSQL)

---

## Frontend Deep Dive

The frontend is a **Next.js 14 App Router** application with two separate role-based experiences.

### Pages & Routes

| Route | Description |
|-------|-------------|
| `/` | Animated splash screen with loading progress bar |
| `/login` | Phone number entry + OTP verification |
| `/worker/home` | Map-based job feed showing nearby gigs |
| `/worker/job` | Job detail view and application form |
| `/worker/tasks` | Active and completed task history |
| `/worker/wallet` | Wallet balance, earnings, transaction history |
| `/worker/profile` | Profile editor, KYC doc upload, verification status |
| `/customer/home` | Employer dashboard with posted jobs overview |
| `/customer/post-job` | New gig creation form (title, location, budget, skills) |
| `/customer/tasks` | Manage posted jobs, review applicants, hire/reject |
| `/customer/wallet` | Top up wallet, payment history |
| `/customer/profile` | Employer profile management |

### Key Frontend Features
- **Animated splash screen** with ambient gradient blobs and a live progress bar
- **Map-first UI** using React-Leaflet to display gig locations with worker GPS
- **Places autocomplete** using Google Maps API for job location entry
- **Supabase** for additional backend integration (storage, auth helper)
- **NextAuth.js** session management

---

## Database Schema

Each microservice owns its own isolated PostgreSQL database. Below is the User Service schema (most complex):

```mermaid
erDiagram
    UserProfile ||--o{ VerificationDocument : has
    UserProfile {
        String  id               PK
        String  userId           UK
        String  name
        String  email
        String  avatarUrl
        String  bio
        String  role
        Enum    verificationStatus
        Float   rating
        Int     totalRatings
        String  skills[]
        Float   locationLat
        Float   locationLng
        String  locationCity
        Boolean isOnline
        Decimal walletBalance
        DateTime createdAt
        DateTime updatedAt
    }
    VerificationDocument {
        String   id        PK
        String   profileId FK
        String   type
        String   url
        String   status
        DateTime createdAt
    }
```

**Verification Status Enum:** `PENDING` → `VERIFIED` | `REJECTED`

---

## Application Workflows

### 1. 🔑 Registration & Onboarding

```mermaid
sequenceDiagram
    participant U as User
    participant F as Frontend
    participant A as Auth Service
    participant US as User Service
    participant R as Redis

    U->>F: Enter phone number
    F->>A: POST /auth/send-otp
    A->>R: Store OTP (TTL 5min)
    A-->>F: "OTP sent"
    U->>F: Enter 6-digit OTP
    F->>A: POST /auth/verify-otp { phone, otp, role }
    A->>R: Validate OTP
    A->>A: Upsert User record
    A-->>F: { accessToken, refreshToken }
    F->>US: POST /users/profile (create profile)
    US-->>F: Profile created
    F-->>U: Redirect to home
```

### 2. 💼 Job Posting & Matching

```mermaid
sequenceDiagram
    participant E as Employer
    participant F as Frontend
    participant J as Job Service
    participant PS as Pub/Sub
    participant M as Matching Service
    participant N as Notification Service
    participant W as Worker

    E->>F: Fill job form (title, location, budget, skills)
    F->>J: POST /jobs
    J->>PS: Publish job.created event
    J-->>F: Job created (id)
    PS->>M: job.created event received
    M->>M: Geo-radius search (5km) + skill filter
    M-->>PS: Matched workers list
    PS->>N: Trigger notifications
    N-->>W: 🔔 Push notification "New job near you!"
    W->>F: View job on map
    W->>J: POST /jobs/:id/apply
    J->>PS: Publish application.submitted
    PS->>N: Notify employer
    N-->>E: 🔔 "New application received"
```

### 3. 💰 Payment & Wallet Flow

```
Employer tops up wallet
    └─> POST /payments/order (Razorpay)
    └─> Razorpay webhook confirms payment
    └─> Employer walletBalance credited

Employer hires worker
    └─> Funds conceptually escrowed

Job completed & marked done
    └─> Payment Service transfers amount to Worker walletBalance
    └─> Transaction logged in DB
    └─> Worker & Employer notified via FCM
```

---

## Infrastructure & Ports

| Service | Container Name | Host Port | Internal Port |
|---------|---------------|-----------|---------------|
| PostgreSQL | `worknow-postgres` | `5432` | `5432` |
| Redis | `worknow-redis` | `6379` | `6379` |
| Pub/Sub Emulator | `worknow-pubsub` | `8085` | `8085` |
| Auth Service | `worknow-auth` | `3001` | `3000` |
| User Service | `worknow-user` | `3002` | `3000` |
| Job Service | `worknow-job` | `3003` | `3000` |
| Payment Service | `worknow-payment` | `3004` | `3000` |
| Notification Service | `worknow-notification` | `3005` | `3000` |
| Matching Service | `worknow-matching` | `3006` | `3000` |
| Frontend (Next.js) | _(local)_ | `3000` | — |

---

## Environment Variables

### Backend (`.env` in `backend/`)

```env
# PostgreSQL (per service)
DATABASE_URL=postgresql://worknow:worknow@localhost:5432/worknow_<service>

# Redis
REDIS_URL=redis://localhost:6379

# Auth
JWT_SECRET=your-secret-key
JWT_EXPIRY=15m
JWT_REFRESH_EXPIRY=7d
OTP_TTL_SECONDS=300

# GCP Pub/Sub
PUBSUB_EMULATOR_HOST=localhost:8085
GCP_PROJECT_ID=worknow-dev

# Razorpay (Payment Service)
RAZORPAY_KEY_ID=rzp_test_xxx
RAZORPAY_KEY_SECRET=your_secret
RAZORPAY_WEBHOOK_SECRET=webhook_secret

# Firebase (Notification Service)
FCM_PROJECT_ID=your-project
FCM_CLIENT_EMAIL=service-account@project.iam.gserviceaccount.com
FCM_PRIVATE_KEY="-----BEGIN RSA PRIVATE KEY-----\n..."

# SMS
SMS_API_KEY=msg91_api_key
SMS_SENDER_ID=WRKSNW
```

### Frontend (`.env.local` in `frontend/`)

```env
NEXT_PUBLIC_AUTH_SERVICE_URL=http://localhost:3001
NEXT_PUBLIC_USER_SERVICE_URL=http://localhost:3002
NEXT_PUBLIC_JOB_SERVICE_URL=http://localhost:3003
NEXT_PUBLIC_GOOGLE_MAPS_API_KEY=your_google_maps_key
NEXT_PUBLIC_SUPABASE_URL=https://xxx.supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=your_anon_key
```

---

## Getting Started

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

# 2. Install root dependencies
npm install

# 3. Install backend dependencies (all services via workspaces)
cd backend
npm install

# 4. Install frontend dependencies
cd ../frontend
npm install
```

---

## Running the Application

### Step 1 — Start Infrastructure

```bash
cd backend
npm run docker:up
# Starts: PostgreSQL, Redis, Pub/Sub emulator
```

### Step 2 — Run Database Migrations

```bash
# Run migrations for each service
cd backend/services/auth    && npx prisma migrate dev --name init
cd backend/services/user    && npx prisma migrate dev --name init
cd backend/services/job     && npx prisma migrate dev --name init
cd backend/services/payment && npx prisma migrate dev --name init
cd backend/services/notification && npx prisma migrate dev --name init
```

### Step 3 — Start All Backend Services (Dev Mode)

```bash
cd backend
npm run dev
# Turborepo starts all 6 services in parallel
```

### Step 4 — Start Frontend

```bash
cd frontend
npm run dev
# App available at http://localhost:3000
```

### Step 5 — Seed Demo Data (Optional)

```bash
cd backend
npm run seed:dev
```

### Useful Commands

```bash
# View Docker logs
cd backend && npm run docker:logs

# Stop all containers
cd backend && npm run docker:down

# Run all migrations
cd backend && npm run migrate:dev

# Lint all packages
npm run lint

# Type check all packages
npm run typecheck

# Run all tests
npm run test
```

---

## Mobile Access

To access WorkNow on your mobile device during development:

1. Find your PC's IP address:
   ```powershell
   ipconfig
   # Look for IPv4 Address under your Wi-Fi adapter
   ```
2. Ensure your phone is on the **same Wi-Fi network**.
3. Start the frontend with network binding:
   ```bash
   cd frontend
   npx next dev -H 0.0.0.0
   ```
4. Open `http://<YOUR_PC_IP>:3000` in your mobile browser.

---

## API Reference

### Auth Service (`localhost:3001`)

| Method | Endpoint | Body | Description |
|--------|----------|------|-------------|
| `POST` | `/auth/send-otp` | `{ phone, countryCode }` | Send OTP to phone |
| `POST` | `/auth/verify-otp` | `{ phone, otp, role }` | Verify OTP, get tokens |
| `POST` | `/auth/refresh` | `{ refreshToken }` | Refresh access token |
| `GET` | `/health` | — | Health check |

### User Service (`localhost:3002`)

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/users/profile` | Create user profile |
| `GET` | `/users/profile/:id` | Get profile (with docs) |
| `PATCH` | `/users/profile/:id` | Update profile |
| `POST` | `/users/profile/:id/docs` | Upload verification document |
| `GET` | `/health` | Health check |

### Job Service (`localhost:3003`)

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/jobs` | Create a new job/gig |
| `GET` | `/jobs` | List jobs (with filters) |
| `GET` | `/jobs/:id` | Get job details |
| `PATCH` | `/jobs/:id` | Update job |
| `POST` | `/jobs/:id/apply` | Apply to a job |
| `PATCH` | `/jobs/:id/hire/:workerId` | Hire a worker |
| `PATCH` | `/jobs/:id/complete` | Mark job as complete |

### Payment Service (`localhost:3004`)

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/payments/order` | Create Razorpay order |
| `POST` | `/payments/verify` | Verify payment & credit wallet |
| `POST` | `/payments/webhook` | Razorpay webhook handler |
| `GET` | `/payments/transactions` | List transactions |

### Matching Service (`localhost:3006`)

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/matching/jobs` | Get nearby jobs (lat/lng params) |
| `GET` | `/matching/workers/:jobId` | Get matched workers for a job |

---

## Testing

```bash
# Unit tests (all services)
cd backend && npm run test

# CI mode (no watch, coverage)
cd backend && npm run test:ci

# All tests sequentially (safe for CI pipelines)
cd backend && npm run test:all
```

**Testing strategy:**
- **Unit tests** — NestJS services mocked with `jest-mock-extended` for Prisma
- **Integration tests** — Docker-based PostgreSQL + full migration run
- **Contract tests** — OpenAPI schema validation against REST responses

---

## Documentation

| Document | Description |
|----------|-------------|
| [Application Flow](APPLICATION_FLOW.md) | End-to-end user journey diagrams |
| [Install Guide](INSTALL_GUIDE.md) | Step-by-step environment setup |
| [User Service – Prisma Schema](backend/services/user/PRISMA_SCHEMA_DOC.md) | Full DB schema reference, CRUD examples, security notes |

---

## Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/your-feature`
3. Commit your changes: `git commit -m 'feat: add your feature'`
4. Push to the branch: `git push origin feature/your-feature`
5. Open a Pull Request

---

## License

MIT © 2026 WorkNow Team

---

*Built with ❤️ for students who hustle.*
