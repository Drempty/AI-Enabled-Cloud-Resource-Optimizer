"""
Metrics API router
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from datetime import datetime, timedelta
from typing import List

from app.core.database import get_db
from app.models.database import Resource, Metric
from app.schemas.api import MetricCreate, Metric as MetricSchema

router = APIRouter()


@router.post("/", response_model=MetricSchema, status_code=201)
async def create_metric(
    metric: MetricCreate,
    db: AsyncSession = Depends(get_db)
):
    """Submit a new metric data point"""
    # Verify resource exists
    result = await db.execute(
        select(Resource).where(Resource.id == metric.resource_id)
    )
    if not result.scalar_one_or_none():
        raise HTTPException(status_code=404, detail="Resource not found")
    
    # Create metric
    db_metric = Metric(**metric.model_dump())
    db.add(db_metric)
    await db.commit()
    await db.refresh(db_metric)
    
    return db_metric


@router.get("/{resource_id}", response_model=List[MetricSchema])
async def get_metrics(
    resource_id: int,
    hours: int = 24,
    db: AsyncSession = Depends(get_db)
):
    """Get metrics for a resource"""
    start_time = datetime.utcnow() - timedelta(hours=hours)
    
    result = await db.execute(
        select(Metric)
        .where(
            and_(
                Metric.resource_id == resource_id,
                Metric.timestamp >= start_time
            )
        )
        .order_by(Metric.timestamp)
    )
    
    return result.scalars().all()
