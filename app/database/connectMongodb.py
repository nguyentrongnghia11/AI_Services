import os
import pymongo
from dotenv import load_dotenv
from pymongo.errors import ConnectionFailure 

load_dotenv() 

# Đọc cấu hình từ môi trường
MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017/MUSIC_APP") 
DATABASE_NAME = os.getenv("DATABASE_NAME", "MUSIC_APP")

# Biến cấp module để lưu trữ kết nối (Singleton)
_mongo_client = None

def get_mongo_client():
    """Tạo hoặc trả về đối tượng MongoClient đã tồn tại."""
    global _mongo_client
    if _mongo_client is None:
        try:
            _mongo_client = pymongo.MongoClient(
                MONGO_URI,
                serverSelectionTimeoutMS=5000
            )
            # Kiểm tra kết nối
            _mongo_client.admin.command('ping')
            print("✅ Kết nối MongoDB thành công.")
        except (ConnectionFailure) as e:
            print(f"❌ Lỗi kết nối MongoDB: {e}")
            raise
    return _mongo_client

def get_database():
    """Trả về đối tượng database."""
    client = get_mongo_client()
    return client[DATABASE_NAME]

def close_mongo_client():
    """
    Đóng kết nối MongoDB một cách an toàn khi ứng dụng tắt (Shutdown).
    Hàm này được gọi trong sự kiện Lifespan Shutdown của FastAPI.
    """
    global _mongo_client
    if _mongo_client is not None:
        _mongo_client.close()
        _mongo_client = None
        print("🛑 Kết nối MongoDB đã đóng an toàn.")
