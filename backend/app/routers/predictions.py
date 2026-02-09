"""
Predictions API router
"""
from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from datetime import datetime, timedelta
from typing import List

from app.core.database import get_db
from app.models.database import Resource, Metric, Prediction
from app.schemas.api import PredictionRequest, PredictionResponse, PredictionPoint
from app.services.ml_service import MLService

router = APIRouter()


def get_ml_service(request: Request) -> MLService:
    """Get ML service from app state"""
    return request.app.state.ml_service


@router.post("/", response_model=PredictionResponse)
async def create_prediction(
    request: PredictionRequest,
    db: AsyncSession = Depends(get_db),
    ml_service: MLService = Depends(get_ml_service)
):
    """Generate predictions for a resource"""
    # Check if resource exists
    result = await db.execute(
        select(Resource).where(Resource.id == request.resource_id)
    )
    resource = result.scalar_one_or_none()
    
    if not resource:
        raise HTTPException(status_code=404, detail="Resource not found")
    
    # Get historical metrics (last 7 days)
    start_date = datetime.utcnow() - timedelta(days=7)
    metrics_result = await db.execute(
        select(Metric)
        .where(
            and_(
                Metric.resource_id == request.resource_id,
                Metric.timestamp >= start_date
            )
        )
        .order_by(Metric.timestamp)
    )
    metrics = metrics_result.scalars().all()
    
    if not metrics:
        raise HTTPException(
            status_code=400,
            detail="Insufficient historical data for predictions"
        )
    
    # Convert to dict format
    metrics_data = [
        {
            'cpu_usage': m.cpu_usage,
            'memory_usage': m.memory_usage,
            'network_in_mb': m.network_in_mb or 0,
            'network_out_mb': m.network_out_mb or 0,
            'timestamp': m.timestamp
        }
        for m in metrics
    ]
    
    # Generate predictions
    prediction_hours = request.prediction_days * 24
    
    cpu_predictions, cpu_confidence = await ml_service.predict_usage(
        metrics_data, 'cpu', prediction_hours
    )
    memory_predictions, memory_confidence = await ml_service.predict_usage(
        metrics_data, 'memory', prediction_hours
    )
    
    # Calculate network predictions (simple average-based)
    avg_network = sum(m['network_in_mb'] + m['network_out_mb'] for m in metrics_data) / len(metrics_data)
    network_predictions = [avg_network] * prediction_hours
    
    # Create prediction points
    start_time = datetime.utcnow()
    prediction_points = []
    
    for i in range(prediction_hours):
        point = PredictionPoint(
            timestamp=start_time + timedelta(hours=i),
            cpu_usage=cpu_predictions[i],
            memory_usage=memory_predictions[i],
            network_usage=network_predictions[i],
            confidence=(cpu_confidence + memory_confidence) / 2
        )
        prediction_points.append(point)
    
    # Save prediction to database
    db_prediction = Prediction(
        resource_id=request.resource_id,
        prediction_start=start_time,
        prediction_end=start_time + timedelta(days=request.prediction_days),
        predicted_cpu=cpu_predictions,
        predicted_memory=memory_predictions,
        predicted_network=network_predictions,
        cpu_confidence=cpu_confidence,
        memory_confidence=memory_confidence,
        model_version="1.0",
        training_samples=len(metrics)
    )
    db.add(db_prediction)
    await db.commit()
    
    # Generate recommendations based on predictions
    recommendations = []
    
    max_predicted_cpu = max(cpu_predictions)
    avg_predicted_cpu = sum(cpu_predictions) / len(cpu_predictions)
    
    if max_predicted_cpu > 85:
        recommendations.append(
            f"⚠️ Predicted CPU usage will exceed 85% (peak: {max_predicted_cpu:.1f}%). Consider scaling up."
        )
    elif avg_predicted_cpu < 20:
        recommendations.append(
            f"💡 Predicted average CPU usage is low ({avg_predicted_cpu:.1f}%). Consider downsizing to save costs."
        )
    
    max_predicted_memory = max(memory_predictions)
    if max_predicted_memory > 85:
        recommendations.append(
            f"⚠️ Predicted memory usage will exceed 85% (peak: {max_predicted_memory:.1f}%). Monitor closely."
        )
    
    return PredictionResponse(
        resource_id=request.resource_id,
        prediction_start=start_time,
        prediction_end=start_time + timedelta(days=request.prediction_days),
        predictions=prediction_points,
        model_accuracy=(cpu_confidence + memory_confidence) / 2,
        recommendations=recommendations
    )


@router.get("/{resource_id}", response_model=List[PredictionResponse])
async def get_predictions(
    resource_id: int,
    limit: int = 5,
    db: AsyncSession = Depends(get_db)
):
    """Get historical predictions for a resource"""
    result = await db.execute(
        select(Prediction)
        .where(Prediction.resource_id == resource_id)
        .order_by(Prediction.created_at.desc())
        .limit(limit)
    )
    predictions = result.scalars().all()
    
    response_list = []
    for pred in predictions:
        # Reconstruct prediction points
        points = []
        timestamps = []
        current_time = pred.prediction_start
        
        for i in range(len(pred.predicted_cpu)):
            points.append(PredictionPoint(
                timestamp=current_time + timedelta(hours=i),
                cpu_usage=pred.predicted_cpu[i],
                memory_usage=pred.predicted_memory[i],
                network_usage=pred.predicted_network[i] if pred.predicted_network else 0,
                confidence=(pred.cpu_confidence + pred.memory_confidence) / 2
            ))
        
        response_list.append(PredictionResponse(
            resource_id=resource_id,
            prediction_start=pred.prediction_start,
            prediction_end=pred.prediction_end,
            predictions=points,
            model_accuracy=(pred.cpu_confidence + pred.memory_confidence) / 2,
            recommendations=[]
        ))
    
    return response_list
