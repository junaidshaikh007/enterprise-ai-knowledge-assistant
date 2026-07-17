from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.core.database import get_db
from app.core import security
from app.core.config import settings
from app.core.deps import get_current_user
from app.models.user import User
from app.models.organization import Organization
from app.schemas.user import UserCreate, User as UserSchema
from app.schemas.token import Token

router = APIRouter()

@router.post("/login", response_model=Token)
async def login_access_token(
    db: AsyncSession = Depends(get_db), form_data: OAuth2PasswordRequestForm = Depends()
):
    """
    OAuth2 compatible token login, get an access token for future requests
    """
    result = await db.execute(select(User).where(User.email == form_data.username))
    user = result.scalars().first()
    
    if not user or not security.verify_password(form_data.password, user.hashed_password):
        raise HTTPException(status_code=400, detail="Incorrect email or password")
    elif not user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
        
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    return {
        "access_token": security.create_access_token(
            user.id, expires_delta=access_token_expires
        ),
        "token_type": "bearer",
    }

@router.post("/register", response_model=UserSchema)
async def register_user(
    *,
    db: AsyncSession = Depends(get_db),
    user_in: UserCreate,
):
    """
    Create new user and organization.
    """
    # Check if user exists
    result = await db.execute(select(User).where(User.email == user_in.email))
    if result.scalars().first():
        raise HTTPException(
            status_code=400,
            detail="The user with this username already exists in the system.",
        )
        
    # Create org
    org = Organization(name=user_in.organization_name)
    db.add(org)
    await db.commit()
    await db.refresh(org)
    
    # Create user
    user = User(
        email=user_in.email,
        hashed_password=security.get_password_hash(user_in.password),
        organization_id=org.id,
        is_active=True,
        is_superuser=False,
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)
    
    return user

@router.get("/me", response_model=UserSchema)
async def test_token(current_user: User = Depends(get_current_user)):
    """
    Test access token
    """
    return current_user
