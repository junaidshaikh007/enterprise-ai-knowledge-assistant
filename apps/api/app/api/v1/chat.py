from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.deps import get_current_active_user, get_current_organization
from app.models.user import User
from app.models.organization import Organization
from app.schemas.chat import ChatRequest, ChatResponse
from app.services.retrieval_service import retrieval_service
from app.services.llm_service import llm_service

router = APIRouter()

@router.post("/", response_model=ChatResponse)
async def chat(
    request: ChatRequest,
    current_user: User = Depends(get_current_active_user),
    current_org: Organization = Depends(get_current_organization),
    db: AsyncSession = Depends(get_db)
):
    """
    Endpoint to ask questions based on the uploaded organization documents.
    """
    try:
        # Step 1: Retrieve relevant context chunks matching organization_id
        context = retrieval_service.retrieve_context(
            query=request.message,
            organization_id=current_org.id,
            top_k=5
        )
        
        # Step 2: Generate response using LLM
        answer = llm_service.generate_answer(
            query=request.message,
            context_chunks=context
        )
        
        return ChatResponse(
            answer=answer,
            sources=context
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred during chat processing: {str(e)}"
        )
