from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from typing import List
from datetime import datetime, timedelta
import re

from app.core.database import get_db
from app.core.security import get_current_active_user
from app.models.user import User
from app.models.vendor import Vendor, Subscription, SubscriptionPlan
from app.models.conversation import Conversation
from app.models.message import Message
from app.models.knowledge_base import KnowledgeBase, Document
from app.schemas.vendor import (
    VendorCreate,
    VendorResponse,
    VendorUpdate,
    SubscriptionResponse,
    SubscriptionCreate,
    SubscriptionUpdate,
    UsageLimits,
)

router = APIRouter()


def generate_slug(name: str) -> str:
    """Generate a URL-friendly slug from a name"""
    slug = name.lower()
    slug = re.sub(r'[^\w\s-]', '', slug)
    slug = re.sub(r'[-\s]+', '-', slug)
    return slug.strip('-')


@router.post("/vendors", response_model=VendorResponse)
async def create_vendor(
    vendor_data: VendorCreate,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Create a new vendor organization"""
    # Generate slug if not provided
    slug = vendor_data.slug or generate_slug(vendor_data.name)

    # Check if slug already exists
    result = await db.execute(select(Vendor).where(Vendor.slug == slug))
    if result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Vendor with this slug already exists"
        )

    # Create vendor
    vendor = Vendor(
        name=vendor_data.name,
        slug=slug,
        email=vendor_data.email,
        description=vendor_data.description,
    )

    db.add(vendor)
    await db.commit()
    await db.refresh(vendor)

    # Assign user as vendor admin
    current_user.vendor_id = vendor.id
    current_user.role = "vendor_admin"
    await db.commit()

    # Create default free subscription
    free_plan_result = await db.execute(
        select(SubscriptionPlan).where(SubscriptionPlan.slug == "free")
    )
    free_plan = free_plan_result.scalar_one_or_none()

    if free_plan:
        subscription = Subscription(
            vendor_id=vendor.id,
            plan_id=free_plan.id,
            status="active",
            current_period_start=datetime.utcnow(),
            current_period_end=datetime.utcnow() + timedelta(days=30)
        )
        db.add(subscription)
        await db.commit()

    return vendor


@router.get("/vendors/me", response_model=VendorResponse)
async def get_my_vendor(
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Get current user's vendor"""
    if not current_user.vendor_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User is not associated with any vendor"
        )

    result = await db.execute(
        select(Vendor).where(Vendor.id == current_user.vendor_id)
    )
    vendor = result.scalar_one_or_none()

    if not vendor:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Vendor not found"
        )

    return vendor


@router.patch("/vendors/me", response_model=VendorResponse)
async def update_my_vendor(
    vendor_data: VendorUpdate,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Update current user's vendor"""
    if not current_user.vendor_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User is not associated with any vendor"
        )

    if current_user.role != "vendor_admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only vendor admins can update vendor settings"
        )

    result = await db.execute(
        select(Vendor).where(Vendor.id == current_user.vendor_id)
    )
    vendor = result.scalar_one_or_none()

    if not vendor:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Vendor not found"
        )

    # Update fields
    if vendor_data.name is not None:
        vendor.name = vendor_data.name
    if vendor_data.email is not None:
        vendor.email = vendor_data.email
    if vendor_data.description is not None:
        vendor.description = vendor_data.description
    if vendor_data.logo_url is not None:
        vendor.logo_url = vendor_data.logo_url
    if vendor_data.primary_color is not None:
        vendor.primary_color = vendor_data.primary_color
    if vendor_data.secondary_color is not None:
        vendor.secondary_color = vendor_data.secondary_color
    if vendor_data.settings is not None:
        vendor.settings = vendor_data.settings

    await db.commit()
    await db.refresh(vendor)

    return vendor


@router.get("/subscription", response_model=SubscriptionResponse)
async def get_subscription(
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Get current vendor's subscription"""
    if not current_user.vendor_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User is not associated with any vendor"
        )

    result = await db.execute(
        select(Subscription)
        .where(Subscription.vendor_id == current_user.vendor_id)
    )
    subscription = result.scalar_one_or_none()

    if not subscription:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No subscription found"
        )

    # Load plan
    plan_result = await db.execute(
        select(SubscriptionPlan).where(SubscriptionPlan.id == subscription.plan_id)
    )
    subscription.plan = plan_result.scalar_one_or_none()

    return subscription


