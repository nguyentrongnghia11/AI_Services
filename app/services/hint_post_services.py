from ..utils.model_loader import model_hint  # model load sẵn ở utils
from sentence_transformers import util
import torch


def get_list_homologous(post, list_posts, top_k=5):
    if not list_posts:
        return []

    # Chuyển embeddings thành tensor
    post_emb = torch.tensor(post["embedding"]).unsqueeze(0)
    all_emb = torch.tensor([p["embedding"] for p in list_posts])

    # Tính cosine similarity cho tất cả bài viết
    cosine_scores = util.cos_sim(post_emb, all_emb)[0]  # [0] vì batch size = 1

    # Lấy top_k bài có độ tương đồng cao nhất
    top_results = torch.topk(cosine_scores, k=min(top_k, len(list_posts)))

    similar_posts = []
    for score, idx in zip(top_results.values, top_results.indices):
        similar_posts.append({
            "post": list_posts[idx],
            "score": round(score.item(), 3)
        })

    return similar_posts
