# Installation Guide

## Choose Your Installation Method

### 🚀 Option 1: Docker (Easiest - Recommended)

**Best for**: Quick start, demos, no Python/Node setup needed

```bash
# 1. Clone the repo
git clone https://github.com/yourusername/cloud-optimizer.git
cd cloud-optimizer

# 2. Start everything
docker-compose up -d

# 3. Access the app
# Frontend: http://localhost:3000
# Backend: http://localhost:8000/docs
```

That's it! Everything is configured and running.

---

### 💨 Option 2: Lightweight Local Setup (Fastest)

**Best for**: Development, minimal dependencies, fast installation

**Installation size**: ~50MB of Python packages

#### Backend

```bash
cd backend

# Create virtual environment
python3.9 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install minimal dependencies (fast!)
pip install -r requirements.txt

# Start backend
uvicorn app.main:app --reload
```

#### Frontend

```bash
cd frontend

npm install
npm start
```

**What you get**:
- ✅ Full working application
- ✅ Statistical predictions (no TensorFlow)
- ✅ Cost optimization
- ✅ Dashboard and all features
- ✅ Simulated metrics for demo

**What's NOT included**:
- ❌ LSTM neural network predictions
- ❌ Real cloud API integration

---

### 🔬 Option 3: Full Setup (With ML/Cloud SDKs)

**Best for**: Production use, real cloud integration, LSTM predictions

**Installation size**: ~550MB (includes TensorFlow)

#### Backend

```bash
cd backend

python3.9 -m venv venv
source venv/bin/activate

# Install ALL dependencies
pip install -r requirements-full.txt

# Or install specific extras:
pip install -r requirements.txt
pip install tensorflow==2.15.0  # For LSTM
pip install boto3                # For AWS
pip install azure-mgmt-compute  # For Azure
```

#### Frontend
Same as lightweight setup.

**What you get**:
- ✅ Everything from lightweight
- ✅ LSTM predictions with TensorFlow
- ✅ Real AWS/Azure SDK support (needs credentials)
- ✅ Advanced analytics

---

## 📝 Post-Installation

### Verify Installation

```bash
# Check backend
curl http://localhost:8000/health
# Should return: {"status":"healthy"}

# Check frontend
curl http://localhost:3000
# Should load React app
```

### Generate Sample Data

```bash
# Access Python shell in backend directory
cd backend
python

# Run this:
from app.core.database import AsyncSessionLocal
from app.utils.data_generator import DataGenerator
import asyncio

async def setup():
    async with AsyncSessionLocal() as db:
        resources = await DataGenerator.create_sample_resources(db)
        for r in resources:
            await DataGenerator.populate_sample_metrics(db, r.id, 168, 'normal')
        print(f"Created {len(resources)} resources with sample data!")

asyncio.run(setup())
```

---

## 🔧 Configuration

### Environment Variables

Create `.env` in the backend directory:

```bash
# Minimal required
DATABASE_URL=sqlite+aiosqlite:///./cloud_optimizer.db
DEBUG=True

# Optional: AWS (if using real integration)
# AWS_ACCESS_KEY_ID=your-key
# AWS_SECRET_ACCESS_KEY=your-secret

# Optional: Azure (if using real integration)  
# AZURE_SUBSCRIPTION_ID=your-sub-id
```

---

## 🐛 Troubleshooting

### "uvicorn not found"

```bash
pip install uvicorn[standard]
```

### "Module not found: tensorflow"

You don't need TensorFlow! The app works fine without it.

If you want LSTM predictions:
```bash
pip install tensorflow==2.15.0
```

### "Port already in use"

Change ports in `docker-compose.yml` or use different ports:

```bash
# Backend on different port
uvicorn app.main:app --port 8001

# Frontend on different port
PORT=3001 npm start
```

### Database errors

Delete and recreate:
```bash
rm backend/cloud_optimizer.db
# Restart the backend
```

---

## 📦 Installation Comparison

| Feature | Lightweight | Full | Docker |
|---------|-------------|------|--------|
| Install time | 2 min | 5-10 min | 5 min |
| Disk space | ~50 MB | ~550 MB | ~1 GB |
| Dependencies | 10 | 25+ | All included |
| TensorFlow | ❌ | ✅ | Optional |
| Cloud SDKs | ❌ | ✅ | Optional |
| Difficulty | Easy | Medium | Easiest |

**Recommendation**: Start with **Lightweight** or **Docker**. Add TensorFlow later only if you need it.

---

## 🚀 Next Steps

After installation:

1. Visit http://localhost:3000 for the dashboard
2. Check http://localhost:8000/docs for API documentation
3. Generate sample data (see above)
4. Explore the features!

See [QUICKSTART.md](../QUICKSTART.md) for usage guide.
