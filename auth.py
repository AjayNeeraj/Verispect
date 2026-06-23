"""
auth.py — JWT creation/validation and password hashing.
"""

import os
from datetime import datetime, timedelta
from typing import Optional

import bcrypt
from jose import JWTError, jwt
from fastapi import HTTPException, Request

try:
    from dotenv import load_dotenv
    load_dotenv()
except Exception:
    pass

# ── Config ────────────────────────────────────────────────────────────────────
_INSECURE_DEFAULT = "change-this-in-production-use-a-long-random-string"
JWT_SECRET = os.getenv("JWT_SECRET", "")
if not JWT_SECRET or JWT_SECRET == _INSECURE_DEFAULT:
    raise RuntimeError(
        "JWT_SECRET is not set (or is the insecure placeholder). Refusing to start with a "
        "guessable token-signing key — anyone reading the repo could forge auth tokens. "
        "Set JWT_SECRET to a long random value, e.g.  export JWT_SECRET=$(openssl rand -hex 32)"
    )
JWT_ALGORITHM = "HS256"
JWT_EXPIRE_DAYS = 30   # tokens last 30 days — dashboard sessions persist

# ── Password (bcrypt directly — passlib is unmaintained and breaks with bcrypt>=4.1)

def hash_password(plain: str) -> str:
    # bcrypt operates on max 72 bytes; truncate consistently in hash AND verify
    return bcrypt.hashpw(plain.encode("utf-8")[:72], bcrypt.gensalt()).decode("utf-8")


def verify_password(plain: str, hashed: str) -> bool:
    try:
        return bcrypt.checkpw(plain.encode("utf-8")[:72], hashed.encode("utf-8"))
    except ValueError:
        return False


# ── JWT ───────────────────────────────────────────────────────────────────────

def create_token(client_id: str) -> str:
    payload = {
        "sub": client_id,
        "exp": datetime.utcnow() + timedelta(days=JWT_EXPIRE_DAYS),
        "iat": datetime.utcnow(),
    }
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)


def decode_token(token: str) -> Optional[str]:
    """Returns client_id or None if token is invalid/expired."""
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        return payload.get("sub")
    except JWTError:
        return None


# ── FastAPI dependency ────────────────────────────────────────────────────────

async def require_auth(request: Request) -> str:
    """
    FastAPI dependency. Extracts and validates JWT from Authorization header.
    Returns client_id. Raises 401 if missing or invalid.
    """
    auth_header = request.headers.get("Authorization", "")
    if not auth_header.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing or invalid Authorization header")

    token = auth_header[len("Bearer "):]
    client_id = decode_token(token)
    if not client_id:
        raise HTTPException(status_code=401, detail="Token expired or invalid")

    return client_id
