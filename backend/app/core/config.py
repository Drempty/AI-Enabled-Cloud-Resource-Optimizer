"""
Application configuration
"""
from pydantic_settings import BaseSettings
from typing import List
import os


class Settings(BaseSettings):
    """Application settings"""
    
    # Application
    APP_NAME: str = "Cloud Resource Optimizer"
    VERSION: str = "1.0.0"
    DEBUG: bool = True
    
    # API
    API_V1_PREFIX: str = "/api/v1"
    
    # Database
    DATABASE_URL: str = "sqlite+aiosqlite:///./cloud_optimizer.db"
    
    # Security
    SECRET_KEY: str = "your-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # CORS
    CORS_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://localhost:8000",
    ]
    
    # AWS Configuration
    AWS_ACCESS_KEY_ID: str = os.getenv("AWS_ACCESS_KEY_ID", "")
    AWS_SECRET_ACCESS_KEY: str = os.getenv("AWS_SECRET_ACCESS_KEY", "")
    AWS_DEFAULT_REGION: str = "us-east-1"
    
    # Azure Configuration
    AZURE_SUBSCRIPTION_ID: str = os.getenv("AZURE_SUBSCRIPTION_ID", "")
    AZURE_TENANT_ID: str = os.getenv("AZURE_TENANT_ID", "")
    
    # ML Model Settings
    MODEL_RETRAIN_INTERVAL: int = 7  # days
    PREDICTION_HORIZON: int = 7  # days
    CONFIDENCE_THRESHOLD: float = 0.85
    SEQUENCE_LENGTH: int = 24  # hours for LSTM
    
    # Optimization Settings
    COST_WEIGHT: float = 0.6
    PERFORMANCE_WEIGHT: float = 0.4
    MIN_INSTANCES: int = 1
    MAX_INSTANCES: int = 10
    
    # Metric Collection
    METRIC_RETENTION_DAYS: int = 90
    METRIC_AGGREGATION_INTERVAL: int = 5  # minutes
    
    # Simulation
    ENABLE_SIMULATION: bool = True
    SIMULATION_DATA_POINTS: int = 1000
    
    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
