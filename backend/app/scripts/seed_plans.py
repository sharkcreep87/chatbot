"""
Seed script to create default subscription plans
Run this once to populate the database with subscription tiers
"""
import asyncio
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from app.core.config import settings
from app.models.vendor import SubscriptionPlan
from app.core.database import Base


async def create_default_plans():
    """Create default subscription plans"""

    engine = create_async_engine(settings.DATABASE_URL, echo=True)
    async_session = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with async_session() as session:
        # Check if plans already exist
        from sqlalchemy import select
        result = await session.execute(select(SubscriptionPlan))
        existing_plans = result.scalars().all()

        if existing_plans:
            print("Plans already exist. Skipping creation.")
            return

        plans = [
            SubscriptionPlan(
                name="Free",
                slug="free",
                description="Perfect for getting started with basic chatbot features",
                price_monthly=0.0,
                price_yearly=0.0,
                max_users=1,
                max_conversations_per_month=50,
                max_messages_per_month=500,
                max_tokens_per_month=25000,
                max_knowledge_bases=1,
                max_documents=5,
                max_storage_mb=50,
                features={
                    "analytics": False,
                    "api_access": False,
                    "custom_branding": False,
                    "priority_support": False,
                    "advanced_analytics": False,
                },
                ai_models=["gpt-3.5-turbo"],
                is_popular=False,
                display_order=1,
                is_active=True,
            ),
            SubscriptionPlan(
                name="Basic",
                slug="basic",
                description="Great for individuals and small teams",
                price_monthly=29.0,
                price_yearly=290.0,
                max_users=3,
                max_conversations_per_month=500,
                max_messages_per_month=5000,
                max_tokens_per_month=250000,
                max_knowledge_bases=5,
                max_documents=50,
                max_storage_mb=500,
                features={
                    "analytics": True,
                    "api_access": False,
                    "custom_branding": False,
                    "priority_support": False,
                    "advanced_analytics": False,
                },
                ai_models=["gpt-3.5-turbo", "gpt-4"],
                is_popular=False,
                display_order=2,
                is_active=True,
            ),
            SubscriptionPlan(
                name="Pro",
                slug="pro",
                description="Best for growing businesses and teams",
                price_monthly=99.0,
                price_yearly=990.0,
                max_users=10,
                max_conversations_per_month=5000,
                max_messages_per_month=50000,
                max_tokens_per_month=1000000,
                max_knowledge_bases=20,
                max_documents=200,
                max_storage_mb=2000,
                features={
                    "analytics": True,
                    "api_access": True,
                    "custom_branding": True,
                    "priority_support": True,
                    "advanced_analytics": True,
                },
                ai_models=["gpt-3.5-turbo", "gpt-4", "gpt-4-turbo-preview", "claude-3-opus-20240229"],
                is_popular=True,
                display_order=3,
                is_active=True,
            ),
            SubscriptionPlan(
                name="Enterprise",
                slug="enterprise",
                description="Custom solution for large organizations",
                price_monthly=499.0,
                price_yearly=4990.0,
                max_users=100,
                max_conversations_per_month=100000,
                max_messages_per_month=1000000,
                max_tokens_per_month=10000000,
                max_knowledge_bases=100,
                max_documents=1000,
                max_storage_mb=10000,
                features={
                    "analytics": True,
                    "api_access": True,
                    "custom_branding": True,
                    "priority_support": True,
                    "advanced_analytics": True,
                    "dedicated_support": True,
                    "sla": True,
                    "custom_integrations": True,
                },
                ai_models=["gpt-3.5-turbo", "gpt-4", "gpt-4-turbo-preview", "claude-3-opus-20240229", "claude-3-sonnet-20240229"],
                is_popular=False,
                display_order=4,
                is_active=True,
            ),
        ]

        for plan in plans:
            session.add(plan)

        await session.commit()
        print(f"Created {len(plans)} subscription plans successfully!")


if __name__ == "__main__":
    asyncio.run(create_default_plans())
