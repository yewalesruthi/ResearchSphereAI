from fastapi import Cookie, Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from app.models.database import get_db
from app.models.user import User
from app.utils.jwt import decode_access_token

security = HTTPBearer(auto_error=False)
COOKIE_NAME = "access_token"


def _resolve_token(
    credentials: HTTPAuthorizationCredentials | None,
    cookie_token: str | None,
) -> str | None:
    if credentials and credentials.credentials:
        return credentials.credentials
    if cookie_token:
        return cookie_token
    return None


def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(security),
    access_token: str | None = Cookie(default=None, alias=COOKIE_NAME),
    db: Session = Depends(get_db),
) -> User:
    token = _resolve_token(credentials, access_token)
    if not token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")

    payload = decode_access_token(token)
    if payload is None or "sub" not in payload:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")

    user = db.query(User).filter(User.id == int(payload["sub"])).first()
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")

    return user


def get_workspace_or_404(db: Session, workspace_id: int, user_id: int):
    from app.models.workspace import Workspace

    workspace = (
        db.query(Workspace)
        .filter(Workspace.id == workspace_id, Workspace.user_id == user_id)
        .first()
    )
    if workspace is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Workspace not found")
    return workspace
