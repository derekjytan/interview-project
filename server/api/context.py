from dataclasses import dataclass
from typing import Annotated

from fastapi import Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from api.dependencies import DbSession
from models.user import User
from service import auth as auth_service


@dataclass(frozen=True)
class RequestContext:
    user: User
    session_token: str


_bearer = HTTPBearer(auto_error=False)


def require_request_context(
    session: DbSession,
    credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(_bearer)],
) -> RequestContext:
    """Resolve the bearer token to its user; 401 when missing or unknown."""
    if (
        credentials is None
        or (user := auth_service.get_session_user(session, credentials.credentials))
        is None
    ):
        # RFC 7235 §3.1 / RFC 6750 want `WWW-Authenticate: Bearer` on 401s. Skipped: the UI
        # always sends a token and sessions never expire, so this only fires after a DB wipe.
        raise HTTPException(status_code=401, detail="Not authenticated.")
    return RequestContext(user=user, session_token=credentials.credentials)


AuthContext = Annotated[RequestContext, Depends(require_request_context)]
