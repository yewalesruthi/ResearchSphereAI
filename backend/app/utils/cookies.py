from fastapi import Response

from app.utils.config import get_settings
from app.utils.deps import COOKIE_NAME

COOKIE_MAX_AGE = 60 * 60 * 24 * 7  # 7 days


def set_auth_cookie(response: Response, token: str) -> None:
    settings = get_settings()
    is_prod = settings.environment == "production"
    response.set_cookie(
        key=COOKIE_NAME,
        value=token,
        httponly=True,
        secure=is_prod,
        samesite="none" if is_prod else "lax",
        max_age=COOKIE_MAX_AGE,
        path="/",
    )


def clear_auth_cookie(response: Response) -> None:
    settings = get_settings()
    is_prod = settings.environment == "production"
    response.delete_cookie(
        key=COOKIE_NAME,
        path="/",
        secure=is_prod,
        samesite="none" if is_prod else "lax",
    )
