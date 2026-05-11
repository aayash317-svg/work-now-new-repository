import collections.abc
from pptx import Presentation
from pptx.util import Inches, Pt

def create_presentation():
    prs = Presentation()

    def add_slide(prs, layout_idx, title, content=None):
        slide = prs.slides.add_slide(prs.slide_layouts[layout_idx])
        title_shape = slide.shapes.title
        title_shape.text = title
        if content and len(slide.placeholders) > 1:
            body_shape = slide.placeholders[1]
            tf = body_shape.text_frame
            if isinstance(content, list):
                for i, item in enumerate(content):
                    if i == 0:
                        tf.text = item
                    else:
                        p = tf.add_paragraph()
                        p.text = item
                        p.level = 0
            else:
                tf.text = content
        return slide

    # Slide 1: Title
    title_slide_layout = prs.slide_layouts[0]
    slide = prs.slides.add_slide(title_slide_layout)
    title = slide.shapes.title
    subtitle = slide.placeholders[1]
    title.text = "WorkNow"
    subtitle.text = "Student Gig Marketplace\nFind Work. Find Workers. Instantly."

    # Slide 2: Overview
    add_slide(prs, 1, "Overview", [
        "WorkNow connects students with flexible, short-term local gigs.",
        "Provides small employers a fast way to hire verified student talent.",
        "Worker Role: Browse nearby gigs on a map, apply, complete tasks, get paid.",
        "Employer Role: Post jobs with location & budget, review applicants, hire, pay."
    ])

    # Slide 3: Architecture
    add_slide(prs, 1, "Micro-Service Architecture", [
        "Frontend: Next.js 14 App Router (Mobile & Web experiences).",
        "Backend: Six independently deployable NestJS microservices.",
        "Services: Auth, User, Job, Payment, Matching, Notification.",
        "Communication: Event-driven async via Google Cloud Pub/Sub.",
        "Infrastructure: Docker Compose, Turborepo."
    ])

    # Slide 4: Tech Stack
    add_slide(prs, 1, "Tech Stack", [
        "Frontend: React 18, Tailwind CSS, Google Maps API.",
        "Backend Framework: NestJS, TypeScript.",
        "Database: PostgreSQL 15, Prisma ORM.",
        "Cache/State: Redis 7.",
        "External APIs: Razorpay, Firebase FCM (Push), MSG91 (SMS)."
    ])

    # Slide 5: Workflows - Registration & Verification
    add_slide(prs, 1, "Registration & Verification", [
        "Phone-based OTP Authentication using MSG91 & Redis.",
        "Role Selection at signup: Worker or Employer.",
        "Profile Creation with Skills & Location data.",
        "KYC Verification: Upload Aadhar/Student ID for Admin review."
    ])

    # Slide 6: Workflows - Job Lifecycle
    add_slide(prs, 1, "Job Lifecycle & Matching", [
        "Employer posts job with budget, location, and skills.",
        "Matching Service performs geo-radius search (5km) and skill filtering.",
        "Workers receive push notifications for nearby matched gigs.",
        "Worker applies via map UI, Employer reviews profile and hires.",
        "Upon task completion, Employer marks job as done."
    ])

    # Slide 7: Payment & Wallet
    add_slide(prs, 1, "Payment System", [
        "Integrated Wallet for both Workers and Employers.",
        "Employers top-up via Razorpay payment gateway.",
        "Funds conceptually escrowed upon hiring a worker.",
        "Automated transfer to Worker's wallet on job completion.",
        "Full transaction history logged."
    ])

    # Slide 8: Mobile Experience
    add_slide(prs, 1, "Mobile-First Experience", [
        "Location Awareness: Uses GPS to find gigs in real-time.",
        "Push Notifications: Instant alerts for matches, applications, and payments.",
        "Mobile Wallet: Easy top-ups and balance checks on the go.",
        "Map-first UI using React-Leaflet for gig discovery."
    ])

    prs.save("WorkNow_Presentation.pptx")
    print("Presentation successfully saved as WorkNow_Presentation.pptx")

if __name__ == "__main__":
    create_presentation()
