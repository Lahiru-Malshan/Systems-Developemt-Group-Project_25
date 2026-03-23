INSERT INTO users (
    role_id,
    username,
    password_hash,
    first_name,
    last_name,
    email,
    phone_number,
    account_status,
    created_at
) VALUES (
    6,
    'tenant',
    '$2b$12$eOT.70HtE85n6zJ7kG.0b.uN8zMwGxP9E23bRf22kkRvemrvAnMd.',  -- Replace with bcrypt hashed password
    'Trung',
    'Nguyen',
    'truntrun@gmail.com',
    '07932241664',
    'active',
    CURRENT_TIMESTAMP
);