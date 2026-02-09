"""
Optimization API router
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from datetime import datetime, timedelta

from app.core.database import get_db
from app.models.database import Resource, Metric
from app.schemas.api import OptimizationRequest, OptimizationResponse, RecommendationDetail, CostAnalysis, PerformanceImpact
from app.services.optimization_service import OptimizationService

router = APIRouter()
optimization_service = OptimizationService()


@router.post("/", response_model=OptimizationResponse)
async def optimize_resource(
    opt_request: OptimizationRequest,
    db: AsyncSession = Depends(get_db)
):
    """Generate optimization recommendations for a resource"""
    # Get resource
    result = await db.execute(
        select(Resource).where(Resource.id == opt_request.resource_id)
    )
    resource = result.scalar_one_or_none()
    
    if not resource:
        raise HTTPException(status_code=404, detail="Resource not found")
    
    # Get metrics from last 7 days
    start_date = datetime.utcnow() - timedelta(days=7)
    metrics_result = await db.execute(
        select(Metric)
        .where(
            and_(
                Metric.resource_id == opt_request.resource_id,
                Metric.timestamp >= start_date
            )
        )
        .order_by(Metric.timestamp)
    )
    metrics = metrics_result.scalars().all()
    
    if not metrics:
        raise HTTPException(status_code=400, detail="Insufficient metrics data")
    
    # Convert to dict
    resource_dict = {
        'id': resource.id,
        'name': resource.name,
        'provider': resource.provider.value,
        'instance_type': resource.instance_type,
        'cost_per_hour': resource.cost_per_hour
    }
    
    metrics_dict = [
        {
            'cpu_usage': m.cpu_usage,
            'memory_usage': m.memory_usage,
            'timestamp': m.timestamp
        }
        for m in metrics
    ]
    
    # Generate recommendations
    recommendations = await optimization_service.generate_recommendations(
        resource_dict,
        metrics_dict,
        cost_weight=opt_request.cost_weight,
        performance_weight=opt_request.performance_weight
    )
    
    # Format response
    formatted_recommendations = []
    total_savings = 0
    
    for rec in recommendations:
        cost_analysis = CostAnalysis(
            current_monthly_cost=rec['current_cost_per_hour'] * 730,
            projected_monthly_cost=rec.get('recommended_cost_per_hour', 0) * 730,
            potential_savings=rec['cost_savings_per_month'],
            savings_percentage=(rec['cost_savings_per_month'] / (rec['current_cost_per_hour'] * 730) * 100) if rec['current_cost_per_hour'] > 0 else 0
        )
        
        perf_impact = PerformanceImpact(
            cpu_impact=rec['details'].get('vcpu_change_percent', 0),
            memory_impact=rec['details'].get('memory_change_percent', 0),
            overall_impact=rec['performance_impact'],
            risk_level='low' if rec['confidence_score'] > 0.8 else 'medium'
        )
        
        formatted_rec = RecommendationDetail(
            id=len(formatted_recommendations) + 1,
            recommendation_type=rec['recommendation_type'],
            priority=rec['priority'],
            current_instance_type=rec['current_instance_type'],
            recommended_instance_type=rec.get('recommended_instance_type', 'N/A'),
            cost_analysis=cost_analysis,
            performance_impact=perf_impact,
            confidence_score=rec['confidence_score'],
            reasoning=rec['reasoning'],
            implementation_steps=rec['implementation_steps']
        )
        
        formatted_recommendations.append(formatted_rec)
        total_savings += rec['cost_savings_per_month']
    
    return OptimizationResponse(
        resource_id=resource.id,
        resource_name=resource.name,
        current_state={
            'instance_type': resource.instance_type,
            'provider': resource.provider.value,
            'cost_per_hour': resource.cost_per_hour,
            'monthly_cost': resource.cost_per_hour * 730
        },
        recommendations=formatted_recommendations,
        total_potential_savings=total_savings,
        analysis_timestamp=datetime.utcnow()
    )


@router.get("/{resource_id}", response_model=OptimizationResponse)
async def get_optimization(
    resource_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Get optimization recommendations with default parameters"""
    opt_request = OptimizationRequest(
        resource_id=resource_id,
        cost_weight=0.6,
        performance_weight=0.4
    )
    return await optimize_resource(opt_request, db)
