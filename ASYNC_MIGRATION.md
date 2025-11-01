# Async Migration Guide

## Overview
The codebase has been refactored to use async/await patterns with:
- **motor**: Async MongoDB driver (replaces pymongo)
- **aio-pika**: Async RabbitMQ client (replaces pika)

## Key Changes

### 1. Database Connections

#### MongoDB (`app/database/connectMongodb.py`)
- Changed from `pymongo.MongoClient` to `motor.motor_asyncio.AsyncIOMotorClient`
- All database operations now use `await`:
  ```python
  # Before
  db = get_database()
  posts = list(db["posts"].find({}))
  
  # After
  db = await get_database()
  cursor = db["posts"].find({})
  posts = await cursor.to_list(length=None)
  ```

#### RabbitMQ (`app/database/connectRabbitmq.py`)
- Changed from `pika.BlockingConnection` to `aio_pika.connect_robust`
- All channel operations now use `await`
- Added proper connection pooling with `connect_robust` for auto-reconnection

### 2. Consumer Workers (`app/consumer.py`)

All three workers converted to async:
- `detectToxicConsumer` → async function
- `hintPostConsumer` → async function  
- `encodePostConsumer` → async function

**Key differences:**
- Message handling uses `async with message.process()` context manager
- No manual ack/nack needed - handled by context manager
- Publishing uses `await exchange.publish(...)`
- Queue consuming uses `await input_q.consume(callback)`

### 3. Main Application (`app/main.py`)

- Workers now run as **asyncio tasks** instead of threads
- Uses `asyncio.Event` instead of `threading.Event`
- Startup/shutdown is fully async:
  ```python
  await run_all_ai_workers()
  await stop_all_ai_workers()
  ```

## Benefits

✅ **Better Performance**: Non-blocking I/O for database and message queue operations  
✅ **Higher Throughput**: Can handle more concurrent messages  
✅ **Resource Efficiency**: Uses fewer threads/processes  
✅ **Better Error Handling**: Async context managers handle ack/nack automatically  
✅ **Scalability**: Easier to scale with async patterns

## Installation & Running

### 1. Install Dependencies
```powershell
# Activate virtual environment
.\.venv\Scripts\Activate.ps1

# Install async libraries
pip install -r requirements.txt
```

### 2. Run the Server
```powershell
# From project root
cd D:\ProjectPersonal\Social_Website\ai_services

# Run with uvicorn
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

### 3. Health Check
Visit: http://localhost:8000/health

Response:
```json
{
  "status": "healthy",
  "workers": 3,
  "active_tasks": 3
}
```

## Testing

### Send Test Message to RabbitMQ

**Toxic Detection:**
```python
import pika
import json

connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
channel = connection.channel()

message = {"content": "This is a test message"}
channel.basic_publish(
    exchange='toxic-detect-exchange',
    routing_key='toxic-detect-queue',
    body=json.dumps(message)
)
```

**Encode Post:**
```python
message = {
    "_id": "507f1f77bcf86cd799439011",
    "content": "Sample post content for embedding"
}
channel.basic_publish(
    exchange='encode-post-exchange',
    routing_key='encode-post-queue',
    body=json.dumps(message)
)
```

## Troubleshooting

### Import Errors
If you see `Import "aio_pika" could not be resolved`:
```powershell
pip install aio-pika motor
```

### Connection Issues
- Ensure RabbitMQ is running: `rabbitmq-server`
- Ensure MongoDB is running: `mongod`
- Check environment variables in `.env`

### Worker Not Starting
- Check logs for detailed error messages
- Verify exchange/queue names match in producer code
- Test connections independently

## Migration Checklist

- [x] Install motor and aio-pika
- [x] Refactor MongoDB connection to async
- [x] Refactor RabbitMQ connection to async
- [x] Convert all worker functions to async
- [x] Update main.py to use asyncio tasks
- [ ] Update any service layers that call database (if needed)
- [ ] Update producer code in Node.js backend (if needed)
- [ ] Performance testing
- [ ] Load testing

## Performance Comparison

Expected improvements:
- **Throughput**: 2-3x higher message processing rate
- **Latency**: Lower p99 latency under load
- **Resource Usage**: 30-50% less memory with async I/O
- **Concurrent Connections**: Can handle 10x more simultaneous DB/MQ operations

## Next Steps

1. Test each worker with real messages
2. Monitor performance metrics
3. Adjust prefetch_count and concurrency settings if needed
4. Consider adding connection pooling for even better performance
5. Add metrics/monitoring (Prometheus, Grafana)
