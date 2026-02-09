"""
Simulation API router
"""
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
import numpy as np
from datetime import datetime, timedelta

from app.core.database import get_db
from app.schemas.api import SimulationScenario, SimulationResult, SimulationMetrics, SimulationCostBreakdown

router = APIRouter()


@router.post("/", response_model=SimulationResult)
async def run_simulation(
    scenario: SimulationScenario,
    db: AsyncSession = Depends(get_db)
):
    """Run a what-if simulation scenario"""
    
    # Simulate metrics for the duration
    hours = scenario.duration_days * 24
    
    # Generate simulated CPU usage (with daily patterns)
    cpu_values = []
    for hour in range(hours):
        hour_of_day = hour % 24
        # Higher usage during business hours
        base_cpu = 40 + 20 * np.sin(2 * np.pi * (hour_of_day - 6) / 24)
        noise = np.random.normal(0, 5)
        cpu_values.append(max(10, min(90, base_cpu + noise)))
    
    # Generate simulated memory usage
    memory_values = []
    for hour in range(hours):
        base_memory = 50 + np.random.normal(0, 10)
        memory_values.append(max(20, min(85, base_memory)))
    
    # Generate request patterns
    total_requests = 0
    response_times = []
    for hour in range(hours):
        hour_of_day = hour % 24
        # More requests during business hours
        if 8 <= hour_of_day <= 18:
            requests = int(np.random.uniform(1000, 5000))
            response_time = np.random.uniform(50, 150)
        else:
            requests = int(np.random.uniform(100, 1000))
            response_time = np.random.uniform(30, 80)
        
        total_requests += requests
        response_times.append(response_time)
    
    # Calculate metrics
    metrics = SimulationMetrics(
        avg_cpu_usage=float(np.mean(cpu_values)),
        avg_memory_usage=float(np.mean(memory_values)),
        peak_cpu_usage=float(np.max(cpu_values)),
        peak_memory_usage=float(np.max(memory_values)),
        total_requests=total_requests,
        avg_response_time_ms=float(np.mean(response_times))
    )
    
    # Calculate costs (example rates)
    compute_cost = len(scenario.resource_ids) * 0.05 * hours  # $0.05/hour per instance
    network_cost = total_requests * 0.000001  # $0.000001 per request
    storage_cost = len(scenario.resource_ids) * 10 * scenario.duration_days / 30  # $10/month storage
    
    cost_breakdown = SimulationCostBreakdown(
        compute_cost=round(compute_cost, 2),
        network_cost=round(network_cost, 2),
        storage_cost=round(storage_cost, 2),
        total_cost=round(compute_cost + network_cost + storage_cost, 2)
    )
    
    # Generate recommendations
    recommendations = []
    
    if metrics.avg_cpu_usage < 30:
        recommendations.append(
            f"CPU utilization is low ({metrics.avg_cpu_usage:.1f}%). Consider downsizing instances."
        )
    
    if metrics.peak_cpu_usage > 80:
        recommendations.append(
            f"Peak CPU usage is high ({metrics.peak_cpu_usage:.1f}%). Consider scaling up or adding auto-scaling."
        )
    
    if metrics.avg_response_time_ms > 100:
        recommendations.append(
            f"Average response time is {metrics.avg_response_time_ms:.0f}ms. Consider performance optimization."
        )
    
    # Comparison to current (example - 10% more expensive in current setup)
    comparison = {
        'cost_difference_percent': -10.0,
        'performance_difference_percent': 5.0,
        'efficiency_improvement': 15.0
    }
    
    return SimulationResult(
        scenario_name=scenario.name,
        duration_days=scenario.duration_days,
        metrics=metrics,
        cost_breakdown=cost_breakdown,
        comparison_to_current=comparison,
        recommendations=recommendations
    )
