import os

from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware

from app.api.chat import router as chat_router
from app.api.upload import router as upload_router
from app.api.history import router as history_router
from app.api.profile import router as profile_router

from app.core.exceptions import (
    APIException,
    api_exception_handler,
    unhandled_exception_handler,
    validation_exception_handler,
)

from app.utils.logging_utils import configure_logging

configure_logging()

app = FastAPI(
    title="AI Lawyer Assistant API",
    version="1.0.0",
    description="AI-powered legal assistant with RAG and live legal search.",
    docs_url="/docs",
    redoc_url="/redoc",
)

# CORS — restrict to configured origins in production
_raw_origins = os.getenv("CORS_ORIGINS", "http://localhost:5173,http://127.0.0.1:5173")
ALLOWED_ORIGINS = [o.strip() for o in _raw_origins.split(",") if o.strip()]

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routers — each included exactly once
app.include_router(chat_router)
app.include_router(upload_router)
app.include_router(history_router)
app.include_router(profile_router)

# Exception handlers
app.add_exception_handler(APIException, api_exception_handler)
app.add_exception_handler(RequestValidationError, validation_exception_handler)
app.add_exception_handler(Exception, unhandled_exception_handler)


@app.get("/")
def home():
    return {
        "project": "AI Lawyer Assistant",
        "status": "Running Successfully",
        "version": "1.0.0",
    }


@app.get("/health")
def health():
    return {"status": "healthy"}