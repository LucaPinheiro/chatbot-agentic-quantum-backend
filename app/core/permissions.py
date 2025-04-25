from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from app.core.jwtoken import JWToken
from app.helpers.enums.enums import PermissionLevelEnum
from app.schemas.token import TokenUser

auth_scheme = HTTPBearer(auto_error=True)

async def manage_user_permission(
    credentials: HTTPAuthorizationCredentials = Depends(auth_scheme),
    required_permission: PermissionLevelEnum = PermissionLevelEnum.USER
) -> TokenUser:
    token = credentials.credentials
    decoded = JWToken.decode(token)

    if not decoded:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido ou expirado"
        )

    user_id = decoded.get("user_id")
    permission = decoded.get("permission")

    if permission is None or permission < required_permission:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Permissão insuficiente"
        )

    return TokenUser(id=user_id, permission=permission)


def RequirePermission(required_permission: PermissionLevelEnum):
    async def dependency(credentials: HTTPAuthorizationCredentials = Depends(auth_scheme)):
        return await manage_user_permission(credentials, required_permission)
    return dependency 
