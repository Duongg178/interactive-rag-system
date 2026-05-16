import google.generativeai as genai
from qdrant_client import QdrantClient
from src.config import settings

print("Đang kiểm tra kết nối, vui lòng đợi...\n")

# 1. Kiểm tra kết nối Gemini
try:
    genai.configure(api_key=settings.google_api_key)
    model = genai.GenerativeModel(settings.gemini_model)
    response = model.generate_content("Hãy nói đúng 4 chữ: 'Gemini đã sẵn sàng!'")
    print(f"✅ Gemini: {response.text.strip()}")
except Exception as e:
    print(f"❌ Lỗi kết nối Gemini: {e}")

# 2. Kiểm tra kết nối Qdrant Cloud
try:
    client = QdrantClient(
        url=settings.qdrant_cloud_url,
        api_key=settings.qdrant_api_key
    )
    # Thử lấy danh sách các collection (dù hiện tại đang trống)
    collections = client.get_collections()
    print("✅ Qdrant: Kết nối thành công tới Cloud Database!")
except Exception as e:
    print(f"❌ Lỗi kết nối Qdrant: {e}")