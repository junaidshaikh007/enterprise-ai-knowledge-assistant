import uuid
from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime

class OrganizationBase(BaseModel):
    name: str

class OrganizationCreate(OrganizationBase):
    pass

class Organization(OrganizationBase):
    id: uuid.UUID
    created_at: datetime
    
    class Config:
        from_attributes = True

class UserBase(BaseModel):
    email: EmailStr
    is_active: Optional[bool] = True
    is_superuser: bool = False

class UserCreate(UserBase):
    password: str
    organization_name: str  # For simplified registration to create org and user at once

class User(UserBase):
    id: uuid.UUID
    organization_id: uuid.UUID
    created_at: datetime
    
    class Config:
        from_attributes = True
