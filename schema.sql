-- ==========================================
-- WorkNow Student Gig Marketplace SQL Schema
-- Compatible with MySQL 8.0+
-- ==========================================

-- 1. Create Database
CREATE DATABASE IF NOT EXISTS worknow;
USE worknow;

-- 2. Drop existing tables if they exist (dependencies order)
DROP TABLE IF EXISTS reviews;
DROP TABLE IF EXISTS transactions;
DROP TABLE IF EXISTS applications;
DROP TABLE IF EXISTS jobs;
DROP TABLE IF EXISTS verification_documents;
DROP TABLE IF EXISTS users;

-- 3. Create Users Table
CREATE TABLE users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    phone VARCHAR(20) NULL UNIQUE,
    password_hash VARCHAR(255) NULL,
    auth_provider VARCHAR(50) NOT NULL DEFAULT 'PHONE', -- 'PHONE', 'EMAIL', 'GOOGLE', 'GITHUB'
    provider_id VARCHAR(255) NULL,
    role VARCHAR(20) NOT NULL DEFAULT 'WORKER', -- 'WORKER', 'CUSTOMER', 'ADMIN'
    name VARCHAR(100) NULL,
    email VARCHAR(100) NULL,
    avatar_url VARCHAR(500) NULL,
    bio TEXT NULL,
    verification_status VARCHAR(20) NOT NULL DEFAULT 'PENDING', -- 'PENDING', 'VERIFIED', 'REJECTED'
    rating FLOAT NOT NULL DEFAULT 0.0,
    total_ratings INT NOT NULL DEFAULT 0,
    skills TEXT NULL, -- Comma-separated list of skills
    location_lat DOUBLE NULL,
    location_lng DOUBLE NULL,
    location_city VARCHAR(100) NULL,
    is_online BOOLEAN NOT NULL DEFAULT FALSE,
    wallet_balance DECIMAL(10, 2) NOT NULL DEFAULT 0.00,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 4. Create Verification Documents Table (Worker KYC)
CREATE TABLE verification_documents (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    type VARCHAR(50) NOT NULL, -- 'AADHAR', 'PAN', 'STUDENT_ID', 'SELFIE'
    url VARCHAR(500) NOT NULL,
    status VARCHAR(20) NOT NULL DEFAULT 'PENDING', -- 'PENDING', 'VERIFIED', 'REJECTED'
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_document_user FOREIGN KEY (user_id) 
        REFERENCES users (id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 5. Create Jobs Table (Gig Postings)
CREATE TABLE jobs (
    id INT AUTO_INCREMENT PRIMARY KEY,
    employer_id INT NOT NULL,
    worker_id INT NULL, -- Hired worker
    title VARCHAR(150) NOT NULL,
    description TEXT NOT NULL,
    category VARCHAR(50) NOT NULL, -- 'Delivery', 'Cleaning', 'Helper', 'Tutoring', 'Gardening', 'Office'
    budget DECIMAL(10, 2) NOT NULL,
    location_lat DOUBLE NOT NULL,
    location_lng DOUBLE NOT NULL,
    location_city VARCHAR(100) NULL,
    date_time VARCHAR(100) NULL, -- 'ASAP', scheduled date
    status VARCHAR(25) NOT NULL DEFAULT 'OPEN', -- 'OPEN', 'ASSIGNED', 'IN_PROGRESS', 'COMPLETED', 'CANCELLED'
    skills_required VARCHAR(200) NULL, -- Comma-separated list of required skills
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_job_employer FOREIGN KEY (employer_id) 
        REFERENCES users (id) ON DELETE CASCADE,
    CONSTRAINT fk_job_worker FOREIGN KEY (worker_id) 
        REFERENCES users (id) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 6. Create Job Applications Table
CREATE TABLE applications (
    id INT AUTO_INCREMENT PRIMARY KEY,
    job_id INT NOT NULL,
    worker_id INT NOT NULL,
    status VARCHAR(20) NOT NULL DEFAULT 'PENDING', -- 'PENDING', 'HIRED', 'REJECTED'
    cover_letter TEXT NULL,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_application_job FOREIGN KEY (job_id) 
        REFERENCES jobs (id) ON DELETE CASCADE,
    CONSTRAINT fk_application_worker FOREIGN KEY (worker_id) 
        REFERENCES users (id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 7. Create Wallet Transactions Table
CREATE TABLE transactions (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    amount DECIMAL(10, 2) NOT NULL,
    type VARCHAR(20) NOT NULL, -- 'CREDIT', 'DEBIT'
    description VARCHAR(255) NOT NULL,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_transaction_user FOREIGN KEY (user_id) 
        REFERENCES users (id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 8. Create Reviews Table (Peer Feedback)
CREATE TABLE reviews (
    id INT AUTO_INCREMENT PRIMARY KEY,
    job_id INT NOT NULL,
    reviewer_id INT NOT NULL,
    reviewee_id INT NOT NULL,
    rating INT NOT NULL, -- 1 to 5 stars
    comment TEXT NULL,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_review_job FOREIGN KEY (job_id) 
        REFERENCES jobs (id) ON DELETE CASCADE,
    CONSTRAINT fk_review_reviewer FOREIGN KEY (reviewer_id) 
        REFERENCES users (id) ON DELETE CASCADE,
    CONSTRAINT fk_review_reviewee FOREIGN KEY (reviewee_id) 
        REFERENCES users (id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 9. Insert default Admin user helper for testing
INSERT INTO users (phone, role, name, verification_status, wallet_balance) 
VALUES ('9999999999', 'ADMIN', 'WorkNow Admin Sandbox', 'VERIFIED', 1000.00);

-- Print success confirmation
SELECT 'WorkNow Database Schema successfully created!' AS Status;
