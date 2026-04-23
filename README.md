# Doclearner AI

> Upload PDFs and chat with them using AI — powered by RAG (Retrieval-Augmented Generation).

![Tech Stack](https://img.shields.io/badge/FastAPI-005571?style=for-the-badge&logo=fastapi)
![MongoDB](https://img.shields.io/badge/MongoDB-4EA94B?style=for-the-badge&logo=mongodb)
![Redis](https://img.shields.io/badge/Redis-DC382D?style=for-the-badge&logo=redis)
![React](https://img.shields.io/badge/React-20232A?style=for-the-badge&logo=react)
![Docker](https://img.shields.io/badge/Docker-2496ED?style=for-the-badge&logo=docker)

## What it does
Users sign up, upload PDFs, and chat with them using AI. The system finds the most relevant parts of the document and returns them as answers.

## Tech Stack
- **FastAPI** — Python backend with JWT authentication
- **LangChain + ChromaDB** — RAG pipeline for PDF ingestion and semantic search
- **HuggingFace Embeddings** — all-MiniLM-L6-v2 model for vector embeddings
- **MongoDB** — stores users, documents and chat history
- **Redis** — caches recent chat messages and sessions
- **React + Vite + Tailwind CSS** — frontend UI
- **Docker Compose** — runs MongoDB and Redis

## Features
- JWT authentication (register/login)
- PDF upload and processing
- AI-powered chat with documents
- Chat history saved to MongoDB
- Redis caching for fast message retrieval

## Quick Start

### Prerequisites
- Python 3.11+
- Node.js 20+
- Docker Desktop

### Run locally

1. Clone the repo
   git clone https://github.com/ankit07patel/Doclearner-ai.git
   cd Doclearner-ai

2. Start MongoDB and Redis
   docker compose up -d mongodb redis

3. Start the backend
   cd backend
   python -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   uvicorn main:app --reload

4. Start the frontend
   cd frontend
   npm install
   npm run dev

5. Open http://localhost:5173

## API Endpoints
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | /register | Create account |
| POST | /login | Login and get JWT token |
| GET | /me | Get current user |
| POST | /upload | Upload a PDF |
| GET | /documents | List all documents |
| POST | /chat | Chat with a document |
| GET | /chat/history/{doc_id} | Get chat history |

## Engineering Decisions
- **Chunking with overlap** — used 500 token chunks with 50 token overlap to avoid losing context at boundaries
- **all-MiniLM-L6-v2** — fast, lightweight embedding model that runs locally with no API cost
- **Redis caching** — stores last 10 chat turns per session, expires after 1 hour
- **JWT tokens** — access tokens expire in 30 minutes for security

## Project Structure
Doclearner-ai/
├── backend/
│   ├── main.py          # FastAPI routes
│   ├── auth.py          # JWT authentication
│   ├── database.py      # MongoDB connection
│   ├── rag.py           # RAG pipeline
│   ├── redis_client.py  # Redis caching
│   └── config.py        # Environment config
├── frontend/
│   ├── src/
│   │   ├── App.jsx      # Main app
│   │   ├── Login.jsx    # Login/Register page
│   │   ├── Dashboard.jsx # Document dashboard
│   │   ├── Chat.jsx     # Chat interface
│   │   └── api.js       # API calls
└── docker-compose.yml