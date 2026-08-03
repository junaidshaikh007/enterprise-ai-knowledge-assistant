from pydantic import BaseModel
from typing import List, Dict, Any, Optional
import uuid
from datetime import datetime

class ChatRequest(BaseModel):
    message: str

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
