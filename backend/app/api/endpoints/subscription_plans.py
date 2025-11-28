from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List

from app.core.database import get_db
from app.models.vendor import SubscriptionPlan
from app.schemas.vendor import SubscriptionPlanResponse, SubscriptionPlanCreate

router = APIRouter()


@router.get("/plans", response_model=List[SubscriptionPlanResponse])
async def get_subscription_plans(
    db: AsyncSession = Depends(get_db)
):
    """Get all available subscription plans"""
    result = await db.execute(
        select(SubscriptionPlan)
        .where(SubscriptionPlan.is_active == True)
        .order_by(SubscriptionPlan.display_order)
    )
    plans = result.scalars().all()
    return plans


@router.get("/plans/{plan_id}", response_model=SubscriptionPlanResponse)
async def get_subscription_plan(
    plan_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Get a specific subscription plan"""
    result = await db.execute(
        select(SubscriptionPlan).where(SubscriptionPlan.id == plan_id)
    )
    plan = result.scalar_one_or_none()

    if not plan:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Subscription plan not found"
        )

    return plan
