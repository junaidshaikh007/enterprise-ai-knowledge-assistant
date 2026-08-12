from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List
import uuid

from app.core.database import get_db
from app.core.deps import get_current_active_user, get_current_organization
from app.models.user import User
from app.models.organization import Organization
from app.models.chat import ChatSession, ChatMessage
from app.schemas.chat import ChatSessionResponse, ChatSessionCreate, ChatMessageResponse

router = APIRouter()

@router.post("/", response_model=ChatSessionResponse)
async def create_chat_session(
    request: ChatSessionCreate,
    current_user: User = Depends(get_current_active_user),
    current_org: Organization = Depends(get_current_organization),
    db: AsyncSession = Depends(get_db)
):
    session = ChatSession(
        title=request.title,
        user_id=current_user.id,
        organization_id=current_org.id
    )
    db.add(session)
    await db.commit()
    await db.refresh(session)
    return session

@router.get("/", response_model=List[ChatSessionResponse])
async def fetch_chat_sessions(
    current_user: User = Depends(get_current_active_user),
    current_org: Organization = Depends(get_current_organization),
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(
        select(ChatSession)
        .where(ChatSession.user_id == current_user.id)
        .where(ChatSession.organization_id == current_org.id)
        .order_by(ChatSession.created_at.desc())
    )
    return result.scalars().all()

@router.delete("/{session_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_chat_session(
    session_id: uuid.UUID,
    current_user: User = Depends(get_current_active_user),
    current_org: Organization = Depends(get_current_organization),
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(
        select(ChatSession)
        .where(ChatSession.id == session_id)
        .where(ChatSession.user_id == current_user.id)
        .where(ChatSession.organization_id == current_org.id)
    )
    session = result.scalars().first()
    
    if not session:
        raise HTTPException(status_code=404, detail="Chat session not found")
        
    await db.delete(session)
    await db.commit()

@router.get("/{session_id}/messages", response_model=List[ChatMessageResponse])
async def fetch_session_messages(
    session_id: uuid.UUID,
    current_user: User = Depends(get_current_active_user),
    current_org: Organization = Depends(get_current_organization),
    db: AsyncSession = Depends(get_db)
):
    session_result = await db.execute(
        select(ChatSession)
        .where(ChatSession.id == session_id)
        .where(ChatSession.user_id == current_user.id)
        .where(ChatSession.organization_id == current_org.id)
    )
    if not session_result.scalars().first():
        raise HTTPException(status_code=404, detail="Chat session not found")
        
    messages_result = await db.execute(
        select(ChatMessage)
        .join(ChatSession, ChatMessage.session_id == ChatSession.id)
        .where(ChatMessage.session_id == session_id)
        .where(ChatSession.user_id == current_user.id)
        .where(ChatSession.organization_id == current_org.id)
        .order_by(ChatMessage.created_at.asc())
    )
    return messages_result.scalars().all()
