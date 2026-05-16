from src.store import get_qdrant_client
from src.config import settings
from qdrant_client import models


def setup_qdrant_index():
    client = get_qdrant_client()
    collection_name = settings.qdrant_collection

    print(f"⏳ Đang tạo Payload Index cho trường 'metadata.source' trong collection '{collection_name}'...")

    try:
        client.create_payload_index(
            collection_name=collection_name,
            field_name="metadata.source",
            field_schema=models.PayloadSchemaType.KEYWORD,
        )
        print("✅ Tạo Index thành công! Bộ lọc của bạn đã sẵn sàng hoạt động với tốc độ ánh sáng.")
    except Exception as e:
        # Nếu đã có index rồi thì nó sẽ báo lỗi (nhưng không sao cả)
        print(f"⚠️ Thông báo từ Qdrant: {e}")


if __name__ == "__main__":
    setup_qdrant_index()