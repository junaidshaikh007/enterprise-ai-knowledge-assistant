from pydantic import BaseModel
from typing import List, Dict, Any, Optional
import uuid
from datetime import datetime

class ChatRequest(BaseModel):
    message: str
    session_id: Optional[uuid.UUID] = None

class ChatSource(BaseModel):
    score: float
    text: str
    file_name: str

class ChatResponse(BaseModel):
    answer: str
    sources: List[ChatSource]

class ChatSessionCreate(BaseModel):
    title: Optional[str] = "New Chat"

class ChatSessionResponse(BaseModel):
    id: uuid.UUID
    title: str
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class ChatMessageResponse(BaseModel):
    id: uuid.UUID
    session_id: uuid.UUID
    role: str
    content: str
    created_at: datetime

    class Config:
        from_attributes = True
