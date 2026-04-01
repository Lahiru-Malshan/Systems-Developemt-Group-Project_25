/*
Navicat Premium Dump SQL

Source Server         : Local MySQL
Source Server Type    : MySQL
Source Server Version : 90001 (9.0.1)
Source Host           : localhost:3306
Source Schema         : paragon_db

Target Server Type    : MySQL
Target Server Version : 90001 (9.0.1)
File Encoding         : 65001

Date: 18/03/2026 19:18:57
*/

SET NAMES utf8mb4;
SET FOREIGN_KEY_CHECKS = 0;

-- ----------------------------
-- Table structure for administrators
-- ----------------------------
DROP TABLE IF EXISTS `administrators`;
CREATE TABLE `administrators` (
  `admin_id` int NOT NULL AUTO_INCREMENT,
  `user_id` int NOT NULL,
  `location_id` int NOT NULL,
  PRIMARY KEY (`admin_id`),
  KEY `user_id` (`user_id`),
  KEY `location_id` (`location_id`),
  CONSTRAINT `administrators_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `users` (`user_id`),
  CONSTRAINT `administrators_ibfk_2` FOREIGN KEY (`location_id`) REFERENCES `locations` (`location_id`)
) ENGINE=InnoDB AUTO_INCREMENT=5 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- ----------------------------
-- Records of administrators
-- ----------------------------
BEGIN;
INSERT INTO `administrators` (`admin_id`, `user_id`, `location_id`) VALUES (4, 36, 1);
COMMIT;

-- ----------------------------
-- Table structure for broadcasts
-- ----------------------------
DROP TABLE IF EXISTS broadcasts;
CREATE TABLE broadcasts (
    broadcast_id INT NOT NULL AUTO_INCREMENT,
    title VARCHAR(255) NOT NULL,
    content TEXT NOT NULL,
    target_audience VARCHAR(50) NOT NULL DEFAULT 'All', -- All / All Staff / All Residents
    urgency ENUM('Info','Urgent') DEFAULT 'Info',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (broadcast_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

DROP TABLE IF EXISTS broadcast_targets;

BEGIN;
-- Send All
INSERT INTO broadcasts (title, content, target_audience, urgency)
VALUES ('System Maintenance', 'The system will be down from 10 PM to 12 AM', 'All', 'Info');

-- Send All Staffs
INSERT INTO broadcasts (title, content, target_audience, urgency)
VALUES ('Staff Meeting', 'Please join the staff meeting at 3 PM', 'All Staff', 'Urgent');

-- Send tenants
INSERT INTO broadcasts (title, content, target_audience, urgency)
VALUES ('Rent Reminder', 'Please pay your rent before the 5th of each month', 'All Residents', 'Info');

COMMIT;

-- ----------------------------
-- Table structure for apartment_requirements
-- ----------------------------
DROP TABLE IF EXISTS `apartment_requirements`;
CREATE TABLE `apartment_requirements` (
  `requirement_id` int NOT NULL AUTO_INCREMENT,
  `tenant_id` int NOT NULL,
  `bedrooms` int DEFAULT NULL,
  `bathrooms` int DEFAULT NULL,
  `furnished` tinyint(1) DEFAULT NULL,
  `additional_notes` text,
  `max_rent` decimal(10,2) DEFAULT NULL,
  PRIMARY KEY (`requirement_id`),
  KEY `tenant_id` (`tenant_id`),
  CONSTRAINT `apartment_requirements_ibfk_1` FOREIGN KEY (`tenant_id`) REFERENCES `tenants` (`tenant_id`)
) ENGINE=InnoDB AUTO_INCREMENT=5 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- ----------------------------
-- Records of apartment_requirements
-- ----------------------------
BEGIN;
INSERT INTO `apartment_requirements` (`requirement_id`, `tenant_id`, `bedrooms`, `bathrooms`, `furnished`, `additional_notes`, `max_rent`) VALUES (1, 1, 2, 1, 1, 'Near public transport and parking required', NULL);
INSERT INTO `apartment_requirements` (`requirement_id`, `tenant_id`, `bedrooms`, `bathrooms`, `furnished`, `additional_notes`, `max_rent`) VALUES (2, 2, 1, 1, 0, 'Quiet building preferred', NULL);
INSERT INTO `apartment_requirements` (`requirement_id`, `tenant_id`, `bedrooms`, `bathrooms`, `furnished`, `additional_notes`, `max_rent`) VALUES (3, 1, 2, 1, 1, NULL, 1300.00);
INSERT INTO `apartment_requirements` (`requirement_id`, `tenant_id`, `bedrooms`, `bathrooms`, `furnished`, `additional_notes`, `max_rent`) VALUES (4, 2, 1, 1, 0, NULL, 1000.00);
COMMIT;

-- ----------------------------
-- Table structure for apartments
-- ----------------------------
DROP TABLE IF EXISTS `apartments`;
CREATE TABLE `apartments` (
  `apartment_id` int NOT NULL AUTO_INCREMENT,
  `location_id` int NOT NULL,
  `apartment_number` varchar(20) DEFAULT NULL,
  `bedrooms` int DEFAULT NULL,
  `bathrooms` int DEFAULT NULL,
  `rent` decimal(10,2) DEFAULT NULL,
  `status` enum('Available','Occupied','Maintenance') DEFAULT 'Available',
  PRIMARY KEY (`apartment_id`),
  KEY `location_id` (`location_id`),
  CONSTRAINT `apartments_ibfk_1` FOREIGN KEY (`location_id`) REFERENCES `locations` (`location_id`)
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- ----------------------------
-- Records of apartments
-- ----------------------------
BEGIN;
INSERT INTO `apartments` (`apartment_id`, `location_id`, `apartment_number`, `bedrooms`, `bathrooms`, `rent`, `status`) VALUES (1, 1, 'A101', 2, 1, 1200.00, 'Available');
INSERT INTO `apartments` (`apartment_id`, `location_id`, `apartment_number`, `bedrooms`, `bathrooms`, `rent`, `status`) VALUES (2, 1, 'A102', 1, 1, 900.00, 'Occupied');
INSERT INTO `apartments` (`apartment_id`, `location_id`, `apartment_number`, `bedrooms`, `bathrooms`, `rent`, `status`) VALUES (3, 2, 'B201', 3, 2, 1500.00, 'Available');
COMMIT;

-- ----------------------------
-- Table structure for complaints
-- ----------------------------
DROP TABLE IF EXISTS `complaints`;
CREATE TABLE `complaints` (
  `complaint_id` int NOT NULL AUTO_INCREMENT,
  `tenant_id` int NOT NULL,
  `description` text NOT NULL,
  `status` enum('Open','Closed') DEFAULT 'Open',
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`complaint_id`),
  KEY `tenant_id` (`tenant_id`),
  CONSTRAINT `complaints_ibfk_1` FOREIGN KEY (`tenant_id`) REFERENCES `tenants` (`tenant_id`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- ----------------------------
-- Records of complaints
-- ----------------------------
BEGIN;
INSERT INTO `complaints` (`complaint_id`, `tenant_id`, `description`, `status`, `created_at`) VALUES (1, 1, 'Noise from neighbouring apartment late at night', 'Open', '2026-03-17 00:18:06');
COMMIT;

-- ----------------------------
-- Table structure for financial_managers
-- ----------------------------
DROP TABLE IF EXISTS `financial_managers`;
CREATE TABLE `financial_managers` (
  `finance_manager_id` int NOT NULL AUTO_INCREMENT,
  `user_id` int NOT NULL,
  `location_id` int NOT NULL,
  `hire_date` date DEFAULT NULL,
  PRIMARY KEY (`finance_manager_id`),
  KEY `user_id` (`user_id`),
  KEY `location_id` (`location_id`),
  CONSTRAINT `financial_managers_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `users` (`user_id`),
  CONSTRAINT `financial_managers_ibfk_2` FOREIGN KEY (`location_id`) REFERENCES `locations` (`location_id`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- ----------------------------
-- Records of financial_managers
-- ----------------------------
BEGIN;
INSERT INTO `financial_managers` (`finance_manager_id`, `user_id`, `location_id`, `hire_date`) VALUES (1, 40, 1, '2024-02-15');
COMMIT;

-- ----------------------------
-- Table structure for financial_reports
-- ----------------------------
DROP TABLE IF EXISTS `financial_reports`;
CREATE TABLE `financial_reports` (
  `report_id` int NOT NULL AUTO_INCREMENT,
  `generated_by` int NOT NULL,
  `report_type` varchar(50) DEFAULT NULL,
  `period_start` date DEFAULT NULL,
  `period_end` date DEFAULT NULL,
  `generated_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`report_id`),
  KEY `generated_by` (`generated_by`),
  CONSTRAINT `financial_reports_ibfk_1` FOREIGN KEY (`generated_by`) REFERENCES `financial_managers` (`finance_manager_id`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- ----------------------------
-- Records of financial_reports
-- ----------------------------
BEGIN;
INSERT INTO `financial_reports` (`report_id`, `generated_by`, `report_type`, `period_start`, `period_end`, `generated_at`) VALUES (1, 1, 'Monthly Revenue', '2026-03-01', '2026-03-31', '2026-03-17 00:18:23');
COMMIT;

-- ----------------------------
-- Table structure for frontdesk_staff
-- ----------------------------
DROP TABLE IF EXISTS `frontdesk_staff`;
CREATE TABLE `frontdesk_staff` (
  `frontdesk_staff_id` int NOT NULL AUTO_INCREMENT,
  `user_id` int NOT NULL,
  `location_id` int NOT NULL,
  `hire_date` date DEFAULT NULL,
  PRIMARY KEY (`frontdesk_staff_id`),
  KEY `user_id` (`user_id`),
  KEY `location_id` (`location_id`),
  CONSTRAINT `frontdesk_staff_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `users` (`user_id`),
  CONSTRAINT `frontdesk_staff_ibfk_2` FOREIGN KEY (`location_id`) REFERENCES `locations` (`location_id`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- ----------------------------
-- Records of frontdesk_staff
-- ----------------------------
BEGIN;
INSERT INTO `frontdesk_staff` (`frontdesk_staff_id`, `user_id`, `location_id`, `hire_date`) VALUES (1, 38, 1, '2024-03-01');
COMMIT;

-- ----------------------------
-- Table structure for parcels
-- ----------------------------
DROP TABLE IF EXISTS `parcels`;
CREATE TABLE `parcels` (
  `parcel_id` int NOT NULL AUTO_INCREMENT,
  `apartment_id` int NOT NULL,
  `tenant_id` int DEFAULT NULL,
  `logged_by` int DEFAULT NULL,
  `recipient_name` varchar(120) DEFAULT NULL,
  `carrier` varchar(100) NOT NULL,
  `storage_type` enum('Standard','Cold/Food','Fragile/Large') DEFAULT 'Standard',
  `note` text,
  `status` enum('Pending','Picked Up') DEFAULT 'Pending',
  `received_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  `picked_up_at` timestamp NULL DEFAULT NULL,
  PRIMARY KEY (`parcel_id`),
  KEY `apartment_id` (`apartment_id`),
  KEY `tenant_id` (`tenant_id`),
  KEY `logged_by` (`logged_by`),
  CONSTRAINT `parcels_ibfk_1` FOREIGN KEY (`apartment_id`) REFERENCES `apartments` (`apartment_id`),
  CONSTRAINT `parcels_ibfk_tenant` FOREIGN KEY (`tenant_id`) REFERENCES `tenants` (`tenant_id`),
  CONSTRAINT `parcels_ibfk_2` FOREIGN KEY (`logged_by`) REFERENCES `frontdesk_staff` (`frontdesk_staff_id`)
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- ----------------------------
-- Records of parcels
-- ----------------------------
BEGIN;
INSERT INTO `parcels` (`parcel_id`, `apartment_id`, `tenant_id`, `logged_by`, `recipient_name`, `carrier`, `storage_type`, `note`, `status`, `received_at`, `picked_up_at`) VALUES (1, 2, 1, 1, 'C D', 'Amazon', 'Standard', 'Leave at front desk', 'Pending', '2026-03-18 10:30:00', NULL);
INSERT INTO `parcels` (`parcel_id`, `apartment_id`, `tenant_id`, `logged_by`, `recipient_name`, `carrier`, `storage_type`, `note`, `status`, `received_at`, `picked_up_at`) VALUES (2, 1, NULL, 1, 'Emma Clark', 'Deliveroo', 'Cold/Food', 'Keep chilled', 'Picked Up', '2026-03-18 11:45:00', '2026-03-18 12:15:00');
COMMIT;

-- ----------------------------
-- Table structure for invoices
-- ----------------------------
DROP TABLE IF EXISTS `invoices`;
CREATE TABLE `invoices` (
  `invoice_id` int NOT NULL AUTO_INCREMENT,
  `tenant_id` int NOT NULL,
  `lease_id` int NOT NULL,
  `amount` decimal(10,2) NOT NULL,
  `issue_date` date DEFAULT NULL,
  `due_date` date DEFAULT NULL,
  `status` enum('Unpaid','Paid','Late') DEFAULT 'Unpaid',
  PRIMARY KEY (`invoice_id`),
  KEY `tenant_id` (`tenant_id`),
  KEY `lease_id` (`lease_id`),
  CONSTRAINT `invoices_ibfk_1` FOREIGN KEY (`tenant_id`) REFERENCES `tenants` (`tenant_id`),
  CONSTRAINT `invoices_ibfk_2` FOREIGN KEY (`lease_id`) REFERENCES `lease_agreements` (`lease_id`)
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- ----------------------------
-- Records of invoices
-- ----------------------------
BEGIN;
INSERT INTO `invoices` (`invoice_id`, `tenant_id`, `lease_id`, `amount`, `issue_date`, `due_date`, `status`) VALUES (1, 1, 1, 900.00, '2026-03-01', '2026-03-10', 'Paid');
INSERT INTO `invoices` (`invoice_id`, `tenant_id`, `lease_id`, `amount`, `issue_date`, `due_date`, `status`) VALUES (2, 1, 1, 900.00, '2026-03-18', '2026-03-18', 'Paid');
COMMIT;

-- ----------------------------
-- Table structure for lease_agreements
-- ----------------------------
DROP TABLE IF EXISTS `lease_agreements`;
CREATE TABLE `lease_agreements` (
  `lease_id` int NOT NULL AUTO_INCREMENT,
  `tenant_id` int NOT NULL,
  `apartment_id` int NOT NULL,
  `start_date` date NOT NULL,
  `end_date` date NOT NULL,
  `monthly_rent` decimal(10,2) DEFAULT NULL,
  `status` enum('Active','Expired','Terminated') DEFAULT 'Active',
  PRIMARY KEY (`lease_id`),
  KEY `tenant_id` (`tenant_id`),
  KEY `apartment_id` (`apartment_id`),
  CONSTRAINT `lease_agreements_ibfk_1` FOREIGN KEY (`tenant_id`) REFERENCES `tenants` (`tenant_id`),
  CONSTRAINT `lease_agreements_ibfk_2` FOREIGN KEY (`apartment_id`) REFERENCES `apartments` (`apartment_id`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- ----------------------------
-- Records of lease_agreements
-- ----------------------------
BEGIN;
INSERT INTO `lease_agreements` (`lease_id`, `tenant_id`, `apartment_id`, `start_date`, `end_date`, `monthly_rent`, `status`) VALUES (1, 1, 2, '2025-01-01', '2025-12-31', 900.00, 'Active');
COMMIT;

-- ----------------------------
-- Table structure for locations
-- ----------------------------
DROP TABLE IF EXISTS `locations`;
CREATE TABLE `locations` (
  `location_id` int NOT NULL AUTO_INCREMENT,
  `city` varchar(100) NOT NULL,
  `address` varchar(255) DEFAULT NULL,
  PRIMARY KEY (`location_id`)
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- ----------------------------
-- Records of locations
-- ----------------------------
BEGIN;
INSERT INTO `locations` (`location_id`, `city`, `address`) VALUES (1, 'London', '221B Baker Street');
INSERT INTO `locations` (`location_id`, `city`, `address`) VALUES (2, 'Manchester', '15 King Street');
INSERT INTO `locations` (`location_id`, `city`, `address`) VALUES (3, 'Birmingham', '42 Victoria Square');
COMMIT;

-- ----------------------------
-- Table structure for maintenance_requests
-- ----------------------------
DROP TABLE IF EXISTS `maintenance_requests`;
CREATE TABLE `maintenance_requests` (
  `request_id` int NOT NULL AUTO_INCREMENT,
  `tenant_id` int NOT NULL,
  `apartment_id` int NOT NULL,
  `description` text NOT NULL,
  `status` enum('Pending','In Progress','Resolved') DEFAULT 'Pending',
  `reported_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  `assigned_to` int DEFAULT NULL,
  `resolved_at` timestamp NULL DEFAULT NULL,
  PRIMARY KEY (`request_id`),
  KEY `tenant_id` (`tenant_id`),
  KEY `apartment_id` (`apartment_id`),
  KEY `assigned_to` (`assigned_to`),
  CONSTRAINT `maintenance_requests_ibfk_1` FOREIGN KEY (`tenant_id`) REFERENCES `tenants` (`tenant_id`),
  CONSTRAINT `maintenance_requests_ibfk_2` FOREIGN KEY (`apartment_id`) REFERENCES `apartments` (`apartment_id`),
  CONSTRAINT `maintenance_requests_ibfk_3` FOREIGN KEY (`assigned_to`) REFERENCES `maintenance_staff` (`maintenance_staff_id`)
) ENGINE=InnoDB AUTO_INCREMENT=6 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- ----------------------------
-- Records of maintenance_requests
-- ----------------------------
BEGIN;
INSERT INTO `maintenance_requests` (`request_id`, `tenant_id`, `apartment_id`, `description`, `status`, `reported_at`, `assigned_to`, `resolved_at`) VALUES (2, 1, 2, 'Leaking sink in kitchen', 'Pending', '2026-03-17 00:17:55', 1, NULL);
INSERT INTO `maintenance_requests` (`request_id`, `tenant_id`, `apartment_id`, `description`, `status`, `reported_at`, `assigned_to`, `resolved_at`) VALUES (3, 2, 1, 'fixing light pub', 'Pending', '2026-03-18 17:39:59', NULL, NULL);
INSERT INTO `maintenance_requests` (`request_id`, `tenant_id`, `apartment_id`, `description`, `status`, `reported_at`, `assigned_to`, `resolved_at`) VALUES (4, 1, 2, 'Leaky sink', 'Pending', '2026-03-18 17:46:01', NULL, NULL);
INSERT INTO `maintenance_requests` (`request_id`, `tenant_id`, `apartment_id`, `description`, `status`, `reported_at`, `assigned_to`, `resolved_at`) VALUES (5, 1, 1, 'testing maintenance queue', 'Pending', '2026-03-18 17:58:46', NULL, NULL);
COMMIT;

-- ----------------------------
-- Table structure for maintenance_staff
-- ----------------------------
DROP TABLE IF EXISTS `maintenance_staff`;
CREATE TABLE `maintenance_staff` (
  `maintenance_staff_id` int NOT NULL AUTO_INCREMENT,
  `user_id` int NOT NULL,
  `location_id` int NOT NULL,
  `hire_date` date DEFAULT NULL,
  PRIMARY KEY (`maintenance_staff_id`),
  KEY `user_id` (`user_id`),
  KEY `location_id` (`location_id`),
  CONSTRAINT `maintenance_staff_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `users` (`user_id`),
  CONSTRAINT `maintenance_staff_ibfk_2` FOREIGN KEY (`location_id`) REFERENCES `locations` (`location_id`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- ----------------------------
-- Records of maintenance_staff
-- ----------------------------
BEGIN;
INSERT INTO `maintenance_staff` (`maintenance_staff_id`, `user_id`, `location_id`, `hire_date`) VALUES (1, 39, 1, '2024-01-10');
COMMIT;

-- ----------------------------
-- Table structure for managers
-- ----------------------------
DROP TABLE IF EXISTS `managers`;
CREATE TABLE `managers` (
  `manager_id` int NOT NULL AUTO_INCREMENT,
  `user_id` int NOT NULL,
  `location_id` int NOT NULL,
  PRIMARY KEY (`manager_id`),
  KEY `user_id` (`user_id`),
  KEY `location_id` (`location_id`),
  CONSTRAINT `managers_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `users` (`user_id`),
  CONSTRAINT `managers_ibfk_2` FOREIGN KEY (`location_id`) REFERENCES `locations` (`location_id`)
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- ----------------------------
-- Records of managers
-- ----------------------------
BEGIN;
INSERT INTO `managers` (`manager_id`, `user_id`, `location_id`) VALUES (2, 37, 1);
COMMIT;

-- ----------------------------
-- Table structure for payments
-- ----------------------------
DROP TABLE IF EXISTS `payments`;
CREATE TABLE `payments` (
  `payment_id` int NOT NULL AUTO_INCREMENT,
  `invoice_id` int NOT NULL,
  `processed_by` int NOT NULL,
  `amount` decimal(10,2) NOT NULL,
  `payment_date` date DEFAULT NULL,
  `method` varchar(50) DEFAULT NULL,
  `tenant_id` int DEFAULT NULL,
  `description` varchar(255) DEFAULT NULL,
  `status` enum('Pending','Paid','Failed') DEFAULT 'Paid',
  PRIMARY KEY (`payment_id`),
  KEY `invoice_id` (`invoice_id`),
  KEY `processed_by` (`processed_by`),
  CONSTRAINT `payments_ibfk_1` FOREIGN KEY (`invoice_id`) REFERENCES `invoices` (`invoice_id`),
  CONSTRAINT `payments_ibfk_2` FOREIGN KEY (`processed_by`) REFERENCES `financial_managers` (`finance_manager_id`)
) ENGINE=InnoDB AUTO_INCREMENT=18 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- ----------------------------
-- Records of payments
-- ----------------------------
BEGIN;
INSERT INTO `payments` (`payment_id`, `invoice_id`, `processed_by`, `amount`, `payment_date`, `method`, `tenant_id`, `description`, `status`) VALUES (1, 1, 1, 900.00, '2026-03-05', 'Bank Transfer', 1, NULL, 'Paid');
INSERT INTO `payments` (`payment_id`, `invoice_id`, `processed_by`, `amount`, `payment_date`, `method`, `tenant_id`, `description`, `status`) VALUES (3, 1, 1, 100.00, '2026-03-18', 'Card', 1, 'Test payment by tenant1', 'Paid');
INSERT INTO `payments` (`payment_id`, `invoice_id`, `processed_by`, `amount`, `payment_date`, `method`, `tenant_id`, `description`, `status`) VALUES (6, 2, 1, 100.00, '2026-03-18', 'TestPay', 1, 'Test payment for invoice', 'Paid');
INSERT INTO `payments` (`payment_id`, `invoice_id`, `processed_by`, `amount`, `payment_date`, `method`, `tenant_id`, `description`, `status`) VALUES (7, 2, 1, 200.00, '2026-03-18', 'PayPal', 1, 'Payment via PayPal', 'Paid');
INSERT INTO `payments` (`payment_id`, `invoice_id`, `processed_by`, `amount`, `payment_date`, `method`, `tenant_id`, `description`, `status`) VALUES (17, 2, 1, 900.00, '2026-03-18', 'Visa / Mastercard', 1, 'Payment on invoice 2', 'Paid');
COMMIT;

-- ----------------------------
-- Table structure for roles
-- ----------------------------
DROP TABLE IF EXISTS `roles`;
CREATE TABLE `roles` (
  `role_id` int NOT NULL AUTO_INCREMENT,
  `role_name` varchar(50) NOT NULL,
  PRIMARY KEY (`role_id`),
  UNIQUE KEY `role_name` (`role_name`)
) ENGINE=InnoDB AUTO_INCREMENT=7 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- ----------------------------
-- Records of roles
-- ----------------------------
BEGIN;
INSERT INTO `roles` (`role_id`, `role_name`) VALUES (1, 'Administrator');
INSERT INTO `roles` (`role_id`, `role_name`) VALUES (5, 'FinancialManager');
INSERT INTO `roles` (`role_id`, `role_name`) VALUES (3, 'FrontDeskStaff');
INSERT INTO `roles` (`role_id`, `role_name`) VALUES (4, 'MaintenanceStaff');
INSERT INTO `roles` (`role_id`, `role_name`) VALUES (2, 'Manager');
INSERT INTO `roles` (`role_id`, `role_name`) VALUES (6, 'Tenant');
COMMIT;

-- ----------------------------
-- Table structure for tenant_references
-- ----------------------------
DROP TABLE IF EXISTS `tenant_references`;
CREATE TABLE `tenant_references` (
  `reference_id` int NOT NULL AUTO_INCREMENT,
  `tenant_id` int NOT NULL,
  `reference_name` varchar(100) NOT NULL,
  `relationship_type` varchar(50) DEFAULT NULL,
  `phone_number` varchar(20) DEFAULT NULL,
  `email` varchar(100) DEFAULT NULL,
  PRIMARY KEY (`reference_id`),
  KEY `tenant_id` (`tenant_id`),
  CONSTRAINT `tenant_references_ibfk_1` FOREIGN KEY (`tenant_id`) REFERENCES `tenants` (`tenant_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- ----------------------------
-- Records of tenant_references
-- ----------------------------
BEGIN;
COMMIT;

-- ----------------------------
-- Table structure for tenants
-- ----------------------------
DROP TABLE IF EXISTS `tenants`;
CREATE TABLE `tenants` (
  `tenant_id` int NOT NULL AUTO_INCREMENT,
  `user_id` int NOT NULL,
  `ni_number` varchar(20) NOT NULL,
  `occupation` varchar(100) DEFAULT NULL,
  PRIMARY KEY (`tenant_id`),
  UNIQUE KEY `ni_number` (`ni_number`),
  KEY `user_id` (`user_id`),
  CONSTRAINT `tenants_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `users` (`user_id`)
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- ----------------------------
-- Records of tenants
-- ----------------------------
BEGIN;
INSERT INTO `tenants` (`tenant_id`, `user_id`, `ni_number`, `occupation`) VALUES (1, 35, 'NI123456A', 'Software Engineer');
INSERT INTO `tenants` (`tenant_id`, `user_id`, `ni_number`, `occupation`) VALUES (2, 42, 'NI987654B', 'Teacher');
COMMIT;

-- ----------------------------
-- Table structure for users
-- ----------------------------
DROP TABLE IF EXISTS `users`;
CREATE TABLE `users` (
  `user_id` int NOT NULL AUTO_INCREMENT,
  `role_id` int NOT NULL,
  `username` varchar(50) NOT NULL,
  `password_hash` varchar(255) NOT NULL,
  `first_name` varchar(50) NOT NULL,
  `last_name` varchar(50) NOT NULL,
  `email` varchar(100) NOT NULL,
  `phone_number` varchar(20) DEFAULT NULL,
  `account_status` enum('Active','Inactive') DEFAULT 'Active',
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  `nickname` varchar(50) DEFAULT NULL,
  `dob` varchar(20) DEFAULT NULL,
  PRIMARY KEY (`user_id`),
  UNIQUE KEY `username` (`username`),
  UNIQUE KEY `email` (`email`),
  KEY `role_id` (`role_id`),
  CONSTRAINT `users_ibfk_1` FOREIGN KEY (`role_id`) REFERENCES `roles` (`role_id`)
) ENGINE=InnoDB AUTO_INCREMENT=43 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- ----------------------------
-- Records of users
-- ----------------------------
BEGIN;
INSERT INTO `users` (`user_id`, `role_id`, `username`, `password_hash`, `first_name`, `last_name`, `email`, `phone_number`, `account_status`, `created_at`, `nickname`, `dob`) VALUES (33, 6, 'test_user2', '$2b$12$Szk2X3RPCJD3UXQNC682nenJbNKcaY8OHkHCJc.IGhJ7xBgip0Tni', 'Test', 'User', 'test2@example.com', NULL, 'Active', '2026-03-16 23:58:24', NULL, NULL);
INSERT INTO `users` (`user_id`, `role_id`, `username`, `password_hash`, `first_name`, `last_name`, `email`, `phone_number`, `account_status`, `created_at`, `nickname`, `dob`) VALUES (34, 1, 'admin', '$2b$12$MwsiV3mlNgALVX445RdeGeDQXA4WOK4MBqZQGoJEy7YHIXBKgBb7K', 'A', 'B', 'a@b.c', NULL, 'Active', '2026-03-16 23:59:20', NULL, NULL);
INSERT INTO `users` (`user_id`, `role_id`, `username`, `password_hash`, `first_name`, `last_name`, `email`, `phone_number`, `account_status`, `created_at`, `nickname`, `dob`) VALUES (35, 6, 'tenant', '$2b$12$72IjhjLYN/2Oxp6EGaSgwOJpY.irGNEJBsZQFJgqChnD3cc3V/3Lu', 'C', 'D', 'x@y.com', '123', 'Active', '2026-03-16 23:59:20', 'NewNick', '1990-01-01');
INSERT INTO `users` (`user_id`, `role_id`, `username`, `password_hash`, `first_name`, `last_name`, `email`, `phone_number`, `account_status`, `created_at`, `nickname`, `dob`) VALUES (36, 1, 'admin1', 'hash_admin', 'John', 'Smith', 'admin1@email.com', '0700000001', 'Active', '2026-03-17 00:10:28', NULL, NULL);
INSERT INTO `users` (`user_id`, `role_id`, `username`, `password_hash`, `first_name`, `last_name`, `email`, `phone_number`, `account_status`, `created_at`, `nickname`, `dob`) VALUES (37, 2, 'manager1', 'hash_manager', 'Alice', 'Brown', 'manager@email.com', '0700000002', 'Active', '2026-03-17 00:10:28', NULL, NULL);
INSERT INTO `users` (`user_id`, `role_id`, `username`, `password_hash`, `first_name`, `last_name`, `email`, `phone_number`, `account_status`, `created_at`, `nickname`, `dob`) VALUES (38, 3, 'frontdesk1', 'hash_fd', 'Mark', 'Lee', 'frontdesk@email.com', '0700000003', 'Active', '2026-03-17 00:10:28', NULL, NULL);
INSERT INTO `users` (`user_id`, `role_id`, `username`, `password_hash`, `first_name`, `last_name`, `email`, `phone_number`, `account_status`, `created_at`, `nickname`, `dob`) VALUES (39, 4, 'maint1', 'hash_maint', 'Bob', 'Taylor', 'maint@email.com', '0700000004', 'Active', '2026-03-17 00:10:28', NULL, NULL);
INSERT INTO `users` (`user_id`, `role_id`, `username`, `password_hash`, `first_name`, `last_name`, `email`, `phone_number`, `account_status`, `created_at`, `nickname`, `dob`) VALUES (40, 5, 'finance1', 'hash_finance', 'Sarah', 'White', 'finance@email.com', '0700000005', 'Active', '2026-03-17 00:10:28', NULL, NULL);
INSERT INTO `users` (`user_id`, `role_id`, `username`, `password_hash`, `first_name`, `last_name`, `email`, `phone_number`, `account_status`, `created_at`, `nickname`, `dob`) VALUES (41, 6, 'tenant1', 'hash_tenant', 'David', 'Green', 'tenant@email.com', '0700000006', 'Active', '2026-03-17 00:10:28', NULL, NULL);

COMMIT;

SET FOREIGN_KEY_CHECKS = 1;
