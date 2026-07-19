from pydantic import BaseModel
from typing import List, Dict, Any

class ChatRequest(BaseModel):
    message: str

class ChatSource(BaseModel):
    score: float
    text: str
    file_name: str

class ChatResponse(BaseModel):
    answer: str
    sources: List[ChatSource]
