"""Password hashing and database-backed, revocable cookie sessions."""
import hashlib
import hmac
import os
import secrets
import time

import bcrypt

from fastapi import Depends, HTTPException, Request, Response
from sqlalchemy.orm import Session

from Backend.database import get_db
from Backend.models import LoginSession, User

COOKIE = "fitlog_session"
SESSION_SECONDS = 60 * 60 * 24 * 7
ITERATIONS = 600_000


def hash_password(password):
    salt = secrets.token_hex(16)
    digest = hashlib.pbkdf2_hmac("sha256", password.encode(), salt.encode(), ITERATIONS)
    return f"pbkdf2_sha256${ITERATIONS}${salt}${digest.hex()}"


def verify_password(password, encoded):
    try:
        # Keep accounts made by the original bcrypt-based prototype usable.
        if encoded.startswith(("$2a$", "$2b$", "$2y$")):
            return bcrypt.checkpw(password.encode(), encoded.encode())
        algorithm, iterations, salt, expected = encoded.split("$")
        if algorithm != "pbkdf2_sha256":
            return False
        actual = hashlib.pbkdf2_hmac("sha256", password.encode(), salt.encode(), int(iterations))
        return hmac.compare_digest(actual.hex(), expected)
    except (ValueError, TypeError):
        return False


def token_hash(token):
    return hashlib.sha256(token.encode()).hexdigest()


def start_session(response: Response, user_id: int, db: Session):
    token = secrets.token_urlsafe(32)
    db.query(LoginSession).filter(LoginSession.expires_at <= time.time()).delete()
    db.add(LoginSession(token_hash=token_hash(token), user_id=user_id,
                        expires_at=time.time() + SESSION_SECONDS))
    db.commit()
    response.set_cookie(COOKIE, token, httponly=True, samesite="strict",
                        secure=os.getenv("COOKIE_SECURE", "false").lower() == "true",
                        max_age=SESSION_SECONDS)


def current_user(request: Request, db: Session = Depends(get_db)):
    token = request.cookies.get(COOKIE)
    session = db.get(LoginSession, token_hash(token)) if token else None
    if session is None or session.expires_at <= time.time():
        raise HTTPException(status_code=401, detail="Please sign in to continue.")
    user = db.get(User, session.user_id)
    if user is None:
        raise HTTPException(status_code=401, detail="Please sign in to continue.")
    return user
