from sqlalchemy import Column, Integer, String, Boolean, DateTime, JSON, Float
from sqlalchemy.orm import relationship
from datetime import datetime
from app.core.database import Base


class Vendor(Base):
    """Vendor/Organization model for multi-tenancy"""
    __tablename__ = "vendors"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    slug = Column(String, unique=True, index=True, nullable=False)
    email = Column(String, nullable=False)
    description = Column(String, nullable=True)

    # Branding
    logo_url = Column(String, nullable=True)
    primary_color = Column(String, default="#3b82f6")
    secondary_color = Column(String, default="#1e40af")

    # Settings
    settings = Column(JSON, default={})
    is_active = Column(Boolean, default=True)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    users = relationship("User", back_populates="vendor")
    subscription = relationship("Subscription", back_populates="vendor", uselist=False)

    def __repr__(self):
        return f"<Vendor {self.name}>"


class SubscriptionPlan(Base):
    """Subscription plan templates"""
    __tablename__ = "subscription_plans"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)  # Free, Basic, Pro, Enterprise
    slug = Column(String, unique=True, index=True, nullable=False)
    description = Column(String, nullable=True)

    # Pricing
    price_monthly = Column(Float, default=0.0)
    price_yearly = Column(Float, default=0.0)
    currency = Column(String, default="USD")

    # Limits
    max_users = Column(Integer, default=1)
    max_conversations_per_month = Column(Integer, default=100)
    max_messages_per_month = Column(Integer, default=1000)
    max_tokens_per_month = Column(Integer, default=50000)
    max_knowledge_bases = Column(Integer, default=1)
    max_documents = Column(Integer, default=10)
    max_storage_mb = Column(Integer, default=100)

    # Features
    features = Column(JSON, default={})  # {"analytics": true, "api_access": false, etc.}
    ai_models = Column(JSON, default=["gpt-3.5-turbo"])  # Available AI models

    # Display
    is_popular = Column(Boolean, default=False)
    display_order = Column(Integer, default=0)
    is_active = Column(Boolean, default=True)

    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    subscriptions = relationship("Subscription", back_populates="plan")

    def __repr__(self):
        return f"<SubscriptionPlan {self.name}>"


class Subscription(Base):
    """Active subscription for a vendor"""
    __tablename__ = "subscriptions"

    id = Column(Integer, primary_key=True, index=True)
    vendor_id = Column(Integer, unique=True, nullable=False)
    plan_id = Column(Integer, nullable=False)

    # Status
    status = Column(String, default="active")  # active, canceled, expired, trialing
    billing_cycle = Column(String, default="monthly")  # monthly, yearly

    # Usage tracking
    usage_conversations = Column(Integer, default=0)
    usage_messages = Column(Integer, default=0)
    usage_tokens = Column(Integer, default=0)
    usage_storage_mb = Column(Float, default=0.0)

    # Dates
    current_period_start = Column(DateTime, default=datetime.utcnow)
    current_period_end = Column(DateTime, nullable=True)
    trial_end = Column(DateTime, nullable=True)
    canceled_at = Column(DateTime, nullable=True)

    # Payment
    stripe_customer_id = Column(String, nullable=True)
    stripe_subscription_id = Column(String, nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    vendor = relationship("Vendor", back_populates="subscription")
    plan = relationship("SubscriptionPlan", back_populates="subscriptions")

    def __repr__(self):
        return f"<Subscription vendor_id={self.vendor_id} plan_id={self.plan_id}>"

    def is_within_limits(self, limit_type: str, current_value: int = None) -> bool:
        """Check if vendor is within subscription limits"""
        if not self.plan:
            return False

        limits = {
            'conversations': (self.usage_conversations, self.plan.max_conversations_per_month),
            'messages': (self.usage_messages, self.plan.max_messages_per_month),
            'tokens': (self.usage_tokens, self.plan.max_tokens_per_month),
            'storage': (self.usage_storage_mb, self.plan.max_storage_mb),
        }

        if limit_type not in limits:
            return True

        current, maximum = limits[limit_type]
        if current_value is not None:
            current = current_value

        return current < maximum
