# Architecture Overview

## 🎯 Design Philosophy

This project prioritizes:
1. **Simplicity** - Works out of the box with minimal dependencies
2. **Extensibility** - Easy to add real cloud integrations later
3. **Learning** - Clear code structure for understanding full-stack development
4. **Demo-Ready** - Includes realistic simulated data

## 🏗️ Current Implementation

### What's Real vs Simulated

| Component | Status | Details |
|-----------|--------|---------|
| FastAPI Backend | ✅ Real | Production-ready REST API |
| React Frontend | ✅ Real | Full interactive dashboard |
| SQLite Database | ✅ Real | Stores resources, metrics, predictions |
| Statistical Predictions | ✅ Real | Moving average + trend analysis |
| Cost Optimization | ✅ Real | Rule-based recommendation engine |
| Resource Metrics | 🎭 Simulated | Generated test data (easy to replace with real) |
| Cloud API Integration | 🎭 Simulated | Uses hardcoded instance catalogs |
| LSTM Predictions | 🔧 Optional | Available if you install TensorFlow |

### Architecture Layers

```
┌─────────────────────────────────────────────────────────────┐
│                   Frontend (React)                           │
│  - Material-UI components                                    │
│  - Recharts for visualization                                │
│  - Axios for API calls                                       │
└─────────────────────────────────────────────────────────────┘
                            │ HTTP/REST
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                API Layer (FastAPI)                           │
│  - 5 routers (resources, predictions, optimization, etc.)    │
│  - Pydantic validation                                       │
│  - Async request handling                                    │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│              Business Logic Layer                            │
│  - OptimizationService (rule-based recommendations)          │
│  - MLService (statistical predictions)                       │
│  - DataGenerator (simulation)                                │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│              Data Layer (SQLAlchemy + SQLite)                │
│  - Resource, Metric, Prediction, Recommendation models       │
│  - Async database operations                                 │
└─────────────────────────────────────────────────────────────┘
```

## 🤖 ML/AI Implementation

### Current: Statistical Methods (Default)

**Prediction Algorithm:**
```python
# Time-series forecasting without ML
1. Calculate mean, std, trend from historical data
2. Project trend forward
3. Add hourly/daily seasonality (sine wave)
4. Add small random noise
5. Clamp to valid range (0-100%)

Result: Fast, interpretable, works well for demo
```

**Optimization Algorithm:**
```python
# Rule-based recommendation engine
1. Calculate avg/max CPU and memory usage
2. Apply threshold rules:
   - avg < 20% → scale_down
   - max > 80% → scale_up
   - moderate → rightsize
3. Find matching instance types from catalog
4. Calculate cost savings
5. Rank by weighted score (cost vs performance)

Result: Clear, explainable recommendations
```

### Optional: LSTM Neural Network

If you install TensorFlow:
```python
# LSTM model for more sophisticated predictions
- 2 LSTM layers (50 units each)
- Dropout for regularization
- Trained on 24-hour sequences
- Predicts next 7 days

Pros: Better at capturing complex patterns
Cons: Requires TensorFlow (500MB+), slower
```

## 📊 Data Flow

### Adding a New Resource

```
User Input (Frontend)
    ↓
POST /api/v1/resources
    ↓
Pydantic Validation
    ↓
SQLAlchemy Insert
    ↓
Database (SQLite)
    ↓
Return Resource Object
```

### Generating Predictions

```
User Clicks "Predict" (Frontend)
    ↓
POST /api/v1/predictions {resource_id, days}
    ↓
Fetch Historical Metrics (last 7 days)
    ↓
ML Service: Statistical Prediction
    ↓
Generate hourly predictions for next N days
    ↓
Save to Prediction table
    ↓
Return predictions + recommendations
```

### Getting Optimization Recommendations

```
User Views Resource (Frontend)
    ↓
GET /api/v1/optimize/{resource_id}
    ↓
Fetch Recent Metrics
    ↓
OptimizationService:
  - Analyze usage patterns
  - Apply threshold rules
  - Find candidate instances
  - Calculate cost impact
    ↓
Return ranked recommendations
```

