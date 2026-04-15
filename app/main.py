"""
GenAI PDF Bot — FastAPI Application Entry Point.

Initialises services, configures middleware, and mounts API routes.
"""

import logging
import sys
from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api import routes
from app.core.config import get_settings
from app.services.llm_service import LLMService
from app.services.memory_service import MemoryService
from app.services.rag_service import RAGService

# ---------------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------------

def _setup_logging(level: str) -> None:
    """Configure structured logging for the entire application."""
    fmt = "%(asctime)s | %(levelname)-8s | %(name)-30s | %(message)s"
    logging.basicConfig(
        level=getattr(logging, level, logging.INFO),
        format=fmt,
        handlers=[logging.StreamHandler(sys.stdout)],
    )
    # Silence noisy third-party loggers
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("httpcore").setLevel(logging.WARNING)
    logging.getLogger("sentence_transformers").setLevel(logging.WARNING)


logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Application lifespan
# ---------------------------------------------------------------------------

@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """
    Manage application startup and shutdown lifecycle.

    On startup:
      • Load settings and validate environment.
      • Initialise RAG, LLM, and Memory services.
      • Inject services into the API router.

    On shutdown:
      • Perform any necessary cleanup.
    """
    settings = get_settings()
    _setup_logging(settings.log_level)

    logger.info("=" * 60)
    logger.info("  GenAI PDF Bot — Starting up")
    logger.info("  Provider : %s", settings.llm_provider.value)
    logger.info("  Model    : %s", settings.active_model)
    logger.info("  Embedding: %s", settings.embedding_model)
    logger.info("=" * 60)

    # Build services
    rag_service = RAGService(settings)
    llm_service = LLMService(settings)
    memory_service = MemoryService(max_window=settings.memory_window)

    # Inject into router
    routes.configure(
        rag=rag_service,
        llm=llm_service,
        memory=memory_service,
        upload_dir=settings.upload_dir,
        chunk_size=settings.chunk_size,
        chunk_overlap=settings.chunk_overlap,
    )

    logger.info("All services initialised. Ready to serve requests.")
    yield
    logger.info("Shutting down GenAI PDF Bot.")


# ---------------------------------------------------------------------------
# FastAPI application
# ---------------------------------------------------------------------------

app = FastAPI(
    title="GenAI PDF Bot",
    description=(
        "A production-grade Retrieval-Augmented Generation (RAG) assistant "
        "that lets you upload PDF documents and ask context-aware questions "
        "with conversational memory."
    ),
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)

# --- CORS Middleware ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],          # Restrict in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Mount routes ---
app.include_router(routes.router, prefix="/api/v1")


# --- Root redirect ---
@app.get("/", include_in_schema=False)
async def root() -> dict:
    """Redirect-friendly root that confirms the API is running."""
    return {
        "app": "GenAI PDF Bot",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/api/v1/health",
    }
