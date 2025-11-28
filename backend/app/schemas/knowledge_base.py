from pydantic import BaseModel
from datetime import datetime
from typing import Optional, Dict, Any, List


class KnowledgeBaseBase(BaseModel):
    name: str
    description: Optional[str] = None


class KnowledgeBaseCreate(KnowledgeBaseBase):
    pass


class KnowledgeBaseUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None


class KnowledgeBaseResponse(KnowledgeBaseBase):
    id: int
    user_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class DocumentBase(BaseModel):
    filename: str
    file_type: str
    file_size: int


class DocumentCreate(DocumentBase):
    knowledge_base_id: int


class DocumentResponse(DocumentBase):
    id: int
    knowledge_base_id: int
    user_id: int
    file_path: str
    processed: int
    metadata: Dict[str, Any]
    created_at: datetime

    class Config:
        from_attributes = True


class DocumentWithContent(DocumentResponse):
    content: Optional[str] = None


class AnalyticsResponse(BaseModel):
    total_conversations: int
    total_messages: int
    total_tokens_used: int
    messages_by_day: List[Dict[str, Any]]
    model_usage: Dict[str, int]
    conversation_stats: Dict[str, Any]
    recent_activity: List[Dict[str, Any]]
