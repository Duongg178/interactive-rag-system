import os
from langchain_community.document_loaders import PyPDFLoader
from langchain_experimental.text_splitter import SemanticChunker
from langchain_qdrant import QdrantVectorStore
from src.store import get_embeddings, get_qdrant_client
from src.config import settings


def process_and_index_pdf(file_path: str, original_filename: str):
    # original_filename là tên gốc của file (ví dụ: deepseek.pdf)
    print(f"1. Đang đọc file PDF: {original_filename}")
    loader = PyPDFLoader(file_path)
    documents = loader.load()

    # Gắn thẻ tên file vào metadata để sau này dùng làm bộ lọc
    for doc in documents:
        doc.metadata["source"] = original_filename

    print("2. Đang băm văn bản bằng Semantic Chunking...")
    embeddings = get_embeddings()
    text_splitter = SemanticChunker(embeddings, breakpoint_threshold_type="interquartile")
    chunks = text_splitter.split_documents(documents)

    print("3. Đang đẩy lên Qdrant Cloud...")
    client = get_qdrant_client()

    # --- ĐÃ SỬA LỖI Ở ĐÂY ---
    # Bước 3.1: Khởi tạo kết nối với Vector Store (không nạp dữ liệu vội)
    vector_store = QdrantVectorStore(
        client=client,
        collection_name=settings.qdrant_collection,
        embedding=embeddings
    )

    # Bước 3.2: Dùng lệnh add_documents để nối thêm dữ liệu mới vào DB cũ
    vector_store.add_documents(documents=chunks)

    print("✅ Hoàn tất! Tài liệu của bạn đã được đưa lên mây thành công.")

    return len(chunks)