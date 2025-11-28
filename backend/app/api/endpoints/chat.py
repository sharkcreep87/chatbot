from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc
from typing import List
import json

from app.core.database import get_db
from app.core.security import get_current_active_user
from app.models.user import User
from app.models.conversation import Conversation
from app.models.message import Message
from app.schemas.conversation import (
    ConversationCreate,
    ConversationResponse,
    ConversationUpdate,
    MessageResponse,
    ChatRequest,
    ChatResponse,
)
from app.services.ai_service import ai_service
from app.services.vector_service import vector_service
from app.models.knowledge_base import KnowledgeBase

router = APIRouter()


@router.post("/conversations", response_model=ConversationResponse)
async def create_conversation(
    conversation_data: ConversationCreate,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Create a new conversation"""
    new_conversation = Conversation(
        user_id=current_user.id,
        title=conversation_data.title,
        ai_provider=conversation_data.ai_provider,
        model=conversation_data.model,
        system_prompt=conversation_data.system_prompt,
        settings=conversation_data.settings,
    )

    db.add(new_conversation)
    await db.commit()
    await db.refresh(new_conversation)

    return new_conversation


@router.get("/conversations", response_model=List[ConversationResponse])
async def get_conversations(
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
    skip: int = 0,
    limit: int = 50
):
    """Get all conversations for the current user"""
    result = await db.execute(
        select(Conversation)
        .where(Conversation.user_id == current_user.id)
        .order_by(desc(Conversation.updated_at))
        .offset(skip)
        .limit(limit)
    )
    conversations = result.scalars().all()
    return conversations


@router.get("/conversations/{conversation_id}", response_model=ConversationResponse)
async def get_conversation(
    conversation_id: int,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Get a specific conversation"""
    result = await db.execute(
        select(Conversation).where(
            (Conversation.id == conversation_id) &
            (Conversation.user_id == current_user.id)
        )
    )
    conversation = result.scalar_one_or_none()

    if not conversation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conversation not found"
        )

    return conversation


@router.patch("/conversations/{conversation_id}", response_model=ConversationResponse)
async def update_conversation(
    conversation_id: int,
    conversation_data: ConversationUpdate,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Update a conversation"""
    result = await db.execute(
        select(Conversation).where(
            (Conversation.id == conversation_id) &
            (Conversation.user_id == current_user.id)
        )
    )
    conversation = result.scalar_one_or_none()

    if not conversation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conversation not found"
        )

    if conversation_data.title is not None:
        conversation.title = conversation_data.title
    if conversation_data.system_prompt is not None:
        conversation.system_prompt = conversation_data.system_prompt
    if conversation_data.settings is not None:
        conversation.settings = conversation_data.settings

    await db.commit()
    await db.refresh(conversation)

    return conversation


@router.delete("/conversations/{conversation_id}")
async def delete_conversation(
    conversation_id: int,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Delete a conversation"""
    result = await db.execute(
        select(Conversation).where(
            (Conversation.id == conversation_id) &
            (Conversation.user_id == current_user.id)
        )
    )
    conversation = result.scalar_one_or_none()

    if not conversation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conversation not found"
        )

    await db.delete(conversation)
    await db.commit()

    return {"message": "Conversation deleted successfully"}


@router.get("/conversations/{conversation_id}/messages", response_model=List[MessageResponse])
async def get_messages(
    conversation_id: int,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
    skip: int = 0,
    limit: int = 100
):
    """Get all messages in a conversation"""
    # Verify conversation belongs to user
    result = await db.execute(
        select(Conversation).where(
            (Conversation.id == conversation_id) &
            (Conversation.user_id == current_user.id)
        )
    )
    conversation = result.scalar_one_or_none()

    if not conversation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conversation not found"
        )

    # Get messages
    result = await db.execute(
        select(Message)
        .where(Message.conversation_id == conversation_id)
        .order_by(Message.created_at)
        .offset(skip)
        .limit(limit)
    )
    messages = result.scalars().all()

    return messages


