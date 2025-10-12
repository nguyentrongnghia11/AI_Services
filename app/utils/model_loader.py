# utils/model_loader.py
from sentence_transformers import SentenceTransformer
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM

print("🔹 Loading AI models...")

# Model dùng để tạo embedding cho bài viết
model_hint = SentenceTransformer('all-MiniLM-L6-v2')

# Model phát hiện ngôn ngữ độc hại (ViHateT5)
tokenizer_detect = AutoTokenizer.from_pretrained("tarudesu/ViHateT5-base-HSD")
model_detect = AutoModelForSeq2SeqLM.from_pretrained("tarudesu/ViHateT5-base-HSD")

print("✅ All models loaded successfully.")
