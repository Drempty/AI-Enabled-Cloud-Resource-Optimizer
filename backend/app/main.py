"""
Main FastAPI application entry point
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from contextlib import asynccontextmanager

from app.core.config import settings
from app.core.database import engine, Base
from app.routers import resources, predictions, optimization, metrics, simulation
from app.services.ml_service import MLService

# Initialize ML models on startup
ml_service = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events"""
    global ml_service
    
    # Startup
    print("🚀 Starting Cloud Optimizer API...")
    
    # Create database tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    # Initialize ML service
    ml_service = MLService()
    await ml_service.load_models()
    app.state.ml_service = ml_service
    
    print("✅ Application startup complete")
    
    yield
    
    # Shutdown
    print("🛑 Shutting down Cloud Optimizer API...")
    await ml_service.cleanup()
    print("✅ Application shutdown complete")


# Create FastAPI app
app = FastAPI(
    title="Cloud Resource Optimizer API",
    description="AI-powered cloud resource optimization platform",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# GZip compression
app.add_middleware(GZipMiddleware, minimum_size=1000)

# Include routers
app.include_router(resources.router, prefix="/api/v1/resources", tags=["Resources"])
app.include_router(predictions.router, prefix="/api/v1/predictions", tags=["Predictions"])
app.include_router(optimization.router, prefix="/api/v1/optimize", tags=["Optimization"])
app.include_router(metrics.router, prefix="/api/v1/metrics", tags=["Metrics"])
app.include_router(simulation.router, prefix="/api/v1/simulate", tags=["Simulation"])


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Cloud Resource Optimizer API",
        "version": "1.0.0",
        "docs": "/docs"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "ml_models_loaded": app.state.ml_service.models_loaded if hasattr(app.state, 'ml_service') else False
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
