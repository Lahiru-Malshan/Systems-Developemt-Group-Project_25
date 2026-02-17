import bcrypt

# Step 1: Convert password to bytes
password = "admin"
password_bytes = password.encode('utf-8')

# Step 2: Generate salt and hash
salt = bcrypt.gensalt()
hashed_password = bcrypt.hashpw(password_bytes, salt)

print(hashed_password.decode())