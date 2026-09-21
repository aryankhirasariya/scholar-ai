from fastapi import APIRouter
from app.models.schemas import SignupRequest, LoginRequest, TokenResponse
from app.services.auth_service import (
    create_user, get_user_by_email,
    verify_password, create_token
)
from fastapi import HTTPException

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/signup", response_model=TokenResponse)
def signup(body: SignupRequest):
    user  = create_user(body.name, body.email, body.password)
    token = create_token({"email": user["email"], "name": user["name"]})
    return TokenResponse(
        access_token=token,
        name=user["name"],
        email=user["email"]
    )


@router.post("/login", response_model=TokenResponse)
def login(body: LoginRequest):
    user = get_user_by_email(body.email)
    if not user or not verify_password(body.password, user["password"]):
        raise HTTPException(status_code=401, detail="Invalid email or password")
    token = create_token({"email": user["email"], "name": user["name"]})
    return TokenResponse(
        access_token=token,
        name=user["name"],
        email=user["email"]
    )


@router.get("/me")
def me():
    return {"message": "Token is valid"}