# 🤖 GenAI PDF Bot

> A production-grade **Retrieval-Augmented Generation (RAG)** assistant built with **FastAPI**, **LangChain**, and **FAISS** that lets you upload PDF documents and ask context-aware questions with conversational memory.

![Python](https://img.shields.io/badge/Python-3.10%2B-3776AB?logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-0.115%2B-009688?logo=fastapi&logoColor=white)
![LangChain](https://img.shields.io/badge/LangChain-0.3%2B-1C3C3C?logo=langchain&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-green)

---

## 📋 Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Tech Stack](#tech-stack)
- [Architecture](#architecture)
- [Folder Structure](#folder-structure)
- [Getting Started](#getting-started)
- [Configuration](#configuration)
- [API Reference](#api-reference)
- [Usage Examples](#usage-examples)
- [Running Tests](#running-tests)
- [Future Improvements](#future-improvements)

---

## Overview

**GenAI PDF Bot** is a modular, clean-architecture AI assistant that combines:

- **PDF ingestion** — upload any PDF and have it automatically chunked, embedded, and indexed.
- **Semantic search** — FAISS-powered vector similarity retrieval surfaces the most relevant document sections.
- **LLM-powered answers** — OpenAI or Groq models generate precise, citation-aware responses.
- **Conversational memory** — a sliding window of recent exchanges provides context for follow-up questions.

It is designed to be **resume-worthy**, **industry-standard**, and **easy to extend**.

---

## Features

| Feature | Description |
|---|---|
| 📄 **PDF Upload & Indexing** | Extract text, split into chunks, generate embeddings, store in FAISS |
| 💬 **RAG Q&A** | Retrieve relevant context and generate accurate answers via LLM |
| 🧠 **Conversational Memory** | Maintains last N interactions per session for follow-up context |
| 🔄 **Dual LLM Support** | Switch between OpenAI and Groq with a single env variable |
| 🚀 **Async-First** | Fully asynchronous endpoints for maximum throughput |
| 📊 **Health & Stats** | Built-in health check and system statistics endpoint |
| 🔒 **Input Validation** | Pydantic schemas, file-type checks, size limits, and sanitisation |
| 📝 **Structured Logging** | Consistent, timestamped log output across all modules |
| 🌐 **CORS Enabled** | Ready for frontend integration out of the box |
| 📚 **Interactive Docs** | Auto-generated Swagger UI at `/docs` and ReDoc at `/redoc` |

---

## Tech Stack

| Layer | Technology |
|---|---|
| **Backend Framework** | [FastAPI](https://fastapi.tiangolo.com/) |
| **LLM Orchestration** | [LangChain](https://python.langchain.com/) |
| **LLM Providers** | [OpenAI API](https://platform.openai.com/) / [Groq API](https://groq.com/) |
| **Embeddings** | [HuggingFace sentence-transformers](https://huggingface.co/sentence-transformers) (`all-MiniLM-L6-v2`) |
| **Vector Store** | [FAISS](https://github.com/facebookresearch/faiss) (Facebook AI Similarity Search) |
| **PDF Processing** | [PyPDF](https://pypdf.readthedocs.io/) |
| **Config Management** | [python-dotenv](https://github.com/theskumar/python-dotenv) |
| **Testing** | [pytest](https://pytest.org/) + FastAPI TestClient |

---

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                        FastAPI Server                       │
│  ┌──────────┐   ┌──────────────────────────────────────┐    │
│  │  Client   │──▶│           API Routes (v1)            │    │
│  │ (Browser/ │   │  POST /upload  ·  POST /ask          │    │
│  │  Postman) │   │  GET  /health  ·  POST /memory/clear │    │
│  └──────────┘   └──────────┬───────────┬───────────────┘    │
│                             │           │                    │
│              ┌──────────────▼──┐  ┌─────▼──────────┐        │
│              │   RAG Service   │  │  Memory Service │        │
│              │  (FAISS + Emb.) │  │ (Sliding Window)│        │
│              └────────┬────────┘  └─────┬──────────┘        │
│                       │                 │                    │
│              ┌────────▼─────────────────▼──────────┐        │
│              │           LLM Service               │        │
│              │   (OpenAI / Groq via LangChain)     │        │
│              └─────────────────────────────────────┘        │
└─────────────────────────────────────────────────────────────┘
```

### Data Flow

1. **Upload:** PDF → Text Extraction → Chunking → Embedding → FAISS Index
2. **Ask:** Query → Semantic Search → Retrieve Top-K Chunks → Inject Context + Memory → LLM → Response

---

## Folder Structure

```
GenAI_PDF_Bot/
│
├── app/                          # Application source code
│   ├── __init__.py               # Package marker + version
│   ├── main.py                   # FastAPI app, lifespan, middleware
│   │
│   ├── api/                      # HTTP layer
│   │   ├── __init__.py
│   │   └── routes.py             # All API endpoint definitions
│   │
│   ├── services/                 # Business logic layer
│   │   ├── __init__.py
│   │   ├── rag_service.py        # FAISS vector store + retrieval
│   │   ├── llm_service.py        # LLM abstraction (OpenAI/Groq)
│   │   └── memory_service.py     # Conversational memory
│   │
│   ├── core/                     # Cross-cutting concerns
│   │   ├── __init__.py
│   │   └── config.py             # Settings from environment
│   │
│   └── utils/                    # Shared utilities
│       ├── __init__.py
│       └── helpers.py            # PDF parsing, chunking, validation
│
├── data/                         # Runtime data (git-ignored)
│   ├── faiss_index/              # Persisted FAISS index
│   └── uploads/                  # Temporary PDF uploads
│
├── tests/                        # Test suite
│   ├── __init__.py
│   └── test_api.py               # API endpoint tests
│
├── .env.example                  # Environment variable template
├── .gitignore                    # Git ignore rules
├── requirements.txt              # Python dependencies
└── README.md                     # This file
```

---

## Getting Started

### Prerequisites

- **Python 3.10+**
- An API key for **OpenAI** or **Groq** (free tier available at [console.groq.com](https://console.groq.com))

### 1. Clone the Repository

```bash
git clone https://github.com/your-username/GenAI_PDF_Bot.git
cd GenAI_PDF_Bot
```

### 2. Create a Virtual Environment

```bash
python -m venv venv

# Windows
venv\Scripts\activate

# macOS / Linux
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure Environment

```bash
cp .env.example .env
```

Edit `.env` and add your API key:

```dotenv
LLM_PROVIDER=groq
GROQ_API_KEY=gsk_your_actual_key_here
```

### 5. Run the Server

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at:
- **Swagger UI:** [http://localhost:8000/docs](http://localhost:8000/docs)
- **ReDoc:** [http://localhost:8000/redoc](http://localhost:8000/redoc)
- **Health Check:** [http://localhost:8000/api/v1/health](http://localhost:8000/api/v1/health)

---

## Configuration

All settings are loaded from environment variables (`.env` file):

| Variable | Default | Description |
|---|---|---|
| `LLM_PROVIDER` | `groq` | `openai` or `groq` |
| `OPENAI_API_KEY` | — | Required if provider is `openai` |
| `GROQ_API_KEY` | — | Required if provider is `groq` |
| `OPENAI_MODEL` | `gpt-4o-mini` | OpenAI model name |
| `GROQ_MODEL` | `llama-3.3-70b-versatile` | Groq model name |
| `EMBEDDING_MODEL` | `sentence-transformers/all-MiniLM-L6-v2` | HuggingFace embedding model |
| `CHUNK_SIZE` | `1000` | Characters per text chunk |
| `CHUNK_OVERLAP` | `200` | Overlap between chunks |
| `MEMORY_WINDOW` | `5` | Recent interactions to keep |
| `LOG_LEVEL` | `INFO` | Logging verbosity |

---

## API Reference

### `POST /api/v1/upload` — Upload a PDF

Upload and index a PDF document for question answering.

**Request:**
```
Content-Type: multipart/form-data
```

| Field | Type | Required | Description |
|---|---|---|---|
| `file` | File (PDF) | ✅ | The PDF document to upload |

**Response (201):**
```json
{
  "filename": "research_paper.pdf",
  "pages_extracted": 12,
  "chunks_created": 34,
  "total_vectors": 34,
  "message": "PDF uploaded and indexed successfully."
}
```

---

### `POST /api/v1/ask` — Ask a Question

Ask a question about the uploaded documents.

**Request:**
```json
{
  "question": "What are the key findings?",
  "session_id": "user-session-123"
}
```

| Field | Type | Required | Description |
|---|---|---|---|
| `question` | string | ✅ | Your question (1–2000 chars) |
| `session_id` | string | ❌ | Session ID for memory (auto-generated if omitted) |

**Response (200):**
```json
{
  "answer": "The key findings of the report include...",
  "session_id": "user-session-123",
  "sources_used": 4
}
```

---

### `GET /api/v1/health` — Health Check

**Response (200):**
```json
{
  "status": "healthy",
  "vector_store_ready": true,
  "total_vectors": 34,
  "active_sessions": 2
}
```

---

### `POST /api/v1/memory/clear` — Clear Session Memory

**Request:**
```json
{
  "session_id": "user-session-123"
}
```

**Response (200):**
```json
{
  "message": "Memory cleared for session 'user-session-123'."
}
```

---

## Usage Examples

### Using cURL

**Upload a PDF:**
```bash
curl -X POST http://localhost:8000/api/v1/upload \
  -F "file=@./my_document.pdf"
```

**Ask a question:**
```bash
curl -X POST http://localhost:8000/api/v1/ask \
  -H "Content-Type: application/json" \
  -d '{"question": "Summarize the main points", "session_id": "session-1"}'
```

**Follow-up question (same session):**
```bash
curl -X POST http://localhost:8000/api/v1/ask \
  -H "Content-Type: application/json" \
  -d '{"question": "Can you elaborate on the second point?", "session_id": "session-1"}'
```

**Check health:**
```bash
curl http://localhost:8000/api/v1/health
```

**Clear memory:**
```bash
curl -X POST http://localhost:8000/api/v1/memory/clear \
  -H "Content-Type: application/json" \
  -d '{"session_id": "session-1"}'
```

### Using Python `requests`

```python
import requests

BASE = "http://localhost:8000/api/v1"

# Upload
with open("paper.pdf", "rb") as f:
    resp = requests.post(f"{BASE}/upload", files={"file": f})
    print(resp.json())

# Ask
resp = requests.post(f"{BASE}/ask", json={
    "question": "What methodology was used?",
    "session_id": "demo"
})
print(resp.json()["answer"])
```

---

## Running Tests

```bash
# Install test dependencies (already in requirements.txt)
pip install pytest httpx

# Run all tests
pytest tests/ -v

# Run with coverage (optional)
pip install pytest-cov
pytest tests/ -v --cov=app --cov-report=term-missing
```

---

## Future Improvements

| Area | Improvement |
|---|---|
| 🗄️ **Persistence** | Replace in-memory history with Redis or PostgreSQL |
| 📄 **Multi-format** | Support DOCX, TXT, and Markdown uploads |
| 🔐 **Authentication** | Add JWT-based auth and per-user document isolation |
| 🎨 **Frontend** | Build a React/Next.js chat UI |
| 🐳 **Docker** | Add `Dockerfile` and `docker-compose.yml` |
| ☁️ **Cloud Deploy** | CI/CD pipeline for AWS / GCP / Azure |
| 📊 **Observability** | OpenTelemetry tracing and Prometheus metrics |
| 🔍 **Hybrid Search** | Combine semantic search with BM25 keyword retrieval |
| 🧪 **Advanced Testing** | Integration tests with mocked LLM responses |
| 📱 **Streaming** | Server-Sent Events (SSE) for real-time answer streaming |

---

## License

This project is open-source and available under the [MIT License](LICENSE).

---

<p align="center">
  Built with ❤️ using FastAPI, LangChain & FAISS
</p>