## 🗄️ Database Schema

```sql
-- Resources (cloud VMs/instances)
CREATE TABLE resources (
    id INTEGER PRIMARY KEY,
    name TEXT UNIQUE,
    provider TEXT,  -- aws, azure, gcp
    instance_type TEXT,
    vcpus INTEGER,
    memory_gb REAL,
    cost_per_hour REAL,
    is_active BOOLEAN,
    created_at TIMESTAMP,
    tags JSON
);

-- Metrics (time-series data)
CREATE TABLE metrics (
    id INTEGER PRIMARY KEY,
    resource_id INTEGER,
    timestamp TIMESTAMP,
    cpu_usage REAL,
    memory_usage REAL,
    network_in_mb REAL,
    network_out_mb REAL,
    -- ... more metrics
    FOREIGN KEY (resource_id) REFERENCES resources(id)
);

-- Predictions (AI forecasts)
CREATE TABLE predictions (
    id INTEGER PRIMARY KEY,
    resource_id INTEGER,
    prediction_start TIMESTAMP,
    prediction_end TIMESTAMP,
    predicted_cpu JSON,  -- array of values
    predicted_memory JSON,
    cpu_confidence REAL,
    FOREIGN KEY (resource_id) REFERENCES resources(id)
);

-- Recommendations (optimization suggestions)
CREATE TABLE recommendations (
    id INTEGER PRIMARY KEY,
    resource_id INTEGER,
    recommendation_type TEXT,
    current_instance_type TEXT,
    recommended_instance_type TEXT,
    cost_savings_per_month REAL,
    confidence_score REAL,
    FOREIGN KEY (resource_id) REFERENCES resources(id)
);
```

## 🔌 Extension Points

### Want to Add Real Cloud Integration?

1. **AWS**:
```python
# In services/cloud_service.py
import boto3
ec2 = boto3.client('ec2')
metrics = cloudwatch.get_metric_data(...)
```

2. **Azure**:
```python
from azure.mgmt.compute import ComputeManagementClient
from azure.mgmt.monitor import MonitorManagementClient
# Fetch real VM metrics
```

### Want to Add User Authentication?

1. Add JWT middleware
2. Create User model
3. Associate resources with users
4. Update all endpoints with user filtering

### Want to Use PostgreSQL?

1. Change DATABASE_URL in .env
2. Install: `pip install asyncpg`
3. Everything else works the same (SQLAlchemy handles it)

## 📏 Design Decisions

### Why SQLite?
- Zero configuration
- Perfect for development and demos
- Easy to upgrade to PostgreSQL later
- Supports async with aiosqlite

### Why Statistical Methods over ML?
- Faster predictions (no model loading)
- More interpretable results
- Sufficient accuracy for most use cases
- Much smaller dependencies

### Why Simulated Metrics?
- Demo-ready out of the box
- No cloud credentials needed
- Easy to understand data flow
- Simple to replace with real APIs

### Why No Authentication?
- Simpler onboarding
- Focus on core features
- Easy to add later
- Not needed for single-user demo

## 🚀 Production Considerations

If deploying to production:

1. **Add Authentication** - JWT tokens, user management
2. **Use PostgreSQL** - Better for multi-user, transactions
3. **Add Rate Limiting** - Prevent API abuse
4. **Enable HTTPS** - SSL certificates
5. **Add Monitoring** - Application metrics, error tracking
6. **Real Cloud APIs** - Replace simulated data
7. **Caching** - Redis for frequent queries
8. **Background Jobs** - Celery for long-running tasks

## 📈 Scalability

Current architecture handles:
- ✅ 100s of resources
- ✅ 1000s of metrics per resource
- ✅ Multiple concurrent users (with uvicorn workers)

For larger scale:
- Add database connection pooling
- Use Redis for caching
- Horizontal scaling with load balancer
- Separate read/write database replicas

---

**Summary**: This is a well-structured, working application that uses pragmatic choices (statistical methods, simulated data, SQLite) to deliver a functional demo. It's designed to be easily extended with real integrations when needed.
