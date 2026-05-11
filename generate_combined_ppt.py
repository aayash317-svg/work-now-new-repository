import os
from pptx import Presentation
from pptx.util import Inches, Pt, Emu
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN

# ── Image paths ───────────────────────────────────────────────
BRAIN = r"C:\Users\ADMIN\.gemini\antigravity\brain\5522b47a-3523-4326-a85b-d9cbe2103e09"
IMG = {
    "splash":   os.path.join(BRAIN, "splash_screen_1777436870996.png"),
    "map":      os.path.join(BRAIN, "map_ui_1777436943899.png"),
    "wallet":   os.path.join(BRAIN, "wallet_ui_1777436980123.png"),
    "arch":     os.path.join(BRAIN, "architecture_diagram_1777439904300.png"),
    "kyc":      os.path.join(BRAIN, "kyc_verification_1777440055307.png"),
    "otp":      os.path.join(BRAIN, "otp_login_1777440152310.png"),
}

# ── Colour palette ────────────────────────────────────────────
COLORS = [
    RGBColor(0x1A, 0x1A, 0x2E),   # 0 Deep navy  – title
    RGBColor(0x16, 0x21, 0x3E),   # 1 Dark blue   – overview
    RGBColor(0x0F, 0x3D, 0x57),   # 2 Ocean blue  – arch
    RGBColor(0x1B, 0x26, 0x3B),   # 3 Slate blue  – tech stack
    RGBColor(0x2D, 0x00, 0x5E),   # 4 Deep purple – registration
    RGBColor(0x12, 0x3C, 0x29),   # 5 Forest green– worker feat
    RGBColor(0x3D, 0x1A, 0x00),   # 6 Dark amber  – employer feat
    RGBColor(0x1C, 0x1C, 0x1C),   # 7 Charcoal    – workflow 1
    RGBColor(0x1A, 0x00, 0x33),   # 8 Midnight    – workflow 2
    RGBColor(0x00, 0x33, 0x33),   # 9 Deep teal   – workflow 3
    RGBColor(0x1E, 0x3A, 0x5F),   # 10 Royal blue – tech flow
    RGBColor(0x2C, 0x00, 0x3E),   # 11 Violet     – mobile
    RGBColor(0x0D, 0x1B, 0x2A),   # 12 Deep ocean – closing
]

ACCENT = RGBColor(0x00, 0xD4, 0xFF)  # Cyan accent
WHITE  = RGBColor(0xFF, 0xFF, 0xFF)
YELLOW = RGBColor(0xFF, 0xD7, 0x00)

SW, SH = Inches(10), Inches(7.5)   # slide width / height


def set_bg(slide, color: RGBColor):
    bg = slide.background
    fill = bg.fill
    fill.solid()
    fill.fore_color.rgb = color


def add_rect(slide, x, y, w, h, color: RGBColor, alpha=None):
    shape = slide.shapes.add_shape(1, x, y, w, h)
    shape.fill.solid()
    shape.fill.fore_color.rgb = color
    shape.line.fill.background()
    return shape


def txt(frame, text, size, bold=False, color=WHITE, align=PP_ALIGN.LEFT, level=0):
    para = frame.add_paragraph()
    para.alignment = align
    para.level = level
    run = para.add_run()
    run.text = text
    run.font.size = Pt(size)
    run.font.bold = bold
    run.font.color.rgb = color
    return para


