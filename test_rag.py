
from src.rag import answer_question

# Đặt câu hỏi dựa trên nội dung file PDF bạn đã upload (ví dụ deepseekv3)
cau_hoi = "What is  DeepSeek-V3"

answer = answer_question(cau_hoi)

print("\n" + "="*50)
print(f"HỎI: {cau_hoi}")
print(f"TRẢ LỜI: {answer}")
print("="*50)