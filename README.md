# Interactive Multi-Document RAG System

An advanced, full-stack Retrieval-Augmented Generation (RAG) application inspired by NotebookLM. This system allows users to upload multiple PDF documents, selectively target specific files for data extraction, and query them with highly accurate answers featuring precise page-level citations.

[![Deployment Status](https://img.shields.io/badge/Frontend-Vercel-black?style=flat&logo=vercel)](https://vercel.com)
[![Backend Framework](https://img.shields.io/badge/Backend-FastAPI-009688?style=flat&logo=fastapi)](https://fastapi.tiangolo.com/)
[![Vector Database](https://img.shields.io/badge/VectorDB-Qdrant-red?style=flat&logo=qdrant)](https://qdrant.tech/)

---

## 🚀 Key Features

- **Selective Multi-Document Querying:** Leverages Qdrant's payload metadata filtering to allow users to pick exactly which PDFs to extract information from, moving beyond basic monolithic chatbots.
- **Advanced 2-Stage Retrieval Pipeline:**
  - **Stage 1 (Dense Retrieval):** Semantic search using `all-MiniLM-L6-v2` embeddings via `sentence-transformers` to fetch top candidate chunks.
  - **Stage 2 (Reranking):** Cross-Encoder reranking powered by `BAAI/bge-reranker-base` to optimize context relevance and eliminate LLM hallucinations.
- **Intelligent Chunking:** Implements Semantic Chunking via LangChain to maintain structural context across page boundaries.
- **Production-Ready Architecture:** Clean decoupled codebase separating a Next.js (React) modern UI from a high-performance FastAPI asynchronous backend.

---

## 🛠️ Tech Stack

- **Frontend:** Next.js (React), Tailwind CSS, Vercel
- **Backend:** Python, FastAPI, Uvicorn
- **AI/LLM Frameworks:** LangChain, OpenAI API
- **Core AI & Deep Learning:** PyTorch, Sentence-Transformers, Hugging Face, NumPy
- **Vector Search Engine:** Qdrant Vector Database
- **Tunneling:** Ngrok (for hybrid local-cloud testing)

---

## 🗺️ System Architecture

1. **Ingestion:** Upload PDF -> LangChain Semantic Chunking -> PyTorch Embedding Generation -> Qdrant Upsert with File Metadata.
2. **Retrieval:** User Query + Selected File IDs -> Qdrant Metadata Filter & Vector Search -> Sentence-Transformers Cross-Encoder Reranking -> Top Context.
3. **Generation:** Re-ordered Context + Prompt -> OpenAI LLM -> Structured Answer with exact page citations.

---

## 💻 Local Setup & Installation

### Prerequisites
- Python 3.9+
- Node.js 18+
- OpenAI API Key
- [Ngrok](https://ngrok.com/) (for connecting local backend to deployed frontend)

### 1. Clone the Repository
```bash
git clone [https://github.com/Duongg178/interactive-rag-system.git](https://github.com/Duongg178/interactive-rag-system.git)
cd interactive-rag-system
2. Backend Setup
Create a virtual environment and install the required dependencies:

Bash
python -m venv .venv

# Activate on Windows:
.venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
Create a .env file in the root directory and add your credentials:

Đoạn mã
OPENAI_API_KEY=your_openai_api_key_here
QDRANT_HOST=localhost
QDRANT_PORT=6333
Start the FastAPI development server:

Bash
python -m uvicorn src.api:app --reload
3. Frontend Setup (Local Testing)
Navigate into the frontend directory, install node modules, and run the Next.js app:

Bash
cd frontend
npm install
npm run dev
Open http://localhost:3000 with your browser to interact with the UI.

4. Hybrid Deployment: Connecting Vercel to Local Backend
To test the live Vercel frontend with your powerful local GPU/Backend:

Start your local FastAPI server (runs on port 8000).

Open a new terminal and expose your local port using Ngrok:

Bash
./ngrok http 8000
Copy the generated HTTPS forwarding URL (e.g., https://xxxx.ngrok-free.app).

Go to your project on Vercel -> Settings -> Environment Variables.

Update the NEXT_PUBLIC_API_URL variable with your Ngrok URL.

Go to the Deployments tab and click Redeploy.

🎥 Demo Video


<video src="https://github.com/user-attachments/assets/7558f228-1858-4147-bafb-69805ac34097" controls="controls" width="100%"></video>



