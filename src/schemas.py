from pydantic import BaseModel
from typing import Optional, List

# 1. Định nghĩa dữ liệu khi người dùng gửi câu hỏi
class AskRequest(BaseModel):
    question: str
    sources: Optional[List[str]] = []
# 2. Định nghĩa dữ liệu khi hệ thống trả về câu trả lời
class AskResponse(BaseModel):
    answer: str

# 3. Định nghĩa phản hồi chung cho các thông báo hệ thống (như Upload thành công)
class BaseResponse(BaseModel):
    message: str
    status: str = "success"