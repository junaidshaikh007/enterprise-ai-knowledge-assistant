from collections.abc import AsyncIterator

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession
from langfuse import observe, get_client

from app.core.database import get_db
from app.core.deps import get_current_active_user, get_current_organization
from app.models.user import User
from app.models.organization import Organization
from app.schemas.chat import ChatRequest
from app.models.chat import ChatMessage
from app.services.retrieval_service import retrieval_service
from app.services.llm_service import llm_service
from app.api.v1.sse import format_sse_event
from app.core.database import AsyncSessionLocal

router = APIRouter()

@router.post("/")
@observe(name="chat_request")
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
        # Update trace level details in Langfuse for observability
        get_client().update_current_span(
            name="chat_request",
            input={"message": request.message, "session_id": request.session_id},
            metadata={"user_id": str(current_user.id), "org_id": str(current_org.id)},
        )

        # Step 1: Retrieve relevant context chunks matching organization_id
        context = retrieval_service.retrieve_context(
            query=request.message,
            organization_id=current_org.id,
            top_k=5
        )
        session_id = request.session_id
        
        if session_id:
            user_msg = ChatMessage(
                session_id=session_id,
                role="user",
                content=request.message
            )
            db.add(user_msg)
            await db.commit()

        async def event_stream() -> AsyncIterator[str]:
            yield format_sse_event({"sources": context}, event="sources")

            full_answer = ""
            async for token in llm_service.stream_answer(
                query=request.message,
                context_chunks=context,
            ):
                full_answer += token
                yield format_sse_event({"token": token}, event="token")

            yield format_sse_event({"done": True}, event="done")
            
            # Record output trace details in Langfuse
            get_client().update_current_span(output=full_answer)

            if session_id:
                async with AsyncSessionLocal() as bg_db:
                    assistant_msg = ChatMessage(
                        session_id=session_id,
                        role="assistant",
                        content=full_answer
                    )
                    bg_db.add(assistant_msg)
                    await bg_db.commit()

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
