import pika

def get_rabbitmq_connection():
    """
    Tạo mới một kết nối RabbitMQ cho mỗi worker.
    Dùng cho môi trường local hoặc dev.
    """
    try:
        connection = pika.BlockingConnection(
            pika.ConnectionParameters(
                host="localhost",
                heartbeat=600,                 # giữ kết nối sống
                blocked_connection_timeout=300
            )
        )
        print("✅ Đã kết nối RabbitMQ local thành công.")
        return connection
    except pika.exceptions.AMQPConnectionError as e:
        print(f"❌ Lỗi kết nối RabbitMQ local: {e}")
        raise
