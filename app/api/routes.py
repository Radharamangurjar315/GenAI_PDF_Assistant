"""
API route definitions for the GenAI PDF Bot.

Endpoints:
  POST /upload   — Upload and index a PDF document.
  POST /ask      — Ask a question against indexed documents.
  GET  /health   — Liveness / readiness probe.
  GET  /stats    — Current system statistics.
  POST /memory/clear — Clear conversation memory for a session.
"""

import logging
import shutil
import uuid
from pathlib import Path
from typing import Optional

from fastapi import APIRouter, File, HTTPException, UploadFile, status
from pydantic import BaseModel, Field

from app.services.llm_service import LLMService
from app.services.memory_service import MemoryService
from app.services.rag_service import RAGService
from app.utils.helpers import (
    extract_text_from_pdf,
    sanitise_query,
    split_text_into_chunks,
    validate_pdf,
)

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Router instance (injected dependencies set at startup)
# ---------------------------------------------------------------------------
router = APIRouter()

# These are populated by ``app.main`` during application lifespan.
_rag_service: Optional[RAGService] = None
_llm_service: Optional[LLMService] = None
_memory_service: Optional[MemoryService] = None
_upload_dir: Optional[Path] = None
_chunk_size: int = 1000
_chunk_overlap: int = 200


def configure(
    rag: RAGService,
    llm: LLMService,
    memory: MemoryService,
    upload_dir: Path,
    chunk_size: int,
    chunk_overlap: int,
) -> None:
    """
    Inject runtime dependencies into the router module.

    Called once during application startup from ``main.py``.
    """
    global _rag_service, _llm_service, _memory_service
    global _upload_dir, _chunk_size, _chunk_overlap
    _rag_service = rag
    _llm_service = llm
    _memory_service = memory
    _upload_dir = upload_dir
    _chunk_size = chunk_size
    _chunk_overlap = chunk_overlap
    logger.info("Routes configured with service dependencies.")


# ---------------------------------------------------------------------------
# Request / Response schemas
# ---------------------------------------------------------------------------

class AskRequest(BaseModel):
    """Schema for the /ask endpoint."""
    question: str = Field(
        ...,
        min_length=1,
        max_length=2000,
        description="The question to ask about the uploaded documents.",
        json_schema_extra={"example": "What are the key findings of the report?"},
    )
    session_id: str = Field(
        default_factory=lambda: str(uuid.uuid4()),
        description="Session identifier for conversational memory.",
        json_schema_extra={"example": "user-session-123"},
    )


class AskResponse(BaseModel):
    """Schema for the /ask response."""
    answer: str
    session_id: str
    sources_used: int


class UploadResponse(BaseModel):
    """Schema for the /upload response."""
    filename: str
    pages_extracted: int
    chunks_created: int
    total_vectors: int
    message: str


class HealthResponse(BaseModel):
    """Schema for the /health response."""
    status: str
    vector_store_ready: bool
    total_vectors: int
    active_sessions: int


class ClearMemoryRequest(BaseModel):
    """Schema for the /memory/clear endpoint."""
    session_id: str = Field(
        ...,
        description="Session whose memory should be cleared.",
    )


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------

@router.post(
    "/upload",
    response_model=UploadResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Upload a PDF document for indexing",
    tags=["Documents"],
)
async def upload_pdf(file: UploadFile = File(...)) -> UploadResponse:
    """
    Upload a PDF, extract its text, chunk it, embed the chunks and
    store them in the FAISS vector database.
    """
    assert _rag_service and _upload_dir  # guarded by startup check

    # --- Validate file type early ---
    if not file.filename or not file.filename.lower().endswith(".pdf"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only PDF files are accepted.",
        )

    # --- Save to disk ---
    safe_name = f"{uuid.uuid4().hex}_{file.filename}"
    dest = _upload_dir / safe_name
    try:
        with dest.open("wb") as buf:
            shutil.copyfileobj(file.file, buf)
    except Exception as exc:
        logger.exception("Failed to save uploaded file.")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Could not save file: {exc}",
        ) from exc
    finally:
        await file.close()

    # --- Validate PDF ---
    try:
        validate_pdf(dest)
    except ValueError as exc:
        dest.unlink(missing_ok=True)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc

    # --- Extract → Chunk → Embed ---
    try:
        text = extract_text_from_pdf(dest)
        chunks = split_text_into_chunks(text, _chunk_size, _chunk_overlap)
        total_vectors = await _rag_service.add_documents(
            chunks, source=file.filename or "uploaded.pdf"
        )
    except ValueError as exc:
        dest.unlink(missing_ok=True)
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(exc),
        ) from exc
    except Exception as exc:
        logger.exception("Error processing PDF.")
        dest.unlink(missing_ok=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Processing error: {exc}",
        ) from exc

    # --- Cleanup temp file ---
    dest.unlink(missing_ok=True)

    logger.info(
        "PDF '%s' indexed — %d chunks, %d total vectors.",
        file.filename,
        len(chunks),
        total_vectors,
    )

    return UploadResponse(
        filename=file.filename or "uploaded.pdf",
        pages_extracted=len(text.split("\n\n")),
        chunks_created=len(chunks),
        total_vectors=total_vectors,
        message="PDF uploaded and indexed successfully.",
    )


@router.post(
    "/ask",
    response_model=AskResponse,
    summary="Ask a question about uploaded documents",
    tags=["Q&A"],
)
async def ask_question(body: AskRequest) -> AskResponse:
    """
    Answer a user question using RAG (semantic retrieval + LLM generation)
    with conversational memory.
    """
    assert _rag_service and _llm_service and _memory_service

    # --- Sanitise ---
    try:
        clean_question = sanitise_query(body.question)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc

    # --- Retrieve context ---
    try:
        context = await _rag_service.search(clean_question)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc

    # --- Build conversational history ---
    history = _memory_service.get_formatted_history(body.session_id)

    # --- Generate ---
    try:
        answer = await _llm_service.generate(
            question=clean_question,
            context=context,
            history=history,
        )
    except Exception as exc:
        logger.exception("LLM generation failed.")
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"LLM error: {exc}",
        ) from exc

    # --- Persist to memory ---
    _memory_service.add(body.session_id, clean_question, answer)

    return AskResponse(
        answer=answer,
        session_id=body.session_id,
        sources_used=context.count("[Chunk"),
    )


@router.get(
    "/health",
    response_model=HealthResponse,
    summary="Health check",
    tags=["System"],
)
async def health_check() -> HealthResponse:
    """Return the current health and readiness status of the application."""
    assert _rag_service and _memory_service
    return HealthResponse(
        status="healthy",
        vector_store_ready=_rag_service.is_ready,
        total_vectors=_rag_service.total_vectors,
        active_sessions=_memory_service.active_sessions,
    )


@router.post(
    "/memory/clear",
    status_code=status.HTTP_200_OK,
    summary="Clear session memory",
    tags=["Memory"],
)
async def clear_memory(body: ClearMemoryRequest) -> dict:
    """Clear conversational memory for a given session."""
    assert _memory_service
    _memory_service.clear(body.session_id)
    return {"message": f"Memory cleared for session '{body.session_id}'."}
