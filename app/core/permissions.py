from fastapi import Header, HTTPException, status, Depends
from typing import Optional, Callable

from app.core.jwtoken import JWToken
from app.domain.entities.user import User


from fastapi import Header, HTTPException, status, Depends
from typing import Optional, Callable

from app.core.jwtoken import JWToken
from app.domain.entities.user import User
from app.helpers.enums.enums import PermissionLevelEnum
from app.schemas.token import TokenUser


async def manage_user_permission(
    authorization: Optional[str] = Header(None),
    required_permission: PermissionLevelEnum = PermissionLevelEnum.USER
) -> User:
    if not authorization:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token ausente"
        )

    token = authorization.replace("Bearer ", "")
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



def RequirePermission(required_permission: PermissionLevelEnum) -> Callable:
    async def wrapper(authorization: Optional[str] = Header(None)):
        return await manage_user_permission(authorization, required_permission)
    return Depends(wrapper)
