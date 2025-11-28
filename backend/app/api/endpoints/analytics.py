from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, desc
from datetime import datetime, timedelta
from typing import List, Dict, Any

from app.core.database import get_db
from app.core.security import get_current_active_user
from app.models.user import User
from app.models.conversation import Conversation
from app.models.message import Message
from app.models.knowledge_base import Analytics, Document, KnowledgeBase
from app.schemas.knowledge_base import AnalyticsResponse

router = APIRouter()


@router.get("/analytics", response_model=AnalyticsResponse)
async def get_analytics(
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
    days: int = 30
):
    """Get analytics dashboard data"""

    # Calculate date range
    end_date = datetime.utcnow()
    start_date = end_date - timedelta(days=days)

    # Total conversations
    total_conversations_result = await db.execute(
        select(func.count(Conversation.id))
        .where(Conversation.user_id == current_user.id)
    )
    total_conversations = total_conversations_result.scalar() or 0

    # Total messages
    total_messages_result = await db.execute(
        select(func.count(Message.id))
        .where(Message.user_id == current_user.id)
    )
    total_messages = total_messages_result.scalar() or 0

    # Total tokens used
    total_tokens_result = await db.execute(
        select(func.sum(Message.tokens_used))
        .where(Message.user_id == current_user.id)
    )
    total_tokens_used = total_tokens_result.scalar() or 0

    # Messages by day (last N days)
    messages_by_day = []
    for i in range(days):
        day_start = start_date + timedelta(days=i)
        day_end = day_start + timedelta(days=1)

        result = await db.execute(
            select(func.count(Message.id))
            .where(
                (Message.user_id == current_user.id) &
                (Message.created_at >= day_start) &
                (Message.created_at < day_end)
            )
        )
        count = result.scalar() or 0

        messages_by_day.append({
            "date": day_start.strftime("%Y-%m-%d"),
            "count": count
        })

    # Model usage statistics
    model_usage_result = await db.execute(
        select(
            Message.metadata['model'].astext.label('model'),
            func.count(Message.id).label('count')
        )
        .where(Message.user_id == current_user.id)
        .group_by(Message.metadata['model'].astext)
    )

    model_usage = {}
    for row in model_usage_result:
        if row.model:
            model_usage[row.model] = row.count

    # Conversation stats
    avg_messages_result = await db.execute(
        select(func.avg(func.count(Message.id)))
        .where(Message.user_id == current_user.id)
        .group_by(Message.conversation_id)
    )
    avg_messages_per_conv = avg_messages_result.scalar() or 0

    # Recent activity (last 10 actions)
    recent_messages = await db.execute(
        select(Message)
        .where(Message.user_id == current_user.id)
        .order_by(desc(Message.created_at))
        .limit(10)
    )

    recent_activity = []
    for msg in recent_messages.scalars():
        recent_activity.append({
            "type": "message",
            "role": msg.role,
            "conversation_id": msg.conversation_id,
            "timestamp": msg.created_at.isoformat(),
            "tokens": msg.tokens_used
        })

    conversation_stats = {
        "total": total_conversations,
        "avg_messages": round(avg_messages_per_conv, 2),
        "total_messages": total_messages,
    }

    return AnalyticsResponse(
        total_conversations=total_conversations,
        total_messages=total_messages,
        total_tokens_used=total_tokens_used,
        messages_by_day=messages_by_day,
        model_usage=model_usage,
        conversation_stats=conversation_stats,
        recent_activity=recent_activity
    )


@router.get("/analytics/knowledge-bases")
async def get_knowledge_base_analytics(
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Get knowledge base analytics"""

    # Total knowledge bases
    total_kb_result = await db.execute(
        select(func.count(KnowledgeBase.id))
        .where(KnowledgeBase.user_id == current_user.id)
    )
    total_knowledge_bases = total_kb_result.scalar() or 0

    # Total documents
    total_docs_result = await db.execute(
        select(func.count(Document.id))
        .where(Document.user_id == current_user.id)
    )
    total_documents = total_docs_result.scalar() or 0

    # Total file size
    total_size_result = await db.execute(
        select(func.sum(Document.file_size))
        .where(Document.user_id == current_user.id)
    )
    total_size = total_size_result.scalar() or 0

    # Documents by status
    status_result = await db.execute(
        select(
            Document.processed,
            func.count(Document.id)
        )
        .where(Document.user_id == current_user.id)
        .group_by(Document.processed)
    )

    documents_by_status = {
        "pending": 0,
        "processing": 0,
        "completed": 0,
        "failed": 0
    }

    status_map = {0: "pending", 1: "processing", 2: "completed", 3: "failed"}
    for status, count in status_result:
        status_name = status_map.get(status, "unknown")
        documents_by_status[status_name] = count

    return {
        "total_knowledge_bases": total_knowledge_bases,
        "total_documents": total_documents,
        "total_size_bytes": total_size,
        "total_size_mb": round(total_size / (1024 * 1024), 2),
        "documents_by_status": documents_by_status
    }


@router.post("/analytics/track")
async def track_event(
    event_type: str,
    event_data: Dict[str, Any],
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Track a custom analytics event"""

    analytics_entry = Analytics(
        user_id=current_user.id,
        event_type=event_type,
        event_data=event_data,
        tokens_used=event_data.get('tokens_used', 0),
        model_used=event_data.get('model_used')
    )

    db.add(analytics_entry)
    await db.commit()

    return {"message": "Event tracked successfully"}
