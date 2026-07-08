# ⚖️ Nyaya Samrakshan
### AI-Powered Legal Assistant for the Indian Constitution & Legal System

![Python](https://img.shields.io/badge/Python-3.12-blue)
![FastAPI](https://img.shields.io/badge/FastAPI-Backend-green)
![React](https://img.shields.io/badge/React-Frontend-61DAFB)
![TypeScript](https://img.shields.io/badge/TypeScript-5.0-blue)
![Supabase](https://img.shields.io/badge/Supabase-Authentication-green)
![RAG](https://img.shields.io/badge/RAG-Enabled-orange)
![License](https://img.shields.io/badge/License-MIT-brightgreen)

---

# ⚖️ Nyaya Samrakshan

**Nyaya Samrakshan** translates to **"Protection of Justice."**

It is an AI-powered legal assistant designed to make Indian legal information more accessible to everyone. By combining **Retrieval-Augmented Generation (RAG)**, **Large Language Models (LLMs)**, **Vector Search**, and **Supabase Authentication**, the system provides accurate, context-aware legal guidance based on the Constitution of India and other legal resources.

> **Disclaimer:** This application is developed for educational and research purposes. It is intended to assist users in understanding legal concepts and should not be considered a substitute for professional legal advice.

---

# ✨ Features

- 🤖 AI-powered legal question answering
- 📚 Retrieval-Augmented Generation (RAG)
- 📄 Legal document upload and analysis
- 💬 Persistent chat history
- 🔐 Secure user authentication
- 📑 Citation-based legal responses
- ⚡ FastAPI backend
- 🎨 Modern React + TypeScript interface
- 🔍 Semantic legal document search
- 📊 Confidence scoring for AI responses
- ☁️ Supabase Authentication & Database
- 📂 ChromaDB Vector Database

---

# 🛠️ Technology Stack

## Frontend

- React
- TypeScript
- Vite
- Tailwind CSS
- Axios

## Backend

- FastAPI
- Python
- LangChain
- ChromaDB
- Sentence Transformers
- NVIDIA AI API
- Tavily Search API

## Database & Authentication

- Supabase
- ChromaDB

---

# 🏛️ System Architecture

```
                        User
                          │
                          ▼
                 React Frontend
                          │
                          ▼
                 FastAPI Backend
                          │
       ┌──────────────────┼──────────────────┐
       │                  │                  │
       ▼                  ▼                  ▼
Authentication     Chat History      Document Upload
 (Supabase)         (Supabase)          (PDF/DOCX)
       │                  │                  │
       └──────────────────┼──────────────────┘
                          │
                          ▼
                Retrieval-Augmented Generation
                          │
                          ▼
              ChromaDB Vector Database
                          │
                          ▼
                  Relevant Legal Context
                          │
                          ▼
                NVIDIA Large Language Model
                          │
                          ▼
              AI Generated Legal Response
                          │
                          ▼
                   Response with Citations
```

---

# 📂 Project Structure

```
AI-Lawyer-Assistant/

├── backend/
│   ├── app/
│   ├── database/
│   ├── scripts/
│   ├── tests/
│   ├── requirements.txt
│   └── .env
│
├── frontend/
│   └── frontend/
│       ├── src/
│       ├── public/
│       └── .env
│
├── docs/
│
└── README.md
```

---

# 🚀 Installation

## Clone Repository

```bash
git clone https://github.com/daveedreddy/AI-Lawyer-Assistant.git

cd AI-Lawyer-Assistant
```

---

# Backend Setup

```bash
cd backend

python -m venv .venv

# Windows
.venv\Scripts\activate

pip install -r requirements.txt

uvicorn app.main:app --reload
```

Backend Server

```
http://127.0.0.1:8000
```

Swagger Documentation

```
http://127.0.0.1:8000/docs
```

---

# Frontend Setup

```bash
cd frontend/frontend

npm install

npm run dev
```

Frontend

```
http://localhost:5173
```

---

# 🔑 Environment Variables

## Backend (.env)

```env
DEBUG=false

NVIDIA_API_KEY=
NVIDIA_BASE_URL=https://integrate.api.nvidia.com/v1
NVIDIA_MODEL=

TAVILY_API_KEY=

SUPABASE_URL=
SUPABASE_ANON_KEY=
SUPABASE_SERVICE_ROLE_KEY=
SUPABASE_JWT_SECRET=

DEFAULT_TOP_K=5
CACHE_TTL_SECONDS=300
MAX_QUERY_LENGTH=2000

STORAGE_BUCKET_DOCUMENTS=legal-documents

CORS_ORIGINS=http://localhost:5173,http://127.0.0.1:5173
```

---

## Frontend (.env)

```env
VITE_API_BASE_URL=http://127.0.0.1:8000

VITE_SUPABASE_URL=

VITE_SUPABASE_ANON_KEY=
```

---

# 🔄 Workflow

```
User Query
     │
     ▼
Authentication (Supabase)
     │
     ▼
FastAPI Backend
     │
     ▼
Embedding Generation
     │
     ▼
ChromaDB Semantic Search
     │
     ▼
Relevant Legal Documents Retrieved
     │
     ▼
Prompt Construction
     │
     ▼
NVIDIA Large Language Model
     │
     ▼
AI Response + Citations
     │
     ▼
Frontend Display
```

---

# 📄 Supported File Types

- PDF
- DOCX
- TXT

---

# 📚 Knowledge Base

The AI system works with Indian legal resources including:

- Constitution of India
- Bharatiya Nyaya Sanhita (BNS)
- Bharatiya Nagarik Suraksha Sanhita (BNSS)
- Bharatiya Sakshya Adhiniyam (BSA)
- Government Legal Documents
- Court Judgments
- Uploaded Legal Documents

---

# 🔒 Security

- JWT Authentication
- Secure Supabase Authentication
- Protected API Endpoints
- Environment Variable Management
- Secure Document Storage
- Role-Based Backend Access

---

# 🎯 Future Scope

- 🎙️ Voice-based Legal Assistant
- 🌐 Multilingual Support
- 📷 OCR for Scanned Documents
- 👨‍⚖️ Advocate Recommendation System
- 📍 Location-based Lawyer Suggestions
- 📜 AI-generated Legal Notices
- 📱 Android & iOS Applications

---

# 📸 Screenshots

Add screenshots here:

- Login Page
- Registration Page
- Dashboard
- Chat Interface
- Chat History
- Document Upload
- AI Legal Response
- Citations Display

---

# 👨‍💻 Developer

**S. Daveed Reddy**

B.Tech – Artificial Intelligence & Machine Learning

GitHub:
https://github.com/daveedreddy

Repository:
https://github.com/daveedreddy/AI-Lawyer-Assistant

---

# 🙏 Acknowledgements

Special thanks to the open-source communities and technologies that made this project possible:

- FastAPI
- React
- TypeScript
- Supabase
- LangChain
- ChromaDB
- NVIDIA AI
- Tavily Search
- Python Community

---

# 📜 License

This project is developed for **academic, educational, and research purposes**.

© 2026 S. Daveed Reddy. All Rights Reserved.
