"""
RAG (Retrieval-Augmented Generation) service.

Handles:
  • Embedding generation via HuggingFace sentence-transformers.
  • FAISS vector-store creation and persistence.
  • Semantic similarity search for relevant document chunks.
"""

import logging
from pathlib import Path
from typing import List, Optional

from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings

from app.core.config import Settings

logger = logging.getLogger(__name__)


class RAGService:
    """
    Manages the FAISS vector store and provides retrieval capabilities.

    The service lazily loads or creates the FAISS index, and exposes
    methods for adding new document chunks and querying the store.
    """

    def __init__(self, settings: Settings) -> None:
        """
        Initialise the RAG service.

        Args:
            settings: Application-wide settings instance.
        """
        self._settings = settings
        self._index_path: Path = settings.faiss_index_dir
        self._embeddings = HuggingFaceEmbeddings(
            model_name=settings.embedding_model,
            model_kwargs={"device": "cpu"},
            encode_kwargs={"normalize_embeddings": True},
        )
        self._vectorstore: Optional[FAISS] = self._load_existing_index()
        logger.info(
            "RAGService initialised — embedding_model=%s  index_loaded=%s",
            settings.embedding_model,
            self._vectorstore is not None,
        )

    # ------------------------------------------------------------------
    # Internal
    # ------------------------------------------------------------------

    def _load_existing_index(self) -> Optional[FAISS]:
        """
        Attempt to load a previously persisted FAISS index.

        Returns:
            A ``FAISS`` vectorstore if found, otherwise ``None``.
        """
        index_file = self._index_path / "index.faiss"
        if index_file.exists():
            try:
                store = FAISS.load_local(
                    str(self._index_path),
                    self._embeddings,
                    allow_dangerous_deserialization=True,
                )
                logger.info("Loaded existing FAISS index from %s.", self._index_path)
                return store
            except Exception as exc:
                logger.warning("Could not load FAISS index: %s", exc)
        return None

    def _save_index(self) -> None:
        """Persist the current FAISS index to disk."""
        if self._vectorstore is not None:
            self._vectorstore.save_local(str(self._index_path))
            logger.info("FAISS index saved to %s.", self._index_path)

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    async def add_documents(self, chunks: List[str], source: str = "unknown") -> int:
        """
        Embed and add text chunks to the vector store.

        Args:
            chunks: List of text chunks to embed and store.
            source: Descriptive name for the source document.

        Returns:
            Total number of vectors now in the store.
        """
        metadatas = [{"source": source, "chunk_index": i} for i in range(len(chunks))]

        if self._vectorstore is None:
            self._vectorstore = FAISS.from_texts(
                texts=chunks,
                embedding=self._embeddings,
                metadatas=metadatas,
            )
            logger.info("Created new FAISS index with %d chunks.", len(chunks))
        else:
            self._vectorstore.add_texts(texts=chunks, metadatas=metadatas)
            logger.info("Added %d chunks to existing FAISS index.", len(chunks))

        self._save_index()
        return self._vectorstore.index.ntotal  # type: ignore[union-attr]

    async def search(self, query: str, top_k: int = 4) -> str:
        """
        Perform semantic similarity search against stored documents.

        Args:
            query: The user query to search for.
            top_k: Number of top-matching chunks to return.

        Returns:
            Concatenated relevant text chunks as a single context string.

        Raises:
            ValueError: If no documents have been indexed yet.
        """
        if self._vectorstore is None:
            raise ValueError(
                "No documents have been uploaded yet. "
                "Please upload a PDF before asking questions."
            )

        docs = self._vectorstore.similarity_search(query, k=top_k)
        logger.info("Retrieved %d chunks for query: %r", len(docs), query[:80])

        context_parts: list[str] = []
        for i, doc in enumerate(docs, 1):
            source = doc.metadata.get("source", "unknown")
            context_parts.append(
                f"[Chunk {i} | Source: {source}]\n{doc.page_content}"
            )

        return "\n\n".join(context_parts)

    @property
    def is_ready(self) -> bool:
        """Return ``True`` if the vector store has at least one document."""
        return self._vectorstore is not None

    @property
    def total_vectors(self) -> int:
        """Return the total number of vectors in the store."""
        if self._vectorstore is None:
            return 0
        return self._vectorstore.index.ntotal  # type: ignore[union-attr]