@router.post("/subscription", response_model=SubscriptionResponse)
async def create_or_update_subscription(
    subscription_data: SubscriptionCreate,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Create or update vendor subscription"""
    if not current_user.vendor_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User is not associated with any vendor"
        )

    if current_user.role != "vendor_admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only vendor admins can manage subscriptions"
        )

    # Verify plan exists
    plan_result = await db.execute(
        select(SubscriptionPlan).where(SubscriptionPlan.id == subscription_data.plan_id)
    )
    plan = plan_result.scalar_one_or_none()

    if not plan:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Subscription plan not found"
        )

    # Get existing subscription
    result = await db.execute(
        select(Subscription).where(Subscription.vendor_id == current_user.vendor_id)
    )
    subscription = result.scalar_one_or_none()

    if subscription:
        # Update existing
        subscription.plan_id = subscription_data.plan_id
        subscription.billing_cycle = subscription_data.billing_cycle
        subscription.current_period_start = datetime.utcnow()
        subscription.current_period_end = datetime.utcnow() + timedelta(days=30)
    else:
        # Create new
        subscription = Subscription(
            vendor_id=current_user.vendor_id,
            plan_id=subscription_data.plan_id,
            billing_cycle=subscription_data.billing_cycle,
            status="active",
            current_period_start=datetime.utcnow(),
            current_period_end=datetime.utcnow() + timedelta(days=30)
        )
        db.add(subscription)

    await db.commit()
    await db.refresh(subscription)

    # Load plan
    subscription.plan = plan

    return subscription


@router.get("/usage-limits", response_model=UsageLimits)
async def get_usage_limits(
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Get current usage and limits for vendor"""
    if not current_user.vendor_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User is not associated with any vendor"
        )

    # Get subscription
    sub_result = await db.execute(
        select(Subscription).where(Subscription.vendor_id == current_user.vendor_id)
    )
    subscription = sub_result.scalar_one_or_none()

    if not subscription:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No subscription found"
        )

    # Load plan
    plan_result = await db.execute(
        select(SubscriptionPlan).where(SubscriptionPlan.id == subscription.plan_id)
    )
    plan = plan_result.scalar_one_or_none()

    # Count knowledge bases
    kb_count_result = await db.execute(
        select(func.count(KnowledgeBase.id))
        .join(User)
        .where(User.vendor_id == current_user.vendor_id)
    )
    kb_count = kb_count_result.scalar() or 0

    # Count documents
    doc_count_result = await db.execute(
        select(func.count(Document.id))
        .join(User)
        .where(User.vendor_id == current_user.vendor_id)
    )
    doc_count = doc_count_result.scalar() or 0

    return UsageLimits(
        conversations={
            "used": subscription.usage_conversations,
            "limit": plan.max_conversations_per_month,
            "percentage": (subscription.usage_conversations / plan.max_conversations_per_month * 100) if plan.max_conversations_per_month > 0 else 0
        },
        messages={
            "used": subscription.usage_messages,
            "limit": plan.max_messages_per_month,
            "percentage": (subscription.usage_messages / plan.max_messages_per_month * 100) if plan.max_messages_per_month > 0 else 0
        },
        tokens={
            "used": subscription.usage_tokens,
            "limit": plan.max_tokens_per_month,
            "percentage": (subscription.usage_tokens / plan.max_tokens_per_month * 100) if plan.max_tokens_per_month > 0 else 0
        },
        storage={
            "used": subscription.usage_storage_mb,
            "limit": plan.max_storage_mb,
            "percentage": (subscription.usage_storage_mb / plan.max_storage_mb * 100) if plan.max_storage_mb > 0 else 0
        },
        knowledge_bases={
            "used": kb_count,
            "limit": plan.max_knowledge_bases,
            "percentage": (kb_count / plan.max_knowledge_bases * 100) if plan.max_knowledge_bases > 0 else 0
        },
        documents={
            "used": doc_count,
            "limit": plan.max_documents,
            "percentage": (doc_count / plan.max_documents * 100) if plan.max_documents > 0 else 0
        }
    )
