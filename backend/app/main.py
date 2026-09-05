from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import select

from .database import engine, Base, AsyncSessionLocal
from . import models
from .analytics import get_business_metrics
from .chief_growth_agent import run_chief_growth_agent


@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as connection:
        await connection.run_sync(Base.metadata.create_all)

    yield

    await engine.dispose()


app = FastAPI(
    title="ShopControl API",
    description="Autonomous AI Growth Platform for Online Merchants",
    version="1.0.0",
    lifespan=lifespan
)


# ---------------------------------------------------------
# CORS
# ---------------------------------------------------------

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://localhost:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ---------------------------------------------------------
# BASIC
# ---------------------------------------------------------

@app.get("/")
def root():
    return {
        "message": "ShopControl API is running",
        "status": "online"
    }


@app.get("/health")
def health():
    return {
        "status": "healthy"
    }


# ---------------------------------------------------------
# ANALYTICS
# ---------------------------------------------------------

@app.get("/analytics")
async def analytics():
    async with AsyncSessionLocal() as session:
        metrics = await get_business_metrics(session)

        return metrics


# ---------------------------------------------------------
# AI GROWTH AGENT
# ---------------------------------------------------------

@app.get("/ai/growth")
async def ai_growth():
    result = await run_chief_growth_agent()

    return result


# ---------------------------------------------------------
# OFFERS
# ---------------------------------------------------------

@app.get("/offers")
async def get_offers():
    async with AsyncSessionLocal() as session:

        result = await session.execute(
            select(models.Offer)
            .order_by(models.Offer.id.desc())
        )

        offers = result.scalars().all()

        return [
            {
                "id": offer.id,
                "merchant_id": offer.merchant_id,
                "name": offer.name,
                "discount_percent": offer.discount_percent,
                "max_discount_percent": offer.max_discount_percent,
                "min_margin_percent": offer.min_margin_percent,
                "budget": offer.budget,
                "active": offer.active,
                "created_at": offer.created_at.isoformat()
                if offer.created_at else None
            }
            for offer in offers
        ]


# ---------------------------------------------------------
# EXPERIMENTS
# ---------------------------------------------------------

@app.get("/experiments")
async def get_experiments():
    async with AsyncSessionLocal() as session:

        result = await session.execute(
            select(models.Experiment)
            .order_by(models.Experiment.id.desc())
        )

        experiments = result.scalars().all()

        return [
            {
                "id": experiment.id,
                "merchant_id": experiment.merchant_id,
                "name": experiment.name,
                "hypothesis": experiment.hypothesis,

                "control_visitors": experiment.control_visitors,
                "variant_visitors": experiment.variant_visitors,

                "control_conversions": experiment.control_conversions,
                "variant_conversions": experiment.variant_conversions,

                "control_conversion": experiment.control_conversion,
                "variant_conversion": experiment.variant_conversion,

                "control_revenue": experiment.control_revenue,
                "variant_revenue": experiment.variant_revenue,

                "conversion_lift": experiment.conversion_lift,
                "revenue_lift": experiment.revenue_lift,

                "p_value": experiment.p_value,
                "statistically_significant": experiment.statistically_significant,

                "status": experiment.status,
                "winner": experiment.winner,

                "created_at": experiment.created_at.isoformat()
                if experiment.created_at else None
            }
            for experiment in experiments
        ]


# ---------------------------------------------------------
# AI ACTIONS
# ---------------------------------------------------------

@app.get("/ai/actions")
async def get_ai_actions():
    async with AsyncSessionLocal() as session:

        result = await session.execute(
            select(models.AIAction)
            .order_by(models.AIAction.id.desc())
        )

        actions = result.scalars().all()

        return [
            {
                "id": action.id,
                "merchant_id": action.merchant_id,
                "agent_name": action.agent_name,
                "action_type": action.action_type,
                "description": action.description,
                "status": action.status,
                "expected_impact": action.expected_impact,
                "actual_impact": action.actual_impact,
                "created_at": action.created_at.isoformat()
                if action.created_at else None
            }
            for action in actions
        ]