INSERT INTO users (role_id, username, password_hash, first_name, last_name, email, phone_number, account_status, created_at)
VALUES
(1, 'admin', '$2b$12$KveFLsiJrm.q6aqOgIPz1Oc3Zk2NIN06VmgQ7S1W2Q2u2zpbuKo4C', 'Admin', 'User', 'admin@pams.com', '0700000001', 'active', CURRENT_TIMESTAMP),
(2, 'manager', '$2b$12$RxrBDxXrSq7ug5wd0YteneiePGjT9JdcJHT0adknykODup7LrwFoC', 'Manager', 'User', 'manager@pams.com', '0700000002', 'active', CURRENT_TIMESTAMP),
(3, 'frontdesk', '$2b$12$7WaUfiy7SclFrEjE7VxiOeH4BYV8X13w0ljMIjyHx1gbASTdEtpWS', 'Front', 'Desk', 'frontdesk@pams.com', '0700000003', 'active', CURRENT_TIMESTAMP),
(4, 'maintenance', '$2b$12$.rRGPCNvj6cuHZx1ydCuG.pBoBVRVwF9x3fTf00tFwgs4rAz3/z3q', 'Maintenance', 'Staff', 'maintenance@pams.com', '0700000004', 'active', CURRENT_TIMESTAMP),
(5, 'finance', '$2b$12$7JvvzZTinZ6qd/i0H0LLserOCIAa50dQ6aLweBJx29aTPQyxzw3o2', 'Finance', 'Manager', 'finance@pams.com', '0700000005', 'active', CURRENT_TIMESTAMP),
(6, 'tenant', '$2b$12$PR2HtI7Y6GB6IeSdukDkc.FxSU3cOD5Yl6g82JW7c.UfwELyzgWqm', 'Trung', 'Nguyen', 'truntrun@gmail.com', '07932241664', 'active', CURRENT_TIMESTAMP);
