import asyncio
from fastapi import FastAPI
from contextlib import asynccontextmanager
import uvicorn
import os
from .consumer import detectToxicConsumer, hintPostConsumer, encodePostConsumer 
from .database.connectMongodb import close_mongo_client
from .database.connectRabbitmq import close_rabbitmq_connection


# --- CÁC BIẾN QUẢN LÝ WORKER ---
WORKER_TASKS = []
STOP_EVENTS = []
WORKERS_CONFIG = [
    (detectToxicConsumer, "ToxicDetector"),
    (hintPostConsumer, "HintPost"),
    (encodePostConsumer, "EncodePost"),
]


async def run_all_ai_workers():
    """Khởi động tất cả các Worker RabbitMQ trong các task async."""
    global WORKER_TASKS, STOP_EVENTS
    WORKER_TASKS = []
    STOP_EVENTS = []
    
    print("--- Khởi động tất cả AI Workers (Async)... ---")
    
    for worker_func, name in WORKERS_CONFIG:
        # Tạo Event riêng cho Worker này
        stop_event = asyncio.Event() 
        STOP_EVENTS.append(stop_event)
        
        # Tạo async task
        task = asyncio.create_task(
            worker_func(stop_event),
            name=f"Worker-{name}"
        )
        WORKER_TASKS.append(task)
        
        print(f"Đã khởi chạy Worker {name} trong async task.")
        await asyncio.sleep(0.1)


async def stop_all_ai_workers():
    """Báo hiệu tất cả các Worker dừng lại một cách an toàn."""
    global STOP_EVENTS, WORKER_TASKS
    print("--- Báo hiệu dừng cho tất cả AI Workers... ---")
    
    for event in STOP_EVENTS:
        event.set()
    
    # Đợi tất cả tasks hoàn thành
    if WORKER_TASKS:
        await asyncio.gather(*WORKER_TASKS, return_exceptions=True)
    
    print("--- Tất cả AI Workers đã dừng an toàn. ---")


# --- DEFINITION LIFESPAN HANDLER ---
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Xử lý các sự kiện Vòng đời: Khởi động Worker và Dừng Worker an toàn."""
    # STARTUP: Khởi chạy tất cả các Worker
    await run_all_ai_workers()
    
    # Yield để ứng dụng FastAPI bắt đầu xử lý request
    yield 
    
    # SHUTDOWN: Dọn dẹp và Tắt các Worker
    await stop_all_ai_workers()
    await close_rabbitmq_connection()
    await close_mongo_client()


app = FastAPI(
    title="AI Service Worker (Integrated - Async)",
    lifespan=lifespan
)


@app.get("/")
async def root():
    return {"status": "ok", "message": "API and all async workers are running."}


@app.get("/health")
async def health():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "workers": len(WORKER_TASKS),
        "active_tasks": sum(1 for t in WORKER_TASKS if not t.done())
    }


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
