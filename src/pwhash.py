import bcrypt


def hash_password(password: str) -> str:
    """Hash a plaintext password and return a utf-8 encoded bcrypt hash string."""
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def verify_password(password: str, hashed_password: str) -> bool:
    """Verify a plaintext password against a stored bcrypt hash."""
    if isinstance(hashed_password, str):
        hashed_password = hashed_password.encode("utf-8")
    return bcrypt.checkpw(password.encode("utf-8"), hashed_password)


if __name__ == "__main__":
    pw = "admin"
    h = hash_password(pw)
    print("example hash:", h)
    print("verify admin:", verify_password("admin", h))
