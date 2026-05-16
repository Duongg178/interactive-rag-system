"use client";
import React, { useState, useEffect } from 'react'; // <-- Thêm useEffect
import { Upload, Send, FileText, Loader2, CheckSquare } from 'lucide-react';

export default function NotebookLMClone() {
  const [file, setFile] = useState<File | null>(null);
  const [question, setQuestion] = useState('');
  const [chatHistory, setChatHistory] = useState<{q: string, a: string}[]>([]);
  const [loading, setLoading] = useState(false);
  const [uploading, setUploading] = useState(false);
  useEffect(() => {
    const fetchExistingFiles = async () => {
      try {
        const res = await fetch('http://localhost:8000/files');
        const data = await res.json();
        if (data.files && data.files.length > 0) {
          setUploadedFiles(data.files);
          // (Tùy chọn) Nếu muốn load lên tick chọn sẵn hết tất cả các file thì mở ngoặc dòng dưới:
          // setSelectedFiles(data.files);
        }
      } catch (error) {
        console.error("Lỗi khi tải danh sách file:", error);
      }
    };

    fetchExistingFiles();
  }, []); // Ngoặc vuông rỗng nghĩa là chỉ chạy 1 lần lúc mở web

  // THÊM: Quản lý danh sách file
  const [uploadedFiles, setUploadedFiles] = useState<string[]>([]);
  const [selectedFiles, setSelectedFiles] = useState<string[]>([]);

  const handleUpload = async () => {
    if (!file) return;
    setUploading(true);
    const formData = new FormData();
    formData.append('file', file);

    try {
      const res = await fetch('http://127.0.0.1:8000/upload', {
        method: 'POST',
        body: formData,
      });
      const data = await res.json();

      // THÊM: Cập nhật danh sách file sau khi up thành công
      if (!uploadedFiles.includes(file.name)) {
        setUploadedFiles([...uploadedFiles, file.name]);
        setSelectedFiles([...selectedFiles, file.name]); // Mặc định chọn file vừa up
      }
      alert(data.message);
      setFile(null); // Reset ô chọn file
    } catch (error) {
      console.error("Upload failed", error);
    } finally {
      setUploading(false);
    }
  };

  const handleAsk = async () => {
    if (!question.trim()) return;
    setLoading(true);
    try {
      const res = await fetch('http://127.0.0.1:8000/ask', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        // THÊM: Gửi kèm danh sách file đang được tick chọn
        body: JSON.stringify({ question, sources: selectedFiles }),
      });
      const data = await res.json();
      setChatHistory([...chatHistory, { q: question, a: data.answer }]);
      setQuestion('');
    } catch (error) {
      console.error("Ask failed", error);
    } finally {
      setLoading(false);
    }
  };

  // THÊM: Hàm xử lý khi tick/bỏ tick chọn file
  const toggleFile = (filename: string) => {
    if (selectedFiles.includes(filename)) {
      setSelectedFiles(selectedFiles.filter(f => f !== filename));
    } else {
      setSelectedFiles([...selectedFiles, filename]);
    }
  };

  return (
    <div className="flex h-screen bg-gray-50 text-gray-900 font-sans">
      {/* CỘT TRÁI */}
      <div className="w-1/3 border-r bg-white p-6 flex flex-col">
        <h1 className="text-xl font-bold mb-6 flex items-center gap-2">
          <FileText className="text-blue-600" /> Nguồn tài liệu
        </h1>

        <div className="border-2 border-dashed border-gray-300 rounded-lg p-6 text-center mb-6">
          <input
            type="file" accept=".pdf"
            onChange={(e) => setFile(e.target.files?.[0] || null)}
            className="hidden" id="fileInput"
          />
          <label htmlFor="fileInput" className="cursor-pointer flex flex-col items-center">
            <Upload className="w-8 h-8 text-gray-400 mb-2" />
            <span className="text-sm text-gray-600">{file ? file.name : "Tải lên PDF mới"}</span>
          </label>
          <button
            onClick={handleUpload} disabled={!file || uploading}
            className="mt-4 w-full bg-blue-600 text-white py-2 rounded hover:bg-blue-700 disabled:bg-gray-400 flex justify-center items-center gap-2"
          >
            {uploading ? <Loader2 className="animate-spin w-4 h-4" /> : "Tải lên"}
          </button>
        </div>

        {/* THÊM: Khu vực hiển thị các file đã upload để chọn */}
        {uploadedFiles.length > 0 && (
          <div className="flex-1 overflow-y-auto">
            <h3 className="font-semibold text-sm text-gray-500 mb-3 uppercase tracking-wider">Đã tải lên</h3>
            <div className="space-y-2">
              {uploadedFiles.map(filename => (
                <label key={filename} className="flex items-center gap-3 p-3 border rounded-lg cursor-pointer hover:bg-gray-50 transition">
                  <input
                    type="checkbox"
                    checked={selectedFiles.includes(filename)}
                    onChange={() => toggleFile(filename)}
                    className="w-5 h-5 text-blue-600 rounded"
                  />
                  <span className="text-sm truncate font-medium" title={filename}>{filename}</span>
                </label>
              ))}
            </div>
          </div>
        )}
      </div>

      {/* CỘT PHẢI (Giữ nguyên phần Chat giống code cũ) */}
      <div className="flex-1 flex flex-col p-6 overflow-hidden">
        {/* ... (Copy nguyên xi phần giao diện cột phải từ code trước xuống) ... */}
        <div className="flex-1 overflow-y-auto space-y-4 mb-4 pr-4">
          {chatHistory.length === 0 && (
            <div className="text-center text-gray-400 mt-20">Hãy nạp tài liệu và bắt đầu đặt câu hỏi!</div>
          )}
          {chatHistory.map((chat, i) => (
            <div key={i} className="space-y-2">
              <div className="flex justify-end">
                <div className="bg-blue-100 p-3 rounded-2xl max-w-[80%] text-sm font-medium">{chat.q}</div>
              </div>
              <div className="flex justify-start">
                <div className="bg-white border p-4 rounded-2xl max-w-[90%] text-sm leading-relaxed whitespace-pre-wrap shadow-sm">
                  {chat.a}
                </div>
              </div>
            </div>
          ))}
          {loading && <div className="text-sm text-gray-500 animate-pulse">AI đang suy nghĩ...</div>}
        </div>

        <div className="relative">
          <input
            type="text" value={question}
            onChange={(e) => setQuestion(e.target.value)}
            onKeyDown={(e) => e.key === 'Enter' && handleAsk()}
            placeholder="Đặt câu hỏi..."
            className="w-full border rounded-full py-4 px-6 pr-14 focus:outline-none focus:ring-2 focus:ring-blue-500 shadow-lg"
          />
          <button 
            onClick={handleAsk}
            className="absolute right-3 top-2.5 p-2 bg-blue-600 text-white rounded-full hover:bg-blue-700 transition-all"
          >
            <Send className="w-5 h-5" />
          </button>
        </div>
      </div>
    </div>
  );
}