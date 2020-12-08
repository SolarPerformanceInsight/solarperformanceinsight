from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import httpx
from jose import jwt, jwk  # type: ignore
from pydantic.types import Json


from . import settings


bearer_scheme = HTTPBearer()


async def get_auth_key() -> Json:
    if settings.auth_key is not None:
        return settings.auth_key
    async with httpx.AsyncClient() as client:
        req = await client.get(settings.auth_jwk_url, timeout=10.0)
    req.raise_for_status()  # let this raise the error and fail app startup
    key = req.json()
    settings.auth_key = key
    return key


async def get_user_id(
    creds: HTTPAuthorizationCredentials = Depends(bearer_scheme),
) -> str:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    token = creds.credentials
    key = await get_auth_key()
    try:
        payload = jwt.decode(
            token,
            algorithms=["RS256"],
            key=key,
            audience=settings.auth_audience,
            issuer=settings.auth_issuer,
        )
        user_id: str = payload.get("sub")
        if user_id is None:  # pragma: no cover
            raise credentials_exception
    except (
        jwt.JWTError,
        jwk.JWKError,
        jwt.ExpiredSignatureError,
        jwt.JWTClaimsError,
        AttributeError,
        AssertionError,
        IndexError,
    ):
        raise credentials_exception
    return user_id