def make_title_slide(prs):
    slide = prs.slides.add_slide(prs.slide_layouts[6])  # blank
    set_bg(slide, COLORS[0])

    # Gradient-like accent bar on left
    add_rect(slide, 0, 0, Inches(0.25), SH, ACCENT)
    add_rect(slide, Inches(0.25), 0, Inches(0.08), SH, RGBColor(0x00, 0x90, 0xBB))

    # Splash image on right
    if os.path.exists(IMG["splash"]):
        slide.shapes.add_picture(IMG["splash"], Inches(6.0), Inches(0.5), height=Inches(6.5))

    # Text box
    txBox = slide.shapes.add_textbox(Inches(0.6), Inches(1.5), Inches(5.0), Inches(5.0))
    tf = txBox.text_frame
    tf.word_wrap = True

    p = tf.paragraphs[0]
    p.alignment = PP_ALIGN.LEFT
    r = p.add_run()
    r.text = "WorkNow"
    r.font.size = Pt(54)
    r.font.bold = True
    r.font.color.rgb = ACCENT

    txt(tf, "Student Gig Marketplace", 26, bold=True, color=WHITE)
    txt(tf, "", 10)
    txt(tf, "Find Work.  Find Workers.  Instantly.", 18, color=RGBColor(0xCC, 0xCC, 0xCC))
    txt(tf, "", 10)
    txt(tf, "• Phone OTP Authentication", 14, color=RGBColor(0xAA, 0xDD, 0xFF))
    txt(tf, "• Real-Time Location Matching", 14, color=RGBColor(0xAA, 0xDD, 0xFF))
    txt(tf, "• Integrated Wallet & Payments", 14, color=RGBColor(0xAA, 0xDD, 0xFF))
    txt(tf, "• Push Notifications & KYC", 14, color=RGBColor(0xAA, 0xDD, 0xFF))
    return slide


def make_slide(prs, bg_idx, heading, bullets, img_key=None, accent_color=ACCENT):
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    set_bg(slide, COLORS[bg_idx])

    # Top accent bar
    add_rect(slide, 0, 0, SW, Inches(0.08), accent_color)

    # Heading box
    hbox = slide.shapes.add_textbox(Inches(0.4), Inches(0.15), Inches(9.0), Inches(0.8))
    htf = hbox.text_frame
    p = htf.paragraphs[0]
    r = p.add_run()
    r.text = heading
    r.font.size = Pt(30)
    r.font.bold = True
    r.font.color.rgb = accent_color

    # Determine text area width based on image presence
    img_shown = img_key and img_key in IMG and os.path.exists(IMG[img_key])
    txt_w = Inches(5.6) if img_shown else Inches(9.2)

    # Bullet text box
    bx = slide.shapes.add_textbox(Inches(0.4), Inches(1.1), txt_w, Inches(6.0))
    btf = bx.text_frame
    btf.word_wrap = True
    first = True
    for b in bullets:
        if first:
            p = btf.paragraphs[0]
            p.alignment = PP_ALIGN.LEFT
            r = p.add_run()
            r.text = b
            r.font.size = Pt(16)
            r.font.color.rgb = WHITE
            first = False
        else:
            txt(btf, b, 15, color=RGBColor(0xDD, 0xDD, 0xDD))

    # Image
    if img_shown:
        slide.shapes.add_picture(IMG[img_key], Inches(6.2), Inches(1.0), width=Inches(3.5))

    # Bottom accent line
    add_rect(slide, 0, SH - Inches(0.05), SW, Inches(0.05), accent_color)
    return slide


