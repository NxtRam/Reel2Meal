from datetime import datetime, timedelta, timezone

from jose import JWTError, jwt
from passlib.context import CryptContext

from app.config import settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(plain: str) -> str:
    return pwd_context.hash(plain)


def verify_password(plain: str, hashed: str) -> bool:
    return pwd_context.verify(plain, hashed)


def create_access_token(subject: str) -> tuple[str, int]:
    """Returns (encoded_jwt, expires_in_seconds)."""
    expire_seconds = settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60
    expire = datetime.now(timezone.utc) + timedelta(seconds=expire_seconds)
    payload = {"sub": subject, "exp": expire}
    token = jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return token, expire_seconds


def decode_token(token: str) -> str | None:
    """Returns user id (sub) or None if invalid."""
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        return payload.get("sub")
    except JWTError:
        return None
