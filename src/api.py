from fastapi import FastAPI, HTTPException, UploadFile, File
import os
import shutil
from src.schemas import AskRequest, AskResponse, BaseResponse
from src.rag import answer_question
from src.indexing import process_and_index_pdf
from fastapi.middleware.cors import CORSMiddleware
from src.store import get_qdrant_client
from src.config import settings

app = FastAPI(
    title="NotebookLM Clone API",
    description="API hệ thống RAG hỏi đáp tài liệu",
    version="1.0.0"
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # Trong thực tế nên để là ["http://localhost:3000"]
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# API 1: Kiểm tra trạng thái
@app.get("/", response_model=BaseResponse)
def root():
    return BaseResponse(message="Hệ thống NotebookLM Backend đang hoạt động!")


# API 2: Upload File PDF
@app.post("/upload", response_model=BaseResponse)
@app.post("/upload", response_model=BaseResponse)
async def upload_pdf(file: UploadFile = File(...)):
    # 1. Kiểm tra định dạng
    if not file.filename.endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Chỉ chấp nhận file PDF!")

    # 2. Xử lý đường dẫn tuyệt đối để tránh lỗi trên Windows
    # Lấy thư mục gốc của project và tạo thư mục temp bên trong
    base_dir = os.getcwd()
    temp_dir = os.path.join(base_dir, "temp")
    os.makedirs(temp_dir, exist_ok=True)

    # Tạo đường dẫn đầy đủ cho file tạm
    temp_path = os.path.join(temp_dir, file.filename)
    # Ép về đường dẫn tuyệt đối chuẩn (C:\Users\...)
    absolute_path = os.path.abspath(temp_path)

    try:
        # 3. Ghi file từ dữ liệu upload vào file tạm trên ổ cứng
        with open(absolute_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        # 4. Gọi hàm xử lý (truyền đường dẫn tuyệt đối và tên file gốc)
        chunks_count = process_and_index_pdf(absolute_path, file.filename)

        # 5. Dọn dẹp: Xóa file tạm sau khi đã nạp vào Vector DB thành công
        if os.path.exists(absolute_path):
            os.remove(absolute_path)

        return BaseResponse(
            message=f"Đã nạp thành công file {file.filename} (gồm {chunks_count} đoạn) vào bộ não!"
        )

    except Exception as e:
        # Nếu có lỗi xảy ra trong quá trình băm file hoặc đẩy lên Qdrant,
        # chúng ta vẫn phải xóa file tạm để tránh làm đầy ổ cứng.
        if os.path.exists(absolute_path):
            os.remove(absolute_path)

        print(f"❌ Lỗi xử lý PDF: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Lỗi hệ thống: {str(e)}")





# API 3: Hỏi đáp (RAG)
@app.post("/ask", response_model=AskResponse)
def ask_document(request: AskRequest):
    try:
        # SỬA LẠI: Bắt buộc phải truyền thêm request.sources vào hàm
        answer = answer_question(request.question, request.sources)
        return {"answer": answer}
    except Exception as e:
        print(f"❌ Lỗi Ask: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/files")
def get_existing_files():
    try:
        client = get_qdrant_client()

        # Quét qua database để lấy thông tin (không lấy vector nặng nề, chỉ lấy payload)
        points, _ = client.scroll(
            collection_name=settings.qdrant_collection,
            limit=10000,  # Quét tối đa 10000 đoạn văn bản
            with_payload=True,
            with_vectors=False
        )

        # Dùng 'set' để tự động loại bỏ các tên file trùng lặp
        unique_files = set()
        for point in points:
            payload = point.payload
            # Tùy phiên bản Langchain, nhãn 'source' có thể nằm trực tiếp ở payload hoặc trong dict metadata
            metadata = payload.get("metadata", payload)
            source = metadata.get("source")
            if source:
                unique_files.add(source)

        return {"files": list(unique_files)}

    except Exception as e:
        print(f"❌ Lỗi khi lấy danh sách file: {e}")
        return {"files": []}  # Trả về mảng rỗng nếu database chưa có gì
