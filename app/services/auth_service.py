import sqlite3
import os
from datetime import datetime, timedelta
import bcrypt
from jose import JWTError, jwt
from fastapi import HTTPException, status, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

# ── CONFIG ────────────────────────────────────────────────

SECRET_KEY  = os.getenv("SECRET_KEY", "scholar-ai-secret-change-in-production")
ALGORITHM   = "HS256"
TOKEN_EXPIRE_HOURS = 24 * 7   # 7 days

bearer      = HTTPBearer()
DB_PATH     = "data/users.db"

# ── DATABASE SETUP ────────────────────────────────────────

def init_db():
    os.makedirs("data", exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id         INTEGER PRIMARY KEY AUTOINCREMENT,
            name       TEXT    NOT NULL,
            email      TEXT    NOT NULL UNIQUE,
            password   TEXT    NOT NULL,
            created_at TEXT    NOT NULL
        )
    """)
    conn.commit()
    conn.close()

# ── PASSWORD UTILS ────────────────────────────────────────

def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()

def verify_password(plain: str, hashed: str) -> bool:
    return bcrypt.checkpw(plain.encode(), hashed.encode())

# ── JWT UTILS ─────────────────────────────────────────────

def create_token(data: dict) -> str:
    payload = data.copy()
    payload["exp"] = datetime.utcnow() + timedelta(hours=TOKEN_EXPIRE_HOURS)
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)

def decode_token(token: str) -> dict:
    try:
        return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token"
        )

# ── USER CRUD ─────────────────────────────────────────────

def create_user(name: str, email: str, password: str) -> dict:
    conn = sqlite3.connect(DB_PATH)
    try:
        conn.execute(
            "INSERT INTO users (name, email, password, created_at) VALUES (?,?,?,?)",
            (name, email, hash_password(password),
             datetime.utcnow().isoformat())
        )
        conn.commit()
        user = conn.execute(
            "SELECT id, name, email FROM users WHERE email=?", (email,)
        ).fetchone()
        return {"id": user[0], "name": user[1], "email": user[2]}
    except sqlite3.IntegrityError:
        raise HTTPException(
            status_code=400,
            detail="Email already registered"
        )
    finally:
        conn.close()

def get_user_by_email(email: str) -> dict | None:
    conn = sqlite3.connect(DB_PATH)
    row  = conn.execute(
        "SELECT id, name, email, password FROM users WHERE email=?", (email,)
    ).fetchone()
    conn.close()
    if not row:
        return None
    return {"id": row[0], "name": row[1],
            "email": row[2], "password": row[3]}

# ── AUTH DEPENDENCY ───────────────────────────────────────

def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(bearer)
) -> dict:
    payload = decode_token(credentials.credentials)
    email   = payload.get("email")
    if not email:
        raise HTTPException(status_code=401, detail="Invalid token")
    user = get_user_by_email(email)
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
    return user