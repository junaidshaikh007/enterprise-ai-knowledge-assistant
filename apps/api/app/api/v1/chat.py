from collections.abc import AsyncIterator

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.deps import get_current_active_user, get_current_organization
from app.models.user import User
from app.models.organization import Organization
from app.schemas.chat import ChatRequest
from app.services.retrieval_service import retrieval_service
from app.services.llm_service import llm_service
from app.api.v1.sse import format_sse_event

router = APIRouter()

@router.post("/")
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
        
        async def event_stream() -> AsyncIterator[str]:
            yield format_sse_event({"sources": context}, event="sources")

            async for token in llm_service.stream_answer(
                query=request.message,
                context_chunks=context,
            ):
                yield format_sse_event({"token": token}, event="token")

            yield format_sse_event({"done": True}, event="done")

        return StreamingResponse(
            event_stream(),
            media_type="text/event-stream",
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
                "X-Accel-Buffering": "no",
            },
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred during chat processing: {str(e)}"
        )
