"""
Utility helpers for the GenAI PDF Bot.

Provides PDF text extraction, text chunking,
file-validation, and sanitisation utilities.
"""

import logging
import re
from pathlib import Path
from typing import List

from langchain_text_splitters import RecursiveCharacterTextSplitter
from pypdf import PdfReader

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------
ALLOWED_EXTENSIONS: set[str] = {".pdf"}
MAX_FILE_SIZE_MB: int = 20


# ---------------------------------------------------------------------------
# Validation
# ---------------------------------------------------------------------------

def validate_pdf(file_path: Path) -> None:
    """
    Validate that *file_path* points to a legitimate PDF.

    Raises:
        ValueError: If the file does not exist, has the wrong extension,
                    exceeds the size limit, or cannot be read by PyPDF.
    """
    if not file_path.exists():
        raise ValueError(f"File not found: {file_path}")

    if file_path.suffix.lower() not in ALLOWED_EXTENSIONS:
        raise ValueError(
            f"Unsupported file type '{file_path.suffix}'. Only PDF files are accepted."
        )

    size_mb = file_path.stat().st_size / (1024 * 1024)
    if size_mb > MAX_FILE_SIZE_MB:
        raise ValueError(
            f"File size ({size_mb:.1f} MB) exceeds the "
            f"{MAX_FILE_SIZE_MB} MB limit."
        )

    # Quick parse check
    try:
        reader = PdfReader(str(file_path))
        if len(reader.pages) == 0:
            raise ValueError("The PDF has zero pages.")
    except Exception as exc:
        raise ValueError(f"Cannot read PDF: {exc}") from exc


# ---------------------------------------------------------------------------
# Text extraction
# ---------------------------------------------------------------------------

def extract_text_from_pdf(file_path: Path) -> str:
    """
    Extract and return all text from a PDF file.

    Args:
        file_path: Path to the PDF file.

    Returns:
        Concatenated text of all pages.

    Raises:
        ValueError: If no text could be extracted.
    """
    logger.info("Extracting text from %s", file_path.name)
    reader = PdfReader(str(file_path))
    pages_text: list[str] = []

    for i, page in enumerate(reader.pages):
        text = page.extract_text()
        if text:
            pages_text.append(text)
        else:
            logger.warning("Page %d of %s yielded no text.", i + 1, file_path.name)

    full_text = "\n\n".join(pages_text)
    if not full_text.strip():
        raise ValueError(
            "No extractable text found in the PDF. "
            "The file may be scanned or image-only."
        )

    logger.info(
        "Extracted %d characters from %d page(s).",
        len(full_text),
        len(reader.pages),
    )
    return full_text


# ---------------------------------------------------------------------------
# Chunking
# ---------------------------------------------------------------------------

def split_text_into_chunks(
    text: str,
    chunk_size: int = 1000,
    chunk_overlap: int = 200,
) -> List[str]:
    """
    Split *text* into overlapping chunks for embedding.

    Uses LangChain's RecursiveCharacterTextSplitter, which attempts
    to split at paragraph / sentence boundaries first.

    Args:
        text: The full document text.
        chunk_size: Maximum number of characters per chunk.
        chunk_overlap: Number of overlapping characters between chunks.

    Returns:
        A list of text chunks.
    """
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        length_function=len,
        separators=["\n\n", "\n", ". ", " ", ""],
    )
    chunks = splitter.split_text(text)
    logger.info("Split text into %d chunks (size=%d, overlap=%d).",
                len(chunks), chunk_size, chunk_overlap)
    return chunks


# ---------------------------------------------------------------------------
# Sanitisation
# ---------------------------------------------------------------------------

def sanitise_query(query: str) -> str:
    """
    Clean and normalise a user query string.

    - Strips leading/trailing whitespace.
    - Collapses multiple spaces.

    Args:
        query: Raw user input.

    Returns:
        Sanitised query string.

    Raises:
        ValueError: If query is empty after sanitisation.
    """
    cleaned = re.sub(r"\s+", " ", query.strip())
    if not cleaned:
        raise ValueError("Query cannot be empty.")
    return cleaned
