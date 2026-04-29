from collections.abc import Mapping

import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from compass.config import settings

security = HTTPBearer(auto_error=False)


class CognitoAuthorizer:
    def __init__(self) -> None:
        self._jwks_client: jwt.PyJWKClient | None = None
        self._jwks_url: str | None = None

    @property
    def enabled(self) -> bool:
        return bool(settings.cognito_user_pool_id and settings.cognito_client_id)

    @property
    def region(self) -> str:
        return settings.cognito_region or settings.aws_region

    @property
    def issuer(self) -> str:
        return f"https://cognito-idp.{self.region}.amazonaws.com/{settings.cognito_user_pool_id}"

    @property
    def jwks_url(self) -> str:
        return f"{self.issuer}/.well-known/jwks.json"

    def _get_jwks_client(self) -> jwt.PyJWKClient:
        if self._jwks_client is None or self._jwks_url != self.jwks_url:
            self._jwks_url = self.jwks_url
            self._jwks_client = jwt.PyJWKClient(self.jwks_url)
        return self._jwks_client

    def verify_token(self, token: str) -> Mapping[str, object]:
        signing_key = self._get_jwks_client().get_signing_key_from_jwt(token).key
        claims = jwt.decode(
            token,
            signing_key,
            algorithms=["RS256"],
            issuer=self.issuer,
            options={"verify_aud": False},
        )

        token_use = claims.get("token_use")
        if token_use == "id" and claims.get("aud") != settings.cognito_client_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail={"error": "invalid_token", "message": "Unexpected token audience"},
            )

        if token_use == "access" and claims.get("client_id") != settings.cognito_client_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail={"error": "invalid_token", "message": "Unexpected client id"},
            )

        if token_use not in {"id", "access"}:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail={"error": "invalid_token", "message": "Unsupported token type"},
            )

        return claims


authorizer = CognitoAuthorizer()


async def require_auth(
    credentials: HTTPAuthorizationCredentials | None = Depends(security),
) -> Mapping[str, object]:
    if not authorizer.enabled:
        return {}

    if credentials is None or credentials.scheme.lower() != "bearer":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={"error": "unauthorized", "message": "Bearer token required"},
        )

    try:
        return authorizer.verify_token(credentials.credentials)
    except HTTPException:
        raise
    except jwt.PyJWTError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={"error": "invalid_token", "message": str(exc)},
        ) from exc