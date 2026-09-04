from contextlib import asynccontextmanager

from fastapi import FastAPI

from .database import engine, Base, AsyncSessionLocal
from .analytics import get_business_metrics

from .database import engine, Base
from . import models


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

@app.get("/analytics")
async def analytics():

    async with AsyncSessionLocal() as session:

        metrics = await get_business_metrics(session)

        return metrics