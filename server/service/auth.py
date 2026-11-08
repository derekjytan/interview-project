import secrets
from uuid import UUID

from sqlalchemy import delete, select
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.orm import Session

from entities import User as UserEntity
from entities import UserSession
from models.user import User


def authenticate(session: Session, name: str, password: str) -> User | None:
    """Return the matching user, or None.

    WARNING: this sandbox app stores plaintext passwords for demonstration
    only. Production applications must use a salted, slow password hash
    (e.g. Argon2id) or delegate authentication to an identity provider.
    """
    user = session.scalar(
        select(UserEntity).where(
            UserEntity.name == name, UserEntity.password == password
        )
    )
    return User.model_validate(user, from_attributes=True) if user else None


def create_user(session: Session, name: str, password: str) -> User | None:
    """Create a user, or return None if the name is taken.

    Stores plaintext passwords; see the warning on authenticate.
    """
    user = session.scalar(
        insert(UserEntity)
        .values(name=name, password=password)
        .on_conflict_do_nothing(index_elements=[UserEntity.name])
        .returning(UserEntity)
    )
    result = User.model_validate(user, from_attributes=True) if user else None
    session.commit()
    return result


def create_session(session: Session, user_id: UUID) -> str:
    """Start a session for the user and return its bearer token."""
    token = secrets.token_urlsafe(32)
    session.add(UserSession(token=token, user_id=user_id))
    session.commit()
    return token


def get_session_user(session: Session, token: str) -> User | None:
    """Return the user owning this session token, or None if it's unknown."""
    user = session.scalar(
        select(UserEntity)
        .join(UserSession, UserSession.user_id == UserEntity.id)
        .where(UserSession.token == token)
    )
    return User.model_validate(user, from_attributes=True) if user else None


def delete_session(session: Session, token: str) -> None:
    """End the session (idempotent)."""
    session.execute(delete(UserSession).where(UserSession.token == token))
    session.commit()
