import aio_pika
import os
from dotenv import load_dotenv

load_dotenv()

_rabbitmq_connection = None

async def get_rabbitmq_connection():
    """
    Tạo mới một kết nối RabbitMQ async cho mỗi worker.
    Dùng cho môi trường local hoặc dev.
    """
    global _rabbitmq_connection
    
    if _rabbitmq_connection is None or _rabbitmq_connection.is_closed:
        try:
            RABBITMQ_HOST = os.getenv("RABBITMQ_HOST", "localhost")
            RABBITMQ_PORT = int(os.getenv("RABBITMQ_PORT", "5672"))
            
            _rabbitmq_connection = await aio_pika.connect_robust(
                host=RABBITMQ_HOST,
                port=RABBITMQ_PORT,
                heartbeat=600,
                connection_attempts=5,
                retry_delay=2
            )
            print("✅ Đã kết nối RabbitMQ thành công.")
        except Exception as e:
            print(f"❌ Lỗi kết nối RabbitMQ: {e}")
            raise
    
    return _rabbitmq_connection

async def close_rabbitmq_connection():
    """Đóng kết nối RabbitMQ an toàn."""
    global _rabbitmq_connection
    if _rabbitmq_connection is not None and not _rabbitmq_connection.is_closed:
        await _rabbitmq_connection.close()
        _rabbitmq_connection = None
        print("🛑 Kết nối RabbitMQ đã đóng an toàn.")
