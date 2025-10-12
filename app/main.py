import threading
import time
from fastapi import FastAPI
from contextlib import asynccontextmanager
import uvicorn
import os
from threading import Event
from .consumer import detectToxicConsumer, hintPostConsumer, encodePostConsumer 

from .database.connectMongodb import close_mongo_client


# --- CÁC BIẾN QUẢN LÝ WORKER ---
# Danh sách chứa các đối tượng Event để kiểm soát việc dừng Worker
STOP_EVENTS = []
WORKERS_CONFIG = [
    (detectToxicConsumer, "ToxicDetector"),
    (hintPostConsumer, "HintPost"),
    (encodePostConsumer, "EncodePost"),
]


def run_all_ai_workers():

    global STOP_EVENTS
    STOP_EVENTS = []
    
    print("--- Khởi động tất cả AI Workers... ---")
    
    for worker_func, name in WORKERS_CONFIG:
        stop_event = threading.Event() 
        STOP_EVENTS.append(stop_event)
        
        worker_thread = threading.Thread(
            target=worker_func, 
            args=(stop_event,),
            daemon=True,
            name=f"Worker-{name}"
        )
        
        worker_thread.start()
        print(f"Đã khởi chạy Worker {name} trong luồng nền.")
        time.sleep(0.1) 


def stop_all_ai_workers():
    global STOP_EVENTS
    for event in STOP_EVENTS:
        event.set() # Bật cờ dừng
    
    time.sleep(3) 
    print("--- Tất cả AI Workers đã dừng an toàn. ---")


# --- DEFINITION LIFESPAN HANDLER ---
@asynccontextmanager
async def lifespan(app: FastAPI):
    run_all_ai_workers()
    
    # Yield để ứng dụng FastAPI bắt đầu xử lý request
    yield 
    
    stop_all_ai_workers() 
    close_mongo_client() 


app = FastAPI(
    title="AI Service Worker (Integrated)",
    lifespan=lifespan
)


@app.get("/")
def root():
    return {"status": "ok", "message": "API and all workers are running."}


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
