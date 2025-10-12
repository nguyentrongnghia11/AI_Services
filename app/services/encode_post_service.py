from ..utils.model_loader import model_hint

def encode_post_content(content: str):
    """
    Nhận nội dung bài viết, trả về embedding vector
    """
    embedding = model_hint.encode(
        content,
        convert_to_tensor=True,
        normalize_embeddings=True
    )
    return embedding
