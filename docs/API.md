# API Documentation

## Base URL
```
http://localhost:8000/api/v1
```

## Authentication
Currently, the API does not require authentication. This can be added in production.

## Endpoints

### Resources

#### List Resources
```http
GET /resources
```

**Query Parameters:**
- `skip` (int): Number of records to skip (default: 0)
- `limit` (int): Maximum number of records to return (default: 100)
- `provider` (string): Filter by cloud provider (aws, azure, gcp)
- `is_active` (boolean): Filter by active status

**Response:**
```json
[
  {
    "id": 1,
    "name": "prod-web-server-01",
    "provider": "aws",
    "resource_type": "vm",
    "instance_type": "t3.medium",
    "region": "us-east-1",
    "vcpus": 2,
    "memory_gb": 4,
    "cost_per_hour": 0.0416,
    "created_at": "2024-01-15T10:30:00",
    "updated_at": "2024-01-15T10:30:00",
    "is_active": true,
    "tags": {"environment": "production"}
  }
]
```

#### Create Resource
```http
POST /resources
```

**Request Body:**
```json
{
  "name": "new-server-01",
  "provider": "aws",
  "resource_type": "vm",
  "instance_type": "t3.medium",
  "region": "us-east-1",
  "vcpus": 2,
  "memory_gb": 4,
  "cost_per_hour": 0.0416,
  "tags": {"team": "backend"}
}
```

#### Get Resource
```http
GET /resources/{resource_id}
```

#### Update Resource
```http
PUT /resources/{resource_id}
```

#### Delete Resource
```http
DELETE /resources/{resource_id}
```

### Metrics

#### Submit Metrics
```http
POST /metrics
```

**Request Body:**
```json
{
  "resource_id": 1,
  "timestamp": "2024-01-15T10:30:00",
  "cpu_usage": 45.5,
  "memory_usage": 62.3,
  "network_in_mb": 125.4,
  "network_out_mb": 89.2,
  "disk_read_ops": 450,
  "disk_write_ops": 230,
  "disk_usage": 68.5,
  "request_count": 5420,
  "error_rate": 0.2,
  "response_time_ms": 145.3
}
```

#### Get Metrics
```http
GET /metrics/{resource_id}?hours=24
```

**Query Parameters:**
- `hours` (int): Number of hours of historical data (default: 24)

### Predictions

#### Generate Prediction
```http
POST /predictions
```

**Request Body:**
```json
{
  "resource_id": 1,
  "prediction_days": 7
}
```

**Response:**
```json
{
  "resource_id": 1,
  "prediction_start": "2024-01-15T10:30:00",
  "prediction_end": "2024-01-22T10:30:00",
  "predictions": [
    {
      "timestamp": "2024-01-15T11:00:00",
      "cpu_usage": 48.2,
      "memory_usage": 65.1,
      "network_usage": 120.5,
      "confidence": 0.89
    }
  ],
  "model_accuracy": 0.92,
  "recommendations": [
    "CPU usage expected to peak at 87% in 48 hours"
  ]
}
```

#### Get Predictions
```http
GET /predictions/{resource_id}?limit=5
```

### Optimization

#### Get Recommendations
```http
GET /optimize/{resource_id}
```

Or with custom parameters:

```http
POST /optimize
```

**Request Body:**
```json
{
  "resource_id": 1,
  "cost_weight": 0.6,
  "performance_weight": 0.4,
  "constraints": {}
}
```

**Response:**
```json
{
  "resource_id": 1,
  "resource_name": "prod-web-server-01",
  "current_state": {
    "instance_type": "t3.medium",
    "provider": "aws",
    "cost_per_hour": 0.0416,
    "monthly_cost": 30.37
  },
  "recommendations": [
    {
      "id": 1,
      "recommendation_type": "scale_down",
      "priority": "high",
      "current_instance_type": "t3.medium",
      "recommended_instance_type": "t3.small",
      "cost_analysis": {
        "current_monthly_cost": 30.37,
        "projected_monthly_cost": 15.18,
        "potential_savings": 15.19,
        "savings_percentage": 50.0
      },
      "performance_impact": {
        "cpu_impact": "0%",
        "memory_impact": "-50%",
        "overall_impact": "neutral",
        "risk_level": "low"
      },
      "confidence_score": 0.85,
      "reasoning": "Resource is under-utilized",
      "implementation_steps": [
        "Create snapshot/backup",
        "Stop instance",
        "Change instance type",
        "Start and verify"
      ]
    }
  ],
  "total_potential_savings": 15.19,
  "analysis_timestamp": "2024-01-15T10:30:00"
}
```

