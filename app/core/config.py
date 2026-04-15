"""
Application configuration module.

Loads environment variables and provides a centralized
configuration object used across all services.
"""

import os
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Optional

from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


class LLMProvider(str, Enum):
    """Supported LLM provider backends."""
    OPENAI = "openai"
    GROQ = "groq"


@dataclass(frozen=True)
class Settings:
    """
    Immutable application settings loaded from environment variables.

    Attributes:
        llm_provider: The LLM backend to use ('openai' or 'groq').
        openai_api_key: API key for OpenAI.
        groq_api_key: API key for Groq.
        openai_model: Model name for OpenAI completions.
        groq_model: Model name for Groq completions.
        embedding_model: Model name for generating embeddings.
        chunk_size: Number of characters per text chunk.
        chunk_overlap: Overlap between consecutive chunks.
        memory_window: Number of recent interactions to keep in memory.
        faiss_index_dir: Directory to persist FAISS index files.
        upload_dir: Directory for temporary PDF uploads.
        log_level: Application logging level.
    """

    # --- LLM Provider ---
    llm_provider: LLMProvider = field(
        default_factory=lambda: LLMProvider(
            os.getenv("LLM_PROVIDER", "groq").lower()
        )
    )

    # --- API Keys ---
    openai_api_key: Optional[str] = field(
        default_factory=lambda: os.getenv("OPENAI_API_KEY")
    )
    groq_api_key: Optional[str] = field(
        default_factory=lambda: os.getenv("GROQ_API_KEY")
    )

    # --- Model Names ---
    openai_model: str = field(
        default_factory=lambda: os.getenv("OPENAI_MODEL", "gpt-4o-mini")
    )
    groq_model: str = field(
        default_factory=lambda: os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")
    )
    embedding_model: str = field(
        default_factory=lambda: os.getenv(
            "EMBEDDING_MODEL", "sentence-transformers/all-MiniLM-L6-v2"
        )
    )

    # --- Chunking ---
    chunk_size: int = field(
        default_factory=lambda: int(os.getenv("CHUNK_SIZE", "1000"))
    )
    chunk_overlap: int = field(
        default_factory=lambda: int(os.getenv("CHUNK_OVERLAP", "200"))
    )

    # --- Memory ---
    memory_window: int = field(
        default_factory=lambda: int(os.getenv("MEMORY_WINDOW", "5"))
    )

    # --- Paths ---
    faiss_index_dir: Path = field(
        default_factory=lambda: Path(
            os.getenv("FAISS_INDEX_DIR", "data/faiss_index")
        )
    )
    upload_dir: Path = field(
        default_factory=lambda: Path(os.getenv("UPLOAD_DIR", "data/uploads"))
    )

    # --- Logging ---
    log_level: str = field(
        default_factory=lambda: os.getenv("LOG_LEVEL", "INFO").upper()
    )

    def __post_init__(self) -> None:
        """Validate settings after initialization."""
        if self.llm_provider == LLMProvider.OPENAI and not self.openai_api_key:
            raise ValueError(
                "OPENAI_API_KEY must be set when LLM_PROVIDER is 'openai'."
            )
        if self.llm_provider == LLMProvider.GROQ and not self.groq_api_key:
            raise ValueError(
                "GROQ_API_KEY must be set when LLM_PROVIDER is 'groq'."
            )

        # Ensure directories exist
        self.faiss_index_dir.mkdir(parents=True, exist_ok=True)
        self.upload_dir.mkdir(parents=True, exist_ok=True)

    @property
    def active_api_key(self) -> str:
        """Return the API key for the currently selected provider."""
        if self.llm_provider == LLMProvider.OPENAI:
            return self.openai_api_key  # type: ignore[return-value]
        return self.groq_api_key  # type: ignore[return-value]

    @property
    def active_model(self) -> str:
        """Return the model name for the currently selected provider."""
        if self.llm_provider == LLMProvider.OPENAI:
            return self.openai_model
        return self.groq_model


def get_settings() -> Settings:
    """
    Factory function that creates and returns a Settings instance.

    Returns:
        Settings: Validated application settings.
    """
    return Settings()
