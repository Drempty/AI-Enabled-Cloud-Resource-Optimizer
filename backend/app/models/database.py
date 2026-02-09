"""
SQLAlchemy database models
"""
from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, ForeignKey, JSON, Enum
from sqlalchemy.orm import relationship
from datetime import datetime
import enum

from app.core.database import Base


class CloudProvider(str, enum.Enum):
    """Cloud provider enumeration"""
    AWS = "aws"
    AZURE = "azure"
    GCP = "gcp"


class ResourceType(str, enum.Enum):
    """Resource type enumeration"""
    VM = "vm"
    CONTAINER = "container"
    SERVERLESS = "serverless"


class Resource(Base):
    """Cloud resource model"""
    __tablename__ = "resources"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)
    provider = Column(Enum(CloudProvider))
    resource_type = Column(Enum(ResourceType), default=ResourceType.VM)
    instance_type = Column(String)
    region = Column(String)
    vcpus = Column(Integer)
    memory_gb = Column(Float)
    cost_per_hour = Column(Float)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_active = Column(Boolean, default=True)
    tags = Column(JSON, default={})
    
    # Relationships
    metrics = relationship("Metric", back_populates="resource", cascade="all, delete-orphan")
    predictions = relationship("Prediction", back_populates="resource", cascade="all, delete-orphan")
    recommendations = relationship("Recommendation", back_populates="resource", cascade="all, delete-orphan")


class Metric(Base):
    """Resource metrics model"""
    __tablename__ = "metrics"
    
    id = Column(Integer, primary_key=True, index=True)
    resource_id = Column(Integer, ForeignKey("resources.id"), index=True)
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)
    
    # CPU metrics
    cpu_usage = Column(Float)  # percentage
    cpu_credits = Column(Float, nullable=True)
    
    # Memory metrics
    memory_usage = Column(Float)  # percentage
    memory_available_mb = Column(Float)
    
    # Network metrics
    network_in_mb = Column(Float)
    network_out_mb = Column(Float)
    
    # Disk metrics
    disk_read_ops = Column(Float)
    disk_write_ops = Column(Float)
    disk_usage = Column(Float)  # percentage
    
    # Application metrics
    request_count = Column(Integer, nullable=True)
    error_rate = Column(Float, nullable=True)
    response_time_ms = Column(Float, nullable=True)
    
    # Relationship
    resource = relationship("Resource", back_populates="metrics")


class Prediction(Base):
    """Prediction results model"""
    __tablename__ = "predictions"
    
    id = Column(Integer, primary_key=True, index=True)
    resource_id = Column(Integer, ForeignKey("resources.id"), index=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Prediction time range
    prediction_start = Column(DateTime)
    prediction_end = Column(DateTime)
    
    # Predicted metrics (JSON array of values)
    predicted_cpu = Column(JSON)
    predicted_memory = Column(JSON)
    predicted_network = Column(JSON)
    
    # Confidence scores
    cpu_confidence = Column(Float)
    memory_confidence = Column(Float)
    
    # Model metadata
    model_version = Column(String)
    training_samples = Column(Integer)
    
    # Relationship
    resource = relationship("Resource", back_populates="predictions")


class Recommendation(Base):
    """Optimization recommendations model"""
    __tablename__ = "recommendations"
    
    id = Column(Integer, primary_key=True, index=True)
    resource_id = Column(Integer, ForeignKey("resources.id"), index=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Recommendation type
    recommendation_type = Column(String)  # scale_up, scale_down, rightsize, terminate
    priority = Column(String)  # high, medium, low
    
    # Current state
    current_instance_type = Column(String)
    current_cost_per_hour = Column(Float)
    
    # Recommended state
    recommended_instance_type = Column(String)
    recommended_cost_per_hour = Column(Float)
    
    # Impact analysis
    cost_savings_per_month = Column(Float)
    performance_impact = Column(String)  # improved, neutral, degraded
    confidence_score = Column(Float)
    
    # Implementation
    is_applied = Column(Boolean, default=False)
    applied_at = Column(DateTime, nullable=True)
    
    # Details
    reasoning = Column(String)
    details = Column(JSON)
    
    # Relationship
    resource = relationship("Resource", back_populates="recommendations")


class SimulationRun(Base):
    """Simulation run tracking"""
    __tablename__ = "simulation_runs"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    description = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Simulation parameters
    parameters = Column(JSON)
    
    # Results
    results = Column(JSON)
    
    # Status
    status = Column(String)  # running, completed, failed
    completed_at = Column(DateTime, nullable=True)
