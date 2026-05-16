from qdrant_client import QdrantClient
from langchain_huggingface import HuggingFaceEmbeddings
from src.config import settings

# 1. Hàm kết nối Qdrant Cloud (giữ nguyên)
def get_qdrant_client():
    return QdrantClient(
        url=settings.qdrant_cloud_url,
        api_key=settings.qdrant_api_key
    )

# 2. Đổi sang dùng Local Embedding chạy trên máy
def get_embeddings():
    # Sử dụng model đa ngôn ngữ cực tốt và nhẹ (hỗ trợ tiếng Việt và tiếng Anh)
    return HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-MiniLM-L6-v2",
        # Nếu đã cài CUDA chuẩn, đổi "cpu" thành "cuda" để ép chạy trên RTX 3050
        model_kwargs={'device': 'cpu'},
        encode_kwargs={'normalize_embeddings': True}
    )