def build():
    prs = Presentation()
    prs.slide_width  = SW
    prs.slide_height = SH

    # 1. Title
    make_title_slide(prs)

    # 2. Problem Statement
    make_slide(prs, 4, "Problem Statement", [
        "Students need flexible income — but finding safe, quick gigs is hard.",
        "Small employers need verified local help fast — but hiring is slow and risky.",
        "",
        "Current Gaps:",
        "  No platform tailored to short-term, hyperlocal student gigs.",
        "  Existing platforms (Upwork, Fiverr) are designed for long-term remote work.",
        "  No verified identity / KYC for casual workers — safety risk for employers.",
        "  No real-time location-based job matching for offline/on-site gigs.",
        "  Payment disputes are common with no escrow mechanism.",
        "  Students lack a digital work history or rating system to build credibility.",
        "",
        "The Need: A trusted, mobile-first marketplace where students can find",
        "  hyperlocal gigs instantly, and employers can hire with confidence.",
    ], accent_color=RGBColor(0xFF, 0x55, 0x55))

    # 3. Overview
    make_slide(prs, 1, "📌 Overview", [
        "WorkNow connects student freelancers with local short-term gigs.",
        "",
        "👷 Worker (Student)",
        "  • Browse nearby jobs on an interactive map",
        "  • Apply with one tap and track tasks in real-time",
        "  • Get paid directly to an in-app wallet",
        "",
        "🏢 Employer",
        "  • Post gigs with location, budget & required skills",
        "  • Instantly matched with verified students nearby",
        "  • Review applicants, hire, and pay securely",
    ], img_key="splash", accent_color=RGBColor(0x00, 0xD4, 0xFF))

    # 3. Architecture
    make_slide(prs, 2, "🏗️ Micro-Service Architecture", [
        "A production-grade monorepo (Turborepo) with six NestJS microservices.",
        "",
        "  🔐 Auth Service      – OTP login, JWT tokens",
        "  👤 User Service      – Profiles, KYC, wallet balance",
        "  💼 Job Service       – Gig CRUD, lifecycle management",
        "  📍 Matching Service  – Geo-radius + skill-based matching",
        "  💳 Payment Service   – Razorpay wallet & payouts",
        "  🔔 Notification Svc  – FCM push & MSG91 SMS",
        "",
        "Event-driven: Services communicate via GCP Pub/Sub.",
    ], img_key="arch", accent_color=RGBColor(0x00, 0xFF, 0xCC))

    # 4. Tech Stack
    make_slide(prs, 3, "⚙️ Tech Stack", [
        "Frontend:   Next.js 14, React 18, TypeScript, Tailwind CSS",
        "Maps:       React-Leaflet, Google Maps API",
        "Backend:    NestJS, TypeScript (6 microservices)",
        "ORM:        Prisma ORM",
        "Database:   PostgreSQL 15 (one DB per service)",
        "Cache:      Redis 7  (OTPs, geo-locations, sessions)",
        "Messaging:  Google Cloud Pub/Sub (emulated locally)",
        "Payments:   Razorpay  (wallet top-up & payouts)",
        "Push Alerts: Firebase Cloud Messaging (FCM)",
        "SMS:        MSG91  (OTP delivery)",
        "DevOps:     Docker Compose, Turborepo",
    ], accent_color=YELLOW)

    # 5. Registration & Auth
    make_slide(prs, 4, "🔐 Feature: Registration & Authentication", [
        "Phone-based OTP Login — no password required.",
        "",
        "How it works:",
        "  1. User enters phone number → Auth Service calls MSG91.",
        "  2. 6-digit OTP stored in Redis with 5-minute TTL.",
        "  3. User enters OTP → verified → JWT issued.",
        "  4. Role selected: WORKER or EMPLOYER.",
        "",
        "Security:",
        "  • Access Token: 15 min expiry",
        "  • Refresh Token: 7 day expiry",
        "  • OTP brute-force protected via Redis TTL",
    ], img_key="otp", accent_color=RGBColor(0xBB, 0x86, 0xFC))

    # 6. Worker Features
    make_slide(prs, 5, "👷 Feature: Worker (Student) Experience", [
        "Map-Based Discovery: Live job pins on GPS map (5 km radius).",
        "One-Click Apply: Apply to gigs instantly from the map.",
        "Task Tracker: Monitor active & completed gigs.",
        "KYC Verification: Upload Aadhar/Student ID for 'Verified' badge.",
        "Rating System: Build reputation through successful completions.",
        "Digital Wallet: Receive payout directly to in-app balance.",
        "Push Notifications: Instant alert for every new matching job.",
    ], img_key="map", accent_color=RGBColor(0x00, 0xFF, 0x88))

    # 7. Employer Features
    make_slide(prs, 6, "🏢 Feature: Employer Experience", [
        "Rapid Job Posting: Set title, location (Google Places), budget & skills.",
        "Automated Matching: Top 10 nearest verified workers notified instantly.",
        "Applicant Review: View profiles, ratings & KYC status before hiring.",
        "Escrow Payments: Funds secured on hire; released on completion.",
        "Task Dashboard: Track jobs — OPEN → ASSIGNED → COMPLETED.",
        "Transaction History: Full log of all wallet movements.",
        "Push Alerts: Notified on every application received.",
    ], img_key="kyc", accent_color=RGBColor(0xFF, 0x99, 0x00))

    # 8. System Workflow Part 1
    make_slide(prs, 7, "🔄 System Working: Step 1 & 2 – Post & Match", [
        "STEP 1 — Job Creation",
        "  • Employer fills form → Frontend sends POST /jobs",
        "  • Job Service saves to PostgreSQL",
        "  • Publishes 'job.created' event → GCP Pub/Sub",
        "",
        "STEP 2 — Geo-Radius Matching",
        "  • Matching Service receives 'job.created' event",
        "  • Queries Redis for workers within 5 km",
        "  • Filters by skill overlap",
        "  • Returns ranked list of up to 10 workers",
        "  • Notification Service sends FCM push to each worker",
    ], accent_color=RGBColor(0x00, 0xD4, 0xFF))

    # 9. System Workflow Part 2
    make_slide(prs, 8, "🔄 System Working: Step 3 & 4 – Apply & Hire", [
        "STEP 3 — Application",
        "  • Worker receives push → opens app → views job on map",
        "  • Taps 'Apply' → Frontend sends POST /jobs/:id/apply",
        "  • Job Service publishes 'application.submitted' event",
        "  • Employer receives push: 'New applicant received'",
        "",
        "STEP 4 — Hiring",
        "  • Employer reviews applicant profiles & ratings",
        "  • Selects a worker → PATCH /jobs/:id/hire/:workerId",
        "  • Job status → ASSIGNED → IN_PROGRESS",
        "  • Employer wallet balance conceptually escrowed",
    ], accent_color=RGBColor(0xFF, 0x55, 0x99))

    # 10. System Workflow Part 3
    make_slide(prs, 9, "🔄 System Working: Step 5 – Complete & Pay", [
        "STEP 5 — Task Completion & Payout",
        "  • Worker completes task in real life",
        "  • Employer taps 'Mark as Done' → PATCH /jobs/:id/complete",
        "  • Job Service publishes 'job.completed' event",
        "  • Payment Service transfers funds:",
        "       Employer Wallet  ──▶  Worker Wallet",
        "  • Transaction logged in worknow_payment DB",
        "  • Both parties notified via FCM",
        "  • Both prompted to rate each other",
    ], img_key="wallet", accent_color=RGBColor(0x00, 0xFF, 0xCC))

    # 11. Technical Deep Dive
    make_slide(prs, 10, "⚙️ Under the Hood: Technical Flow", [
        "Frontend  →  REST API calls to individual microservices.",
        "Microservices  →  Async events via GCP Pub/Sub topics.",
        "Redis  →  Caches OTPs (TTL), worker locations, sessions.",
        "PostgreSQL  →  Each service owns its own isolated database.",
        "Razorpay Webhooks  →  Securely verify payments before crediting wallet.",
        "Prisma ORM  →  Type-safe DB access with migration support.",
        "Turborepo  →  Parallel builds & dev across all services.",
        "Docker Compose  →  One command to start Postgres, Redis & Pub/Sub.",
    ], accent_color=YELLOW)

    # 12. Mobile Experience
    make_slide(prs, 11, "Mobile-First Experience", [
        "The entire platform is designed mobile-first.",
        "",
        "  GPS Location: Detects user position automatically.",
        "  Map UI: Jobs shown as interactive pins (React-Leaflet).",
        "  Push Alerts: Firebase FCM for real-time notifications.",
        "  SMS OTP: MSG91 for secure phone verification.",
        "  Mobile Wallet: Top-up and check balance on the go.",
        "  LAN Access: Dev server binds to 0.0.0.0 for phone testing.",
    ], img_key="map", accent_color=RGBColor(0xFF, 0x55, 0xFF))

    # 13. Frontend Deep Dive
    make_slide(prs, 1, "Frontend Deep Dive", [
        "Framework: Next.js 14 App Router — React 18, TypeScript",
        "Styling: Tailwind CSS 3 + Material Symbols (icons)",
        "",
        "Pages & Routes:",
        "  /              – Animated splash screen with gradient blobs",
        "  /login         – Phone entry + 6-digit OTP verification",
        "  /worker/home   – Map-based job feed (React-Leaflet + GPS)",
        "  /worker/job    – Job detail view and application form",
        "  /worker/tasks  – Active and completed task history",
        "  /worker/wallet – Earnings, balance & transaction history",
        "  /worker/profile– Profile editor + KYC document upload",
        "  /customer/home – Employer dashboard",
        "  /customer/post-job – Create a new gig (Google Places API)",
        "  /customer/tasks– Manage jobs, review applicants, hire",
        "  /customer/wallet– Top-up wallet, payment history",
        "Auth: NextAuth.js session management + Supabase JS",
    ], img_key="otp", accent_color=RGBColor(0x00, 0xD4, 0xFF))

    # 14. Backend Deep Dive
    make_slide(prs, 2, "Backend Deep Dive", [
        "Framework: NestJS + TypeScript — 6 independent microservices",
        "Each service runs on its own port with its own PostgreSQL DB.",
        "",
        "Auth Service   (port 3001): OTP via MSG91, JWT access+refresh tokens, Redis TTL",
        "User Service   (port 3002): UserProfile, KYC docs (PENDING/VERIFIED/REJECTED), ratings",
        "Job Service    (port 3003): Gig CRUD, status: OPEN->ASSIGNED->IN_PROGRESS->COMPLETED",
        "Matching Svc   (port 3006): Geo-radius (5km) in Redis, skill filter, top-10 worker rank",
        "Payment Svc    (port 3004): Razorpay orders & webhooks, wallet top-up, fund transfers",
        "Notification   (port 3005): Subscribes to Pub/Sub, sends FCM push + MSG91 SMS",
        "",
        "Database: Prisma ORM — type-safe queries + migration support",
        "Messaging: GCP Pub/Sub — job.created / application.submitted / payment.completed",
        "DevOps: Turborepo (parallel builds), Docker Compose (Postgres + Redis + Pub/Sub)",
    ], img_key="arch", accent_color=RGBColor(0x00, 0xFF, 0xCC))

    # 13. Closing
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    set_bg(slide, COLORS[12])
    add_rect(slide, 0, 0, SW, Inches(0.08), ACCENT)
    add_rect(slide, 0, SH - Inches(0.08), SW, Inches(0.08), ACCENT)

    txBox = slide.shapes.add_textbox(Inches(1.0), Inches(1.5), Inches(8.0), Inches(5.0))
    tf = txBox.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.alignment = PP_ALIGN.CENTER
    r = p.add_run()
    r.text = "Thank You"
    r.font.size = Pt(54)
    r.font.bold = True
    r.font.color.rgb = ACCENT

    txt(tf, "", 12)
    txt(tf, "WorkNow — Student Gig Marketplace", 22, bold=True, color=WHITE, align=PP_ALIGN.CENTER)
    txt(tf, "", 10)
    txt(tf, "Built with ❤️ for students who hustle.", 18, color=RGBColor(0xAA, 0xAA, 0xAA), align=PP_ALIGN.CENTER)
    txt(tf, "", 10)
    txt(tf, "Next.js  •  NestJS  •  PostgreSQL  •  Redis  •  Razorpay  •  FCM", 13,
        color=RGBColor(0x88, 0x88, 0x88), align=PP_ALIGN.CENTER)

    out = r"d:\student job\WorkNow_Complete.pptx"
    prs.save(out)
    print(f"Saved: {out}")

if __name__ == "__main__":
    build()
