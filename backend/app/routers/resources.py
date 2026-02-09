"""
Resources API router
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete
from typing import List
from datetime import datetime

from app.core.database import get_db
from app.models.database import Resource
from app.schemas.api import (
    ResourceCreate,
    ResourceUpdate,
    Resource as ResourceSchema,
    ErrorResponse
)

router = APIRouter()


@router.get("/", response_model=List[ResourceSchema])
async def list_resources(
    skip: int = 0,
    limit: int = 100,
    provider: str = None,
    is_active: bool = None,
    db: AsyncSession = Depends(get_db)
):
    """List all resources with optional filtering"""
    query = select(Resource)
    
    if provider:
        query = query.where(Resource.provider == provider)
    if is_active is not None:
        query = query.where(Resource.is_active == is_active)
    
    query = query.offset(skip).limit(limit)
    
    result = await db.execute(query)
    resources = result.scalars().all()
    
    return resources


@router.post("/", response_model=ResourceSchema, status_code=status.HTTP_201_CREATED)
async def create_resource(
    resource: ResourceCreate,
    db: AsyncSession = Depends(get_db)
):
    """Create a new resource"""
    # Check if resource with same name exists
    existing = await db.execute(
        select(Resource).where(Resource.name == resource.name)
    )
    if existing.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Resource with name '{resource.name}' already exists"
        )
    
    # Create new resource
    db_resource = Resource(**resource.model_dump())
    db.add(db_resource)
    await db.commit()
    await db.refresh(db_resource)
    
    return db_resource


@router.get("/{resource_id}", response_model=ResourceSchema)
async def get_resource(
    resource_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Get a specific resource by ID"""
    result = await db.execute(
        select(Resource).where(Resource.id == resource_id)
    )
    resource = result.scalar_one_or_none()
    
    if not resource:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Resource with ID {resource_id} not found"
        )
    
    return resource


@router.put("/{resource_id}", response_model=ResourceSchema)
async def update_resource(
    resource_id: int,
    resource_update: ResourceUpdate,
    db: AsyncSession = Depends(get_db)
):
    """Update a resource"""
    # Check if resource exists
    result = await db.execute(
        select(Resource).where(Resource.id == resource_id)
    )
    resource = result.scalar_one_or_none()
    
    if not resource:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Resource with ID {resource_id} not found"
        )
    
    # Update resource
    update_data = resource_update.model_dump(exclude_unset=True)
    update_data['updated_at'] = datetime.utcnow()
    
    await db.execute(
        update(Resource)
        .where(Resource.id == resource_id)
        .values(**update_data)
    )
    await db.commit()
    
    # Refresh and return
    await db.refresh(resource)
    return resource


@router.delete("/{resource_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_resource(
    resource_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Delete a resource"""
    result = await db.execute(
        select(Resource).where(Resource.id == resource_id)
    )
    resource = result.scalar_one_or_none()
    
    if not resource:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Resource with ID {resource_id} not found"
        )
    
    await db.execute(
        delete(Resource).where(Resource.id == resource_id)
    )
    await db.commit()
    
    return None
