# Quick Start Guide

## Prerequisites
- Docker and Docker Compose installed
- Git

## Getting Started (Docker - Recommended)

### 1. Clone the repository
```bash
git clone https://github.com/yourusername/cloud-optimizer.git
cd cloud-optimizer
```

### 2. Start the application
```bash
docker-compose up -d
```

### 3. Access the application
- **Frontend Dashboard**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs

### 4. Generate sample data (Optional)
```bash
# Access the backend container
docker exec -it cloud-optimizer-backend bash

# Run Python shell
python3

# Generate sample data
from app.core.database import AsyncSessionLocal
from app.utils.data_generator import DataGenerator
import asyncio

async def setup_demo():
    async with AsyncSessionLocal() as db:
        # Create sample resources
        resources = await DataGenerator.create_sample_resources(db)
        print(f"Created {len(resources)} sample resources")
        
        # Generate metrics for each resource
        for resource in resources:
            count = await DataGenerator.populate_sample_metrics(
                db, resource.id, hours=168, pattern='normal'
            )
            print(f"Generated {count} metrics for {resource.name}")

asyncio.run(setup_demo())
```

## Manual Setup (Without Docker)

### Backend Setup
```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run the server
uvicorn app.main:app --reload
```

### Frontend Setup
```bash
cd frontend

# Install dependencies
npm install

# Start development server
npm start
```

## Default Features

The application comes with:
- 4 sample cloud resources (AWS and Azure)
- Real-time resource monitoring
- AI-powered usage predictions
- Cost optimization recommendations
- What-if scenario simulation

## API Usage Examples

### List all resources
```bash
curl http://localhost:8000/api/v1/resources
```

### Get predictions for a resource
```bash
curl -X POST http://localhost:8000/api/v1/predictions \
  -H "Content-Type: application/json" \
  -d '{"resource_id": 1, "prediction_days": 7}'
```

### Get optimization recommendations
```bash
curl http://localhost:8000/api/v1/optimize/1
```

### Run a simulation
```bash
curl -X POST http://localhost:8000/api/v1/simulate \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Test Scenario",
    "resource_ids": [1, 2],
    "duration_days": 30
  }'
```

## Stopping the Application

```bash
docker-compose down
```

## Troubleshooting

### Port already in use
If ports 3000 or 8000 are already in use, modify `docker-compose.yml` to use different ports.

### Database issues
Delete the database file and restart:
```bash
docker-compose down
rm backend/cloud_optimizer.db
docker-compose up -d
```

### Frontend not loading
Clear browser cache and reload, or try:
```bash
docker-compose restart frontend
```

## Next Steps

1. Explore the Dashboard to see resource utilization
2. Check Predictions tab for AI forecasts
3. Review Optimization recommendations for cost savings
4. Run What-If simulations to test scenarios

For more details, see the main [README.md](README.md)
