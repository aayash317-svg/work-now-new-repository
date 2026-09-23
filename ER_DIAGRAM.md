# Entity-Relationship (ER) Diagram - WorkNow

This document defines the schema structure and relationships for the WorkNow MySQL database.

![ER Diagram (Visual Model)](file:///d:/Downloads/work-now-new-repository-main/er_diagram.png)

## Database Schema Model (Mermaid Diagram)

```mermaid
erDiagram
    users ||--o{ verification_documents : "uploads"
    users ||--o{ jobs : "posts (employer)"
    users ||--o{ jobs : "accepts (worker)"
    users ||--o{ applications : "submits (worker)"
    users ||--o{ transactions : "performs"
    users ||--o{ reviews : "writes (reviewer)"
    users ||--o{ reviews : "receives (reviewee)"
    jobs ||--o{ applications : "has"
    jobs ||--o{ reviews : "linked_to"

    users {
        int id PK
        string phone "UNIQUE, NULLABLE"
        string password_hash "NULLABLE"
        string auth_provider "PHONE | EMAIL | GOOGLE | GITHUB"
        string provider_id "NULLABLE"
        string role "WORKER | CUSTOMER | ADMIN"
        string name
        string email
        string avatar_url
        text bio
        string verification_status "PENDING | VERIFIED | REJECTED"
        float rating
        int total_ratings
        text skills "Comma-separated string"
        float location_lat
        float location_lng
        string location_city
        boolean is_online
        decimal wallet_balance "Numeric(10,2)"
        datetime created_at
    }

    verification_documents {
        int id PK
        int user_id FK
        string type "AADHAR | PAN | STUDENT_ID | SELFIE"
        string url
        string status "PENDING | VERIFIED | REJECTED"
        datetime created_at
    }

    jobs {
        int id PK
        int employer_id FK
        int worker_id FK "nullable"
        string title
        text description
        string category "Delivery | Cleaning | Helper | Tutoring | Gardening | Office"
        decimal budget "Numeric(10,2)"
        float location_lat
        float location_lng
        string location_city
        string date_time
        string status "OPEN | ASSIGNED | IN_PROGRESS | COMPLETED | CANCELLED"
        string skills_required
        datetime created_at
    }

    applications {
        int id PK
        int job_id FK
        int worker_id FK
        string status "PENDING | HIRED | REJECTED"
        text cover_letter
        datetime created_at
    }

    transactions {
        int id PK
        int user_id FK
        decimal amount "Numeric(10,2)"
        string type "CREDIT | DEBIT"
        string description
        datetime created_at
    }

    reviews {
        int id PK
        int job_id FK
        int reviewer_id FK
        int reviewee_id FK
        int rating "1 to 5"
        text comment
        datetime created_at
    }
```

---

## Table Descriptions

### 1. `users` Table
Stores authentication details and profiles of both employers (Customers) and gig workers (Students).
- `role`: Distinguishes user access control between employer dashboard and student work feed.
- `verification_status`: Determines if a worker has been vetted by an admin to start accepting gigs.
- `wallet_balance`: Used to book escrows for jobs and receive job payouts.

### 2. `verification_documents` Table
Holds the verification documents uploaded by students. 
- Relationships: Linked to `users.id` (Many-to-One).

### 3. `jobs` Table
Stores posted gig requests.
- `employer_id`: Identifies the creator of the gig.
- `worker_id`: Identifies the hired student worker (null when open).
- `status`: Drives the task lifecycle progression (OPEN → ASSIGNED → IN_PROGRESS → COMPLETED).

### 4. `applications` Table
Connects student applications to jobs they are interested in.
- Relationships: Linked to `jobs.id` and `users.id`.

### 5. `transactions` Table
Audits movements of wallet funds (top-ups, escrow holds, job payouts, bank withdrawals).
- Relationships: Linked to `users.id`.

### 6. `reviews` Table
Stores peer-to-peer feedback left after gig completion.
- Relationships: Linked to `jobs.id`, reviewer `users.id`, and reviewee `users.id`.
