from datetime import datetime, timedelta, timezone
from typing import Any

import bcrypt as _bcrypt
from cryptography.fernet import Fernet
from jose import jwt

from app.core.config import settings


# ── Password hashing ───────────────────────────────────────────────────────────

def hash_password(plain: str) -> str:
    return _bcrypt.hashpw(plain.encode(), _bcrypt.gensalt()).decode()


def verify_password(plain: str, hashed: str) -> bool:
    return _bcrypt.checkpw(plain.encode(), hashed.encode())


# ── JWT ────────────────────────────────────────────────────────────────────────

def create_access_token(data: dict[str, Any]) -> str:
    payload = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(hours=settings.JWT_EXPIRE_HOURS)
    payload["exp"] = expire
    return jwt.encode(payload, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM)


def decode_access_token(token: str) -> dict[str, Any] | None:
    try:
        return jwt.decode(token, settings.JWT_SECRET, algorithms=[settings.JWT_ALGORITHM])
    except Exception:
        return None


# ── Fernet encryption (Langflow credentials at rest) ──────────────────────────

def _get_fernet() -> Fernet | None:
    if not settings.FERNET_KEY:
        return None
    return Fernet(settings.FERNET_KEY.encode())


def encrypt_secret(plain: str) -> str:
    """Encrypt a secret string. Falls back to plaintext if FERNET_KEY not set."""
    f = _get_fernet()
    if f is None:
        return plain
    return f.encrypt(plain.encode()).decode()


def decrypt_secret(encrypted: str) -> str:
    """Decrypt a secret string. Falls back to returning as-is if FERNET_KEY not set."""
    f = _get_fernet()
    if f is None:
        return encrypted
    try:
        return f.decrypt(encrypted.encode()).decode()
    except Exception:
        return encrypted