### Simulation

#### Run Simulation
```http
POST /simulate
```

**Request Body:**
```json
{
  "name": "Production Scale-Down Test",
  "description": "Test impact of downsizing production servers",
  "resource_ids": [1, 2, 3],
  "instance_type_changes": {
    "1": "t3.small"
  },
  "scaling_changes": {
    "2": 2
  },
  "duration_days": 30
}
```

**Response:**
```json
{
  "scenario_name": "Production Scale-Down Test",
  "duration_days": 30,
  "metrics": {
    "avg_cpu_usage": 42.5,
    "avg_memory_usage": 55.3,
    "peak_cpu_usage": 78.2,
    "peak_memory_usage": 82.1,
    "total_requests": 1250000,
    "avg_response_time_ms": 125.4
  },
  "cost_breakdown": {
    "compute_cost": 450.00,
    "network_cost": 25.50,
    "storage_cost": 30.00,
    "total_cost": 505.50
  },
  "comparison_to_current": {
    "cost_difference_percent": -15.5,
    "performance_difference_percent": 2.3,
    "efficiency_improvement": 18.2
  },
  "recommendations": [
    "Peak usage occurs at 2 PM - consider auto-scaling",
    "Memory utilization is stable - current sizing is optimal"
  ]
}
```

## Error Responses

All endpoints return errors in the following format:

```json
{
  "error": "Resource not found",
  "detail": "Resource with ID 999 does not exist",
  "timestamp": "2024-01-15T10:30:00"
}
```

### Status Codes

- `200` - Success
- `201` - Created
- `204` - No Content (Delete)
- `400` - Bad Request
- `404` - Not Found
- `422` - Validation Error
- `500` - Internal Server Error

## Rate Limiting

Currently not implemented. Recommended for production:
- 100 requests per minute per IP
- 1000 requests per hour per IP

## Webhooks

Future feature: Configure webhooks to receive notifications when:
- Resources exceed utilization thresholds
- Cost optimization opportunities are detected
- Anomalies are identified

## SDK Examples

### Python
```python
import requests

# List resources
response = requests.get('http://localhost:8000/api/v1/resources')
resources = response.json()

# Create resource
new_resource = {
    'name': 'api-server-01',
    'provider': 'aws',
    'instance_type': 't3.medium',
    'region': 'us-east-1'
}
response = requests.post('http://localhost:8000/api/v1/resources', json=new_resource)

# Get predictions
prediction_request = {
    'resource_id': 1,
    'prediction_days': 7
}
response = requests.post('http://localhost:8000/api/v1/predictions', json=prediction_request)
predictions = response.json()
```

### JavaScript
```javascript
// List resources
const resources = await fetch('http://localhost:8000/api/v1/resources')
  .then(res => res.json());

// Get optimization recommendations
const recommendations = await fetch('http://localhost:8000/api/v1/optimize/1')
  .then(res => res.json());
```

### cURL
```bash
# List resources
curl http://localhost:8000/api/v1/resources

# Create resource
curl -X POST http://localhost:8000/api/v1/resources \
  -H "Content-Type: application/json" \
  -d '{
    "name": "test-server",
    "provider": "aws",
    "instance_type": "t3.micro",
    "region": "us-east-1"
  }'

# Get predictions
curl -X POST http://localhost:8000/api/v1/predictions \
  -H "Content-Type: application/json" \
  -d '{
    "resource_id": 1,
    "prediction_days": 7
  }'
```
