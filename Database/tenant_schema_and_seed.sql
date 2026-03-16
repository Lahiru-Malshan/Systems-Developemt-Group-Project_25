-- Tenant database schema and seed data for PAMS backend
-- Run this in your MySQL client: source tenant_schema_and_seed.sql

DROP DATABASE IF EXISTS paragon_db;
CREATE DATABASE paragon_db;
USE paragon_db;

-- Roles table
CREATE TABLE roles (
    role_id INT PRIMARY KEY,
    role_name VARCHAR(64) NOT NULL UNIQUE
);

-- Users table
CREATE TABLE users (
    user_id INT AUTO_INCREMENT PRIMARY KEY,
    role_id INT NOT NULL,
    username VARCHAR(100) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    first_name VARCHAR(100),
    last_name VARCHAR(100),
    email VARCHAR(150),
    phone_number VARCHAR(50),
    occupation VARCHAR(100),
    dob DATE,
    lease_start DATE,
    lease_end DATE,
    account_status VARCHAR(50) DEFAULT 'active',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (role_id) REFERENCES roles(role_id) ON DELETE CASCADE
);

CREATE INDEX idx_users_role ON users(role_id);

-- Tenant payments table
CREATE TABLE payments (
    payment_id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    `date` DATE NOT NULL,
    description VARCHAR(255),
    amount DECIMAL(12,2) NOT NULL,
    status ENUM('Pending','Paid','Failed') NOT NULL DEFAULT 'Pending',
    method VARCHAR(80),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
);

-- Tenant maintenance requests table
CREATE TABLE maintenance_requests (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    category VARCHAR(100) NOT NULL,
    description TEXT NOT NULL,
    priority ENUM('Low','Medium','High') NOT NULL DEFAULT 'Medium',
    status ENUM('Pending','In Progress','Completed','Cancelled') NOT NULL DEFAULT 'Pending',
    created_date DATE NOT NULL,
    completed_date DATE,
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
);

-- Tenant notifications table
CREATE TABLE notifications (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    type VARCHAR(50) NOT NULL,
    title VARCHAR(150) NOT NULL,
    msg TEXT NOT NULL,
    `date` DATE NOT NULL DEFAULT CURRENT_DATE,
    unread BOOLEAN NOT NULL DEFAULT TRUE,
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
);

-- Seed data
INSERT INTO roles (role_id, role_name) VALUES
(1, 'Administrator'),
(2, 'Manager'),
(3, 'FrontDeskStaff'),
(4, 'MaintenanceStaff'),
(5, 'FinancialManager'),
(6, 'Tenant');

INSERT INTO users (role_id, username, password_hash, first_name, last_name, email, phone_number, occupation, dob, lease_start, lease_end, account_status)
VALUES
(1, 'admin', '$2b$12$/GkJmIu77DCdjqqKrDruoehigf7l6.u6Cmdou2bCCf3K29QQvPQ9.', 'Admin', 'User', 'admin@pams.com', '0700000001', 'Administrator', '1985-02-20', NULL, NULL, 'active'),
(2, 'manager', '$2b$12$RxrBDxXrSq7ug5wd0YteneiePGjT9JdcJHT0adknykODup7LrwFoC', 'Manager', 'User', 'manager@pams.com', '0700000002', 'Property Manager', '1987-04-05', NULL, NULL, 'active'),
(3, 'frontdesk', '$2b$12$7WaUfiy7SclFrEjE7VxiOeH4BYV8X13w0ljMIjyHx1gbASTdEtpWS', 'Front', 'Desk', 'frontdesk@pams.com', '0700000003', 'Front Desk Staff', '1990-05-10', NULL, NULL, 'active'),
(4, 'maintenance', '$2b$12$.rRGPCNvj6cuHZx1ydCuG.pBoBVRVwF9x3fTf00tFwgs4rAz3/z3q', 'Maintenance', 'Staff', 'maintenance@pams.com', '0700000004', 'Maintenance Staff', '1992-07-12', NULL, NULL, 'active'),
(5, 'finance', '$2b$12$7JvvzZTinZ6qd/i0H0LLserOCIAa50dQ6aLweBJx29aTPQyxzw3o2', 'Finance', 'Manager', 'finance@pams.com', '0700000005', 'Finance Manager', '1989-08-15', NULL, NULL, 'active'),
(6, 'tenant', '$2b$12$PR2HtI7Y6GB6IeSdukDkc.FxSU3cOD5Yl6g82JW7c.UfwELyzgWqm', 'Trung', 'Nguyen', 'truntrun@gmail.com', '07932241664', 'Tenant', '1993-03-10', '2026-01-01', '2027-01-01', 'active');

INSERT INTO payments (user_id, `date`, description, amount, status, method)
VALUES
(6, '2025-10-01', 'Monthly Rent - October', 1200.00, 'Pending', 'Bank Transfer'),
(6, '2025-09-05', 'Monthly Rent - September', 1200.00, 'Paid', 'Card'),
(6, '2025-08-28', 'Water Bill - August', 50.00, 'Paid', 'Card');

INSERT INTO maintenance_requests (user_id, category, description, priority, status, created_date, completed_date)
VALUES
(1, 'Plumbing', 'Kitchen sink leaking', 'High', 'In Progress', '2026-02-15', NULL),
(1, 'Electrical', 'AC Filter Cleaning', 'Low', 'Completed', '2026-01-22', '2026-01-23'),
(1, 'Furniture', 'Broken door handle', 'Medium', 'Pending', '2026-02-10', NULL);

INSERT INTO notifications (user_id, type, title, msg, `date`, unread)
VALUES
(1, 'Security', 'Parking Update', 'New guest parking rules.', '2026-03-12', FALSE),
(1, 'Billing', 'Rent Invoice Generated', 'Your rent invoice for February is ready.', '2026-03-16', TRUE),
(1, 'Maintenance', 'Elevator Repair', 'Elevator maintenance in Block B.', '2026-03-15', TRUE);