@router.post("/chat", response_model=ChatResponse)
async def chat(
    chat_request: ChatRequest,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Send a message and get AI response"""
    conversation = None

    # Get or create conversation
    if chat_request.conversation_id:
        result = await db.execute(
            select(Conversation).where(
                (Conversation.id == chat_request.conversation_id) &
                (Conversation.user_id == current_user.id)
            )
        )
        conversation = result.scalar_one_or_none()

        if not conversation:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Conversation not found"
            )
    else:
        # Create new conversation
        conversation = Conversation(
            user_id=current_user.id,
            title="New Conversation",
            ai_provider=chat_request.ai_provider,
            model=chat_request.model,
        )
        db.add(conversation)
        await db.commit()
        await db.refresh(conversation)

    # Save user message
    user_message = Message(
        conversation_id=conversation.id,
        user_id=current_user.id,
        role="user",
        content=chat_request.message,
    )
    db.add(user_message)
    await db.commit()
    await db.refresh(user_message)

    # Get conversation history
    result = await db.execute(
        select(Message)
        .where(Message.conversation_id == conversation.id)
        .order_by(Message.created_at)
    )
    messages = result.scalars().all()

    # Search knowledge base if provided
    kb_context = ""
    if chat_request.knowledge_base_id:
        # Verify knowledge base exists and belongs to user
        kb_result = await db.execute(
            select(KnowledgeBase).where(
                (KnowledgeBase.id == chat_request.knowledge_base_id) &
                (KnowledgeBase.user_id == current_user.id)
            )
        )
        kb = kb_result.scalar_one_or_none()

        if kb:
            # Search for relevant context
            search_results = vector_service.search(
                user_id=current_user.id,
                kb_id=chat_request.knowledge_base_id,
                query=chat_request.message,
                n_results=3
            )

            if search_results['documents']:
                kb_context = "\n\n".join(search_results['documents'])

    # Prepare messages for AI
    ai_messages = []

    # Add system prompt with knowledge base context
    system_content = conversation.system_prompt or "You are a helpful AI assistant."
    if kb_context:
        system_content += f"\n\nContext from knowledge base:\n{kb_context}\n\nUse the above context to answer the user's questions when relevant."

    ai_messages.append({"role": "system", "content": system_content})

    for msg in messages:
        ai_messages.append({"role": msg.role, "content": msg.content})

    # Generate AI response
    try:
        ai_response = await ai_service.generate_response(
            messages=ai_messages,
            provider=chat_request.ai_provider,
            model=chat_request.model,
            temperature=chat_request.temperature,
            max_tokens=chat_request.max_tokens,
        )

        # Save AI message
        assistant_message = Message(
            conversation_id=conversation.id,
            user_id=current_user.id,
            role="assistant",
            content=ai_response["content"],
            tokens_used=ai_response["tokens_used"],
        )
        db.add(assistant_message)

        # Update conversation title if it's the first message
        if len(messages) == 1:
            # Generate a title from the first message
            title = chat_request.message[:50] + ("..." if len(chat_request.message) > 50 else "")
            conversation.title = title

        await db.commit()
        await db.refresh(assistant_message)

        return ChatResponse(
            conversation_id=conversation.id,
            message=assistant_message,
            tokens_used=ai_response["tokens_used"],
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"AI service error: {str(e)}"
        )


@router.post("/chat/stream")
async def chat_stream(
    chat_request: ChatRequest,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Send a message and get streaming AI response"""

    async def generate():
        conversation = None

        # Get or create conversation
        if chat_request.conversation_id:
            result = await db.execute(
                select(Conversation).where(
                    (Conversation.id == chat_request.conversation_id) &
                    (Conversation.user_id == current_user.id)
                )
            )
            conversation = result.scalar_one_or_none()

            if not conversation:
                yield f"data: {json.dumps({'error': 'Conversation not found'})}\n\n"
                return
        else:
            # Create new conversation
            conversation = Conversation(
                user_id=current_user.id,
                title="New Conversation",
                ai_provider=chat_request.ai_provider,
                model=chat_request.model,
            )
            db.add(conversation)
            await db.commit()
            await db.refresh(conversation)

        # Save user message
        user_message = Message(
            conversation_id=conversation.id,
            user_id=current_user.id,
            role="user",
            content=chat_request.message,
        )
        db.add(user_message)
        await db.commit()

        # Get conversation history
        result = await db.execute(
            select(Message)
            .where(Message.conversation_id == conversation.id)
            .order_by(Message.created_at)
        )
        messages = result.scalars().all()

        # Prepare messages for AI
        ai_messages = []
        if conversation.system_prompt:
            ai_messages.append({"role": "system", "content": conversation.system_prompt})

        for msg in messages:
            ai_messages.append({"role": msg.role, "content": msg.content})

        # Stream AI response
        full_response = ""
        try:
            async for chunk in ai_service.generate_stream_response(
                messages=ai_messages,
                provider=chat_request.ai_provider,
                model=chat_request.model,
                temperature=chat_request.temperature,
                max_tokens=chat_request.max_tokens,
            ):
                full_response += chunk
                yield f"data: {json.dumps({'content': chunk})}\n\n"

            # Save complete AI message
            assistant_message = Message(
                conversation_id=conversation.id,
                user_id=current_user.id,
                role="assistant",
                content=full_response,
            )
            db.add(assistant_message)
            await db.commit()

            yield f"data: {json.dumps({'done': True, 'conversation_id': conversation.id})}\n\n"

        except Exception as e:
            yield f"data: {json.dumps({'error': str(e)})}\n\n"

    return StreamingResponse(generate(), media_type="text/event-stream")
