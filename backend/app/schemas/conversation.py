from pydantic import BaseModel
from datetime import datetime
from typing import Optional, Dict, Any, List


class ConversationBase(BaseModel):
    title: Optional[str] = "New Conversation"
    ai_provider: Optional[str] = "openai"
    model: Optional[str] = "gpt-4-turbo-preview"
    system_prompt: Optional[str] = None
    settings: Optional[Dict[str, Any]] = {}


class ConversationCreate(ConversationBase):
    pass


class ConversationUpdate(BaseModel):
    title: Optional[str] = None
    system_prompt: Optional[str] = None
    settings: Optional[Dict[str, Any]] = None


class ConversationResponse(ConversationBase):
    id: int
    user_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class MessageBase(BaseModel):
    role: str
    content: str
    metadata: Optional[Dict[str, Any]] = {}


class MessageCreate(MessageBase):
    conversation_id: int


class MessageResponse(MessageBase):
    id: int
    conversation_id: int
    user_id: int
    tokens_used: int
    is_edited: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ChatRequest(BaseModel):
    message: str
    conversation_id: Optional[int] = None
    ai_provider: Optional[str] = "openai"
    model: Optional[str] = "gpt-4-turbo-preview"
    temperature: Optional[float] = 0.7
    max_tokens: Optional[int] = 2000
    stream: Optional[bool] = False


class ChatResponse(BaseModel):
    conversation_id: int
    message: MessageResponse
    tokens_used: int
