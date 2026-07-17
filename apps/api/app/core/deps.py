from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
import jwt
from pydantic import ValidationError

from app.core.config import settings
from app.core.database import get_db
from app.core import security
from app.models.user import User
from app.models.organization import Organization
from app.schemas.token import TokenPayload

reusable_oauth2 = OAuth2PasswordBearer(
    tokenUrl=f"{settings.API_V1_STR}/auth/login"
)

async def get_current_user(
    db: AsyncSession = Depends(get_db), token: str = Depends(reusable_oauth2)
) -> User:
    try:
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[security.ALGORITHM]
        )
        token_data = TokenPayload(**payload)
    except (jwt.PyJWTError, ValidationError):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Could not validate credentials",
        )
    result = await db.execute(select(User).where(User.id == token_data.sub))
    user = result.scalars().first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

async def get_current_active_user(
    current_user: User = Depends(get_current_user),
) -> User:
    if not current_user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user

async def get_current_organization(
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
) -> Organization:
    result = await db.execute(select(Organization).where(Organization.id == current_user.organization_id))
    org = result.scalars().first()
    if not org:
        raise HTTPException(status_code=404, detail="Organization not found")
    return org
