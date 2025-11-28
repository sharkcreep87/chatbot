from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Optional, Dict, Any, List


# Vendor Schemas
class VendorBase(BaseModel):
    name: str
    email: EmailStr
    description: Optional[str] = None
    slug: Optional[str] = None


class VendorCreate(VendorBase):
    pass


class VendorUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[EmailStr] = None
    description: Optional[str] = None
    logo_url: Optional[str] = None
    primary_color: Optional[str] = None
    secondary_color: Optional[str] = None
    settings: Optional[Dict[str, Any]] = None


class VendorResponse(VendorBase):
    id: int
    slug: str
    logo_url: Optional[str]
    primary_color: str
    secondary_color: str
    settings: Dict[str, Any]
    is_active: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# Subscription Plan Schemas
class SubscriptionPlanBase(BaseModel):
    name: str
    slug: str
    description: Optional[str] = None
    price_monthly: float = 0.0
    price_yearly: float = 0.0


class SubscriptionPlanCreate(SubscriptionPlanBase):
    max_users: int = 1
    max_conversations_per_month: int = 100
    max_messages_per_month: int = 1000
    max_tokens_per_month: int = 50000
    max_knowledge_bases: int = 1
    max_documents: int = 10
    max_storage_mb: int = 100
    features: Dict[str, Any] = {}
    ai_models: List[str] = ["gpt-3.5-turbo"]


class SubscriptionPlanResponse(SubscriptionPlanBase):
    id: int
    currency: str
    max_users: int
    max_conversations_per_month: int
    max_messages_per_month: int
    max_tokens_per_month: int
    max_knowledge_bases: int
    max_documents: int
    max_storage_mb: int
    features: Dict[str, Any]
    ai_models: List[str]
    is_popular: bool
    display_order: int
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True


# Subscription Schemas
class SubscriptionBase(BaseModel):
    plan_id: int
    billing_cycle: str = "monthly"


class SubscriptionCreate(SubscriptionBase):
    pass


class SubscriptionUpdate(BaseModel):
    plan_id: Optional[int] = None
    billing_cycle: Optional[str] = None
    status: Optional[str] = None


class SubscriptionResponse(BaseModel):
    id: int
    vendor_id: int
    plan_id: int
    status: str
    billing_cycle: str
    usage_conversations: int
    usage_messages: int
    usage_tokens: int
    usage_storage_mb: float
    current_period_start: datetime
    current_period_end: Optional[datetime]
    trial_end: Optional[datetime]
    created_at: datetime
    updated_at: datetime
    plan: SubscriptionPlanResponse

    class Config:
        from_attributes = True


class UsageLimits(BaseModel):
    conversations: Dict[str, Any]
    messages: Dict[str, Any]
    tokens: Dict[str, Any]
    storage: Dict[str, Any]
    knowledge_bases: Dict[str, Any]
    documents: Dict[str, Any]
