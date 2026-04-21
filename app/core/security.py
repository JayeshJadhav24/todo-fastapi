"""
core/security.py — Security utilities (skeleton for future use).

Currently this project has no authentication, but this file shows WHERE
you would add it when the time comes.

Future features to add here:
  • Password hashing   (passlib + bcrypt)
  • JWT token creation (python-jose)
  • Token verification

Beginner Note:
  Never store plain-text passwords in the database.
  Use bcrypt or argon2 hashing instead.
  JWTs (JSON Web Tokens) are the standard way to authenticate API requests.
"""

# --------------------------------------------------------------------------- #
# Placeholder — add `pip install passlib[bcrypt] python-jose[cryptography]`
# when you're ready to implement authentication.
# --------------------------------------------------------------------------- #

# Example (uncomment when ready):
#
# from datetime import datetime, timedelta, timezone
# from passlib.context import CryptContext
# from jose import jwt
# from app.core.config import settings
#
# pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
#
# def hash_password(plain: str) -> str:
#     return pwd_context.hash(plain)
#
# def verify_password(plain: str, hashed: str) -> bool:
#     return pwd_context.verify(plain, hashed)
#
# def create_access_token(subject: str) -> str:
#     expire = datetime.now(timezone.utc) + timedelta(minutes=30)
#     payload = {"sub": subject, "exp": expire}
#     return jwt.encode(payload, settings.SECRET_KEY, algorithm="HS256")
