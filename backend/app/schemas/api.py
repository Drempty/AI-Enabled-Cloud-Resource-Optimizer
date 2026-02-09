"""
Pydantic schemas for API request/response validation
"""
from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum


class CloudProvider(str, Enum):
    """Cloud provider enumeration"""
    AWS = "aws"
    AZURE = "azure"
    GCP = "gcp"


class ResourceType(str, Enum):
    """Resource type enumeration"""
    VM = "vm"
    CONTAINER = "container"
    SERVERLESS = "serverless"


class RecommendationType(str, Enum):
    """Recommendation type enumeration"""
    SCALE_UP = "scale_up"
    SCALE_DOWN = "scale_down"
    RIGHTSIZE = "rightsize"
    TERMINATE = "terminate"
    SPOT_INSTANCE = "spot_instance"


# Resource Schemas
class ResourceBase(BaseModel):
    """Base resource schema"""
    name: str = Field(..., min_length=1, max_length=255)
    provider: CloudProvider
    resource_type: ResourceType = ResourceType.VM
    instance_type: str
    region: str
    vcpus: Optional[int] = None
    memory_gb: Optional[float] = None
    cost_per_hour: Optional[float] = None
    tags: Optional[Dict[str, Any]] = {}


class ResourceCreate(ResourceBase):
    """Schema for creating a resource"""
    pass


class ResourceUpdate(BaseModel):
    """Schema for updating a resource"""
    name: Optional[str] = None
    instance_type: Optional[str] = None
    region: Optional[str] = None
    is_active: Optional[bool] = None
    tags: Optional[Dict[str, Any]] = None


class Resource(ResourceBase):
    """Schema for resource response"""
    id: int
    created_at: datetime
    updated_at: datetime
    is_active: bool
    
    model_config = ConfigDict(from_attributes=True)


# Metric Schemas
class MetricCreate(BaseModel):
    """Schema for creating a metric"""
    resource_id: int
    timestamp: Optional[datetime] = None
    cpu_usage: float = Field(..., ge=0, le=100)
    memory_usage: float = Field(..., ge=0, le=100)
    network_in_mb: Optional[float] = Field(0, ge=0)
    network_out_mb: Optional[float] = Field(0, ge=0)
    disk_read_ops: Optional[float] = Field(0, ge=0)
    disk_write_ops: Optional[float] = Field(0, ge=0)
    disk_usage: Optional[float] = Field(0, ge=0, le=100)
    request_count: Optional[int] = Field(None, ge=0)
    error_rate: Optional[float] = Field(None, ge=0, le=100)
    response_time_ms: Optional[float] = Field(None, ge=0)


class Metric(MetricCreate):
    """Schema for metric response"""
    id: int
    
    model_config = ConfigDict(from_attributes=True)


# Prediction Schemas
class PredictionRequest(BaseModel):
    """Schema for prediction request"""
    resource_id: int
    prediction_days: int = Field(7, ge=1, le=30)


class PredictionPoint(BaseModel):
    """Single prediction data point"""
    timestamp: datetime
    cpu_usage: float
    memory_usage: float
    network_usage: float
    confidence: float


class PredictionResponse(BaseModel):
    """Schema for prediction response"""
    resource_id: int
    prediction_start: datetime
    prediction_end: datetime
    predictions: List[PredictionPoint]
    model_accuracy: float
    recommendations: List[str]


# Optimization Schemas
class OptimizationRequest(BaseModel):
    """Schema for optimization request"""
    resource_id: int
    cost_weight: float = Field(0.6, ge=0, le=1)
    performance_weight: float = Field(0.4, ge=0, le=1)
    constraints: Optional[Dict[str, Any]] = {}


class CostAnalysis(BaseModel):
    """Cost analysis details"""
    current_monthly_cost: float
    projected_monthly_cost: float
    potential_savings: float
    savings_percentage: float


class PerformanceImpact(BaseModel):
    """Performance impact analysis"""
    cpu_impact: str
    memory_impact: str
    overall_impact: str
    risk_level: str


class RecommendationDetail(BaseModel):
    """Detailed recommendation"""
    id: int
    recommendation_type: RecommendationType
    priority: str
    current_instance_type: str
    recommended_instance_type: str
    cost_analysis: CostAnalysis
    performance_impact: PerformanceImpact
    confidence_score: float
    reasoning: str
    implementation_steps: List[str]


class OptimizationResponse(BaseModel):
    """Schema for optimization response"""
    resource_id: int
    resource_name: str
    current_state: Dict[str, Any]
    recommendations: List[RecommendationDetail]
    total_potential_savings: float
    analysis_timestamp: datetime


# Simulation Schemas
class SimulationScenario(BaseModel):
    """Simulation scenario configuration"""
    name: str
    description: Optional[str] = None
    resource_ids: List[int]
    instance_type_changes: Optional[Dict[int, str]] = {}
    scaling_changes: Optional[Dict[int, int]] = {}
    duration_days: int = Field(30, ge=1, le=365)


class SimulationMetrics(BaseModel):
    """Simulation metrics result"""
    avg_cpu_usage: float
    avg_memory_usage: float
    peak_cpu_usage: float
    peak_memory_usage: float
    total_requests: int
    avg_response_time_ms: float


class SimulationCostBreakdown(BaseModel):
    """Cost breakdown for simulation"""
    compute_cost: float
    network_cost: float
    storage_cost: float
    total_cost: float


class SimulationResult(BaseModel):
    """Simulation result"""
    scenario_name: str
    duration_days: int
    metrics: SimulationMetrics
    cost_breakdown: SimulationCostBreakdown
    comparison_to_current: Dict[str, float]
    recommendations: List[str]


# Dashboard Schemas
class DashboardSummary(BaseModel):
    """Dashboard summary statistics"""
    total_resources: int
    active_resources: int
    total_monthly_cost: float
    potential_monthly_savings: float
    avg_cpu_utilization: float
    avg_memory_utilization: float
    high_priority_recommendations: int
    anomalies_detected: int


class ResourceUtilization(BaseModel):
    """Resource utilization summary"""
    resource_id: int
    resource_name: str
    provider: str
    current_cpu: float
    current_memory: float
    avg_cpu_7d: float
    avg_memory_7d: float
    utilization_score: float


# Error Response
class ErrorResponse(BaseModel):
    """Error response schema"""
    error: str
    detail: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)
