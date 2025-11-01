# Quick Start Guide - Async Refactored AI Services

## Prerequisites
- Python 3.10+
- RabbitMQ server running (localhost:5672)
- MongoDB server running (localhost:27017)
- Virtual environment activated

## Installation

### Option A: Using UV (Recommended - 10-100x faster ⚡)

```powershell
# Install UV (if not already installed)
pip install uv

# Create virtual environment
uv venv

# Activate
.\.venv\Scripts\Activate.ps1

# Install dependencies (much faster than pip!)
uv pip install -e .
```

**See `UV_SETUP.md` for detailed UV guide.**

### Option B: Using pip (Traditional)

```powershell
# Create virtual environment
python -m venv .venv

# Activate
.\.venv\Scripts\Activate.ps1

# If you get execution policy error:
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope Process

# Install dependencies
pip install -r requirements.txt
```

This will install:
- `fastapi` - Web framework
- `uvicorn` - ASGI server
- `aio-pika` - Async RabbitMQ client
- `motor` - Async MongoDB driver
- `transformers` - Hugging Face models
- `sentence-transformers` - Sentence embeddings
- `torch` - PyTorch for ML models

**Note:** With UV, installation is 10-100x faster than pip!

### 3. Configure Environment
Create/update `.env` file in project root:
```env
# MongoDB
MONGO_URI=mongodb://localhost:27017/MUSIC_APP
DATABASE_NAME=MUSIC_APP

# RabbitMQ
RABBITMQ_HOST=localhost
RABBITMQ_PORT=5672
```

## Testing Setup

### Run Connection Tests (Recommended)
```powershell
# From project root
cd D:\ProjectPersonal\Social_Website\ai_services

# Run test script
python test_async_setup.py
```

Expected output:
```
============================================================
ASYNC REFACTOR VERIFICATION TEST
============================================================

=== Testing MongoDB (motor) ===
✅ MongoDB connection successful: {'ok': 1.0}
✅ Found 0 posts in database

=== Testing RabbitMQ (aio-pika) ===
✅ RabbitMQ connection successful: ...
✅ Channel created: ...
✅ Test queue declared: test-queue
✅ Test queue deleted

=== Testing Worker Setup ===
✅ Exchange declared: test-exchange
✅ Input queue declared: test-input-queue
✅ Result queue declared: test-result-queue

=== Cleanup ===
✅ All connections closed

============================================================
TEST SUMMARY
============================================================
MongoDB             : ✅ PASS
RabbitMQ            : ✅ PASS
Worker Setup        : ✅ PASS

🎉 ALL TESTS PASSED!
============================================================
```

## Running the Application

### Development Mode (with auto-reload)
```powershell
# From project root
cd D:\ProjectPersonal\Social_Website\ai_services

# Start server
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

### Production Mode (no reload)
```powershell
uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 1
```

## Verification

### 1. Check API Health
Open browser: http://localhost:8000/

Expected response:
```json
{
  "status": "ok",
  "message": "API and all async workers are running."
}
```

### 2. Check Worker Status
Open browser: http://localhost:8000/health

Expected response:
```json
{
  "status": "healthy",
  "workers": 3,
  "active_tasks": 3
}
```

### 3. Check Logs
You should see in the terminal:
```
--- Khởi động tất cả AI Workers (Async)... ---
Đã khởi chạy Worker ToxicDetector trong async task.
Đã khởi chạy Worker HintPost trong async task.
Đã khởi chạy Worker EncodePost trong async task.
✅ Đã kết nối RabbitMQ thành công.
Worker Toxic Detector [toxic-detect-queue] đang chạy...
Worker Hint Post [hint-post-queue] đang chạy...
Worker Encode Post [encode-post-queue] đang chạy...
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
```

## Testing Workers

### Send Test Message via Python
```python
import pika
import json

# Connect to RabbitMQ
connection = pika.BlockingConnection(
    pika.ConnectionParameters('localhost')
)
channel = connection.channel()

# Test Toxic Detection
message = {"content": "This is a test message"}
channel.basic_publish(
    exchange='toxic-detect-exchange',
    routing_key='toxic-detect-queue',
    body=json.dumps(message)
)
print("✅ Sent toxic detection test message")

# Test Post Encoding
message = {
    "_id": "507f1f77bcf86cd799439011",
    "content": "Sample post content"
}
channel.basic_publish(
    exchange='encode-post-exchange',
    routing_key='encode-post-queue',
    body=json.dumps(message)
)
print("✅ Sent encoding test message")

connection.close()
```

### Check Worker Logs
You should see processing messages in the terminal:
```
[ToxicDetector] Processing: This is a test message...
[ToxicDetector] Result: non-toxic
[EncodePost] Generated embedding for post 507f1f77bcf86cd799439011
[EncodePost] Updated: {...}
```

## Troubleshooting

### Problem: Import errors for aio_pika or motor
**Solution:**
```powershell
pip install --upgrade aio-pika motor
```

### Problem: RabbitMQ connection refused
**Solution:**
1. Check RabbitMQ is running: `rabbitmq-server`
2. Check port 5672 is open
3. Verify RABBITMQ_HOST in .env

### Problem: MongoDB connection timeout
**Solution:**
1. Check MongoDB is running: `mongod`
2. Check port 27017 is open
3. Verify MONGO_URI in .env

### Problem: Workers not starting
**Solution:**
1. Check logs for detailed error messages
2. Run `python test_async_setup.py` to isolate the issue
3. Ensure all dependencies are installed

### Problem: Model loading too slow
**Solution:**
See `ASYNC_MIGRATION.md` for model caching strategies

## Performance Tuning

### Adjust Prefetch Count
In `consumer.py`, modify `prefetch_count`:
```python
await channel.set_qos(prefetch_count=10)  # Process up to 10 messages concurrently
```

### Adjust Worker Count
Duplicate workers for higher throughput:
```python
# In main.py WORKERS_CONFIG
WORKERS_CONFIG = [
    (detectToxicConsumer, "ToxicDetector-1"),
    (detectToxicConsumer, "ToxicDetector-2"),  # Duplicate
    (hintPostConsumer, "HintPost"),
    (encodePostConsumer, "EncodePost"),
]
```

## Stopping the Server

Press `CTRL+C` in the terminal. You should see:
```
--- Báo hiệu dừng cho tất cả AI Workers... ---
Worker Toxic Detector đã dừng hoàn toàn.
Worker Hint Post đã dừng hoàn toàn.
worker Encode Post đã dừng hoàn toàn.
--- Tất cả AI Workers đã dừng an toàn. ---
🛑 Kết nối RabbitMQ đã đóng an toàn.
🛑 Kết nối MongoDB đã đóng an toàn.
```

## Next Steps

1. ✅ Complete installation and testing
2. ✅ Verify all workers are running
3. 📝 Update producer code in Node.js backend (if needed)
4. 📊 Set up monitoring (optional)
5. 🚀 Deploy to production environment

## Support

- See `ASYNC_MIGRATION.md` for detailed migration info
- Check application logs for error details
- Test connections with `test_async_setup.py`
