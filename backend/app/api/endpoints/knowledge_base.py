from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc, func
from typing import List, Optional
import os

from app.core.database import get_db
from app.core.security import get_current_active_user
from app.models.user import User
from app.models.knowledge_base import KnowledgeBase, Document, DocumentChunk
from app.schemas.knowledge_base import (
    KnowledgeBaseCreate,
    KnowledgeBaseResponse,
    KnowledgeBaseUpdate,
    DocumentResponse,
    DocumentWithContent,
)
from app.services.pdf_service import pdf_service
from app.services.vector_service import vector_service

router = APIRouter()


@router.post("/knowledge-bases", response_model=KnowledgeBaseResponse)
async def create_knowledge_base(
    kb_data: KnowledgeBaseCreate,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Create a new knowledge base"""
    new_kb = KnowledgeBase(
        user_id=current_user.id,
        name=kb_data.name,
        description=kb_data.description,
    )

    db.add(new_kb)
    await db.commit()
    await db.refresh(new_kb)

    return new_kb


@router.get("/knowledge-bases", response_model=List[KnowledgeBaseResponse])
async def get_knowledge_bases(
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
    skip: int = 0,
    limit: int = 50
):
    """Get all knowledge bases for the current user"""
    result = await db.execute(
        select(KnowledgeBase)
        .where(KnowledgeBase.user_id == current_user.id)
        .order_by(desc(KnowledgeBase.updated_at))
        .offset(skip)
        .limit(limit)
    )
    knowledge_bases = result.scalars().all()
    return knowledge_bases


@router.get("/knowledge-bases/{kb_id}", response_model=KnowledgeBaseResponse)
async def get_knowledge_base(
    kb_id: int,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Get a specific knowledge base"""
    result = await db.execute(
        select(KnowledgeBase).where(
            (KnowledgeBase.id == kb_id) &
            (KnowledgeBase.user_id == current_user.id)
        )
    )
    kb = result.scalar_one_or_none()

    if not kb:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Knowledge base not found"
        )

    return kb


@router.patch("/knowledge-bases/{kb_id}", response_model=KnowledgeBaseResponse)
async def update_knowledge_base(
    kb_id: int,
    kb_data: KnowledgeBaseUpdate,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Update a knowledge base"""
    result = await db.execute(
        select(KnowledgeBase).where(
            (KnowledgeBase.id == kb_id) &
            (KnowledgeBase.user_id == current_user.id)
        )
    )
    kb = result.scalar_one_or_none()

    if not kb:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Knowledge base not found"
        )

    if kb_data.name is not None:
        kb.name = kb_data.name
    if kb_data.description is not None:
        kb.description = kb_data.description

    await db.commit()
    await db.refresh(kb)

    return kb


@router.delete("/knowledge-bases/{kb_id}")
async def delete_knowledge_base(
    kb_id: int,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Delete a knowledge base"""
    result = await db.execute(
        select(KnowledgeBase).where(
            (KnowledgeBase.id == kb_id) &
            (KnowledgeBase.user_id == current_user.id)
        )
    )
    kb = result.scalar_one_or_none()

    if not kb:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Knowledge base not found"
        )

    # Delete vector store
    vector_service.delete_knowledge_base(current_user.id, kb_id)

    await db.delete(kb)
    await db.commit()

    return {"message": "Knowledge base deleted successfully"}


@router.post("/knowledge-bases/{kb_id}/upload", response_model=DocumentResponse)
async def upload_document(
    kb_id: int,
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Upload a document to a knowledge base"""
    # Verify knowledge base exists
    result = await db.execute(
        select(KnowledgeBase).where(
            (KnowledgeBase.id == kb_id) &
            (KnowledgeBase.user_id == current_user.id)
        )
    )
    kb = result.scalar_one_or_none()

    if not kb:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Knowledge base not found"
        )

    # Check file type
    if not file.filename.lower().endswith('.pdf'):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only PDF files are supported"
        )

    # Read file content
    file_content = await file.read()
    file_size = len(file_content)

    # Save file
    file_path = await pdf_service.save_upload(
        file_content,
        file.filename,
        current_user.id
    )

    # Create document record
    document = Document(
        knowledge_base_id=kb_id,
        user_id=current_user.id,
        filename=file.filename,
        file_type="pdf",
        file_size=file_size,
        file_path=file_path,
        processed=0,  # pending
    )

    db.add(document)
    await db.commit()
    await db.refresh(document)

    # Process document asynchronously (in background)
    # For now, we'll process it immediately
    try:
        # Update status to processing
        document.processed = 1
        await db.commit()

        # Extract text
        text_content = pdf_service.extract_text_from_pdf(file_path)
        document.content = text_content

        # Extract metadata
        metadata = pdf_service.extract_metadata(file_path)
        document.metadata = metadata

        # Chunk text
        chunks = pdf_service.chunk_text(text_content)

        # Add to vector store
        chunk_ids = vector_service.add_documents(
            user_id=current_user.id,
            kb_id=kb_id,
            document_id=document.id,
            chunks=chunks
        )

        # Save chunks to database
        for i, (chunk_content, chunk_id) in enumerate(zip(chunks, chunk_ids)):
            chunk = DocumentChunk(
                document_id=document.id,
                chunk_index=i,
                content=chunk_content,
                embedding_id=chunk_id
            )
            db.add(chunk)

        # Update status to completed
        document.processed = 2
        await db.commit()
        await db.refresh(document)

    except Exception as e:
        document.processed = 3  # failed
        document.metadata = {"error": str(e)}
        await db.commit()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to process document: {str(e)}"
        )

    return document


@router.get("/knowledge-bases/{kb_id}/documents", response_model=List[DocumentResponse])
async def get_documents(
    kb_id: int,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
    skip: int = 0,
    limit: int = 50
):
    """Get all documents in a knowledge base"""
    # Verify knowledge base exists
    result = await db.execute(
        select(KnowledgeBase).where(
            (KnowledgeBase.id == kb_id) &
            (KnowledgeBase.user_id == current_user.id)
        )
    )
    kb = result.scalar_one_or_none()

    if not kb:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Knowledge base not found"
        )

    # Get documents
    result = await db.execute(
        select(Document)
        .where(Document.knowledge_base_id == kb_id)
        .order_by(desc(Document.created_at))
        .offset(skip)
        .limit(limit)
    )
    documents = result.scalars().all()

    return documents


@router.delete("/documents/{doc_id}")
async def delete_document(
    doc_id: int,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Delete a document"""
    result = await db.execute(
        select(Document).where(
            (Document.id == doc_id) &
            (Document.user_id == current_user.id)
        )
    )
    document = result.scalar_one_or_none()

    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found"
        )

    # Delete from vector store
    vector_service.delete_document(
        current_user.id,
        document.knowledge_base_id,
        doc_id
    )

    # Delete file
    if os.path.exists(document.file_path):
        os.remove(document.file_path)

    await db.delete(document)
    await db.commit()

    return {"message": "Document deleted successfully"}


@router.post("/knowledge-bases/{kb_id}/search")
async def search_knowledge_base(
    kb_id: int,
    query: str = Form(...),
    n_results: int = Form(5),
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Search knowledge base for relevant information"""
    # Verify knowledge base exists
    result = await db.execute(
        select(KnowledgeBase).where(
            (KnowledgeBase.id == kb_id) &
            (KnowledgeBase.user_id == current_user.id)
        )
    )
    kb = result.scalar_one_or_none()

    if not kb:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Knowledge base not found"
        )

    # Search vector store
    results = vector_service.search(
        user_id=current_user.id,
        kb_id=kb_id,
        query=query,
        n_results=n_results
    )

    return results
