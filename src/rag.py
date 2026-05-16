from langchain_openai import ChatOpenAI
from langchain_qdrant import QdrantVectorStore
from langchain_core.prompts import PromptTemplate
from sentence_transformers import CrossEncoder
from qdrant_client import models
from src.store import get_embeddings, get_qdrant_client
from src.config import settings

# Khởi tạo Reranker (Tải mô hình 1 lần duy nhất khi khởi động server)
reranker = CrossEncoder('BAAI/bge-reranker-base')


def answer_question(question: str, sources: list = None) -> str:
    """
    Tìm kiếm ngữ cảnh từ cơ sở dữ liệu Vector và sinh câu trả lời bằng LLM.
    """
    # 1. Kiểm tra tính hợp lệ của đầu vào
    if sources is not None and len(sources) == 0:
        return "Vui lòng tick chọn ít nhất một tài liệu ở cột bên trái để tôi có cơ sở trả lời nhé!"

    # 2. Khởi tạo kết nối Vector Database
    embeddings = get_embeddings()
    client = get_qdrant_client()

    vector_store = QdrantVectorStore(
        client=client,
        collection_name=settings.qdrant_collection,
        embedding=embeddings
    )

    # 3. Xây dựng bộ lọc và truy xuất sơ bộ (Top 20)
    search_kwargs = {"k": 20}
    if sources:
        search_kwargs["filter"] = models.Filter(
            must=[
                models.FieldCondition(
                    key="metadata.source",
                    match=models.MatchAny(any=sources)
                )
            ]
        )

    print(f"-> Đang tìm kiếm tài liệu cho câu hỏi: '{question}'...")
    initial_docs = vector_store.similarity_search(question, **search_kwargs)

    if not initial_docs:
        return "Xin lỗi, không tìm thấy đoạn văn bản nào phù hợp trong các tài liệu bạn đã chọn."

    # 4. Xếp hạng lại (Reranking) để lấy Top 5 đoạn liên quan nhất
    print("-> Đang chấm điểm và xếp hạng lại (Reranking)...")
    pairs = [[question, doc.page_content] for doc in initial_docs]
    scores = reranker.predict(pairs)

    doc_score_pairs = sorted(zip(initial_docs, scores), key=lambda x: x[1], reverse=True)
    top_docs = [pair[0] for pair in doc_score_pairs[:5]]

    # 5. Đóng gói ngữ cảnh kèm trích dẫn (Tên file & Số trang)
    context_sections = []
    for doc in top_docs:
        page_num = doc.metadata.get("page", 0) + 1
        source_file = doc.metadata.get("source", "Không rõ nguồn")
        context_sections.append(f"[Nguồn: {source_file} - Trang {page_num}]: {doc.page_content}")

    context_text = "\n\n".join(context_sections)

    # 6. Thiết lập Prompt cho LLM
    template = """Bạn là một trợ lý nghiên cứu chuyên nghiệp của NotebookLM. 
    Nhiệm vụ của bạn là giải đáp thắc mắc dựa trên các đoạn trích dẫn từ tài liệu dưới đây.

    QUY TẮC TRẢ LỜI:
    1. Chỉ sử dụng thông tin trong phần "NGỮ CẢNH TÀI LIỆU".
    2. BẮT BUỘC trích dẫn TÊN FILE và SỐ TRANG sau mỗi ý quan trọng hoặc cuối câu bằng định dạng [Tên File - Trang X].
    3. Nếu một ý nằm ở nhiều trang hoặc nhiều file, hãy liệt kê rõ ràng.
    4. Nếu không có thông tin, hãy trả lời: "Xin lỗi, tài liệu hiện tại không đề cập đến vấn đề này."

    NGỮ CẢNH TÀI LIỆU:
    {context}

    CÂU HỎI CỦA NGƯỜI DÙNG: 
    {question}

    CÂU TRẢ LỜI (Kèm trích dẫn):"""

    prompt = PromptTemplate(template=template, input_variables=["context", "question"])

    # 7. Khởi tạo LLM và tổng hợp câu trả lời
    llm = ChatOpenAI(
        model=settings.openai_model,
        api_key=settings.openai_api_key,
        temperature=0.1,
        max_tokens=1500
    )

    print(f"-> Đang tổng hợp câu trả lời bằng {settings.openai_model}...")
    chain = prompt | llm
    response = chain.invoke({"context": context_text, "question": question})

    return response.content