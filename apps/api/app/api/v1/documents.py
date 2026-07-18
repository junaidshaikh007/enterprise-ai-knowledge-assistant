from fastapi import APIRouter, Depends, UploadFile, File, HTTPException, status
from typing import List
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.deps import get_current_active_user, get_current_organization
from app.models.user import User
from app.models.organization import Organization
from app.utils.document_parser import document_parser

router = APIRouter()

@router.post("/upload")
async def upload_document(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_active_user),
    current_org: Organization = Depends(get_current_organization),
    db: AsyncSession = Depends(get_db)
):
    """
    Upload a document for processing.
    """
    allowed_extensions = ["pdf", "txt", "docx"]
    file_ext = file.filename.split(".")[-1].lower() if "." in file.filename else ""
    
    if file_ext not in allowed_extensions:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"File extension not allowed. Allowed types: {', '.join(allowed_extensions)}"
        )
        
    # Read file content
    content = await file.read()
    
    try:
        chunks = document_parser.process_document(content, file_ext)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error processing document: {str(e)}"
        )
    
    # Return response with chunk metadata for now
    # In Phase 4, we will send these chunks to the Vector DB
    return {
        "filename": file.filename,
        "content_type": file.content_type,
        "size": len(content),
        "status": "processed",
        "num_chunks": len(chunks),
        "message": "File successfully parsed and chunked. Ready for Vector DB."
    }
