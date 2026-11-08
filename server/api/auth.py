from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from api.context import AuthContext
from api.dependencies import DbSession
from models.user import User
from service import auth as auth_service

router = APIRouter(prefix="/api")


class Credentials(BaseModel):
    name: str = Field(min_length=1)
    password: str = Field(min_length=1)


class LoginResponse(BaseModel):
    token: str
    user: User


@router.post("/auth/login")
def login(request: Credentials, session: DbSession) -> LoginResponse:
    """Exchange name + password for a session token; 401 on bad credentials."""
    user = auth_service.authenticate(session, request.name, request.password)
    if user is None:
        raise HTTPException(status_code=401, detail="Invalid name or password.")
    return LoginResponse(token=auth_service.create_session(session, user.id), user=user)


@router.post("/auth/signup", status_code=201)
def signup(request: Credentials, session: DbSession) -> LoginResponse:
    """Create a user and start a session; 409 when the name is taken."""
    user = auth_service.create_user(session, request.name, request.password)
    if user is None:
        raise HTTPException(status_code=409, detail="That name is already taken.")
    return LoginResponse(token=auth_service.create_session(session, user.id), user=user)


@router.post("/auth/logout", status_code=204)
def logout(session: DbSession, context: AuthContext) -> None:
    """Delete the caller's session."""
    auth_service.delete_session(session, context.session_token)
