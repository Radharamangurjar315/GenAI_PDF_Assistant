"""
Test suite for the GenAI PDF Bot API.

Uses ``pytest`` + ``httpx`` (via FastAPI's ``TestClient``) to verify
endpoint behaviour without requiring a live LLM backend.
"""

import os
import io

import pytest
from fastapi.testclient import TestClient

# Set test environment variables BEFORE importing the app
os.environ.setdefault("LLM_PROVIDER", "groq")
os.environ.setdefault("GROQ_API_KEY", "test-key-not-real")
os.environ.setdefault("OPENAI_API_KEY", "test-key-not-real")


from app.main import app  # noqa: E402


@pytest.fixture(scope="module")
def client():
    """Create a test client for the FastAPI app."""
    with TestClient(app) as c:
        yield c


# ------------------------------------------------------------------
# Root / Health
# ------------------------------------------------------------------

class TestHealthEndpoints:
    """Verify system health and root endpoints."""

    def test_root_returns_app_info(self, client: TestClient) -> None:
        """GET / should return app metadata."""
        resp = client.get("/")
        assert resp.status_code == 200
        data = resp.json()
        assert data["app"] == "GenAI PDF Bot"
        assert "docs" in data

    def test_health_check(self, client: TestClient) -> None:
        """GET /api/v1/health should return healthy status."""
        resp = client.get("/api/v1/health")
        assert resp.status_code == 200
        data = resp.json()
        assert data["status"] == "healthy"
        assert "total_vectors" in data
        assert "active_sessions" in data


# ------------------------------------------------------------------
# Upload validation
# ------------------------------------------------------------------

class TestUploadValidation:
    """Verify PDF upload validation logic."""

    def test_reject_non_pdf(self, client: TestClient) -> None:
        """POST /api/v1/upload should reject non-PDF files."""
        fake_file = io.BytesIO(b"not a pdf")
        resp = client.post(
            "/api/v1/upload",
            files={"file": ("document.txt", fake_file, "text/plain")},
        )
        assert resp.status_code == 400
        assert "PDF" in resp.json()["detail"]

    def test_reject_empty_body(self, client: TestClient) -> None:
        """POST /api/v1/upload with no file should return 422."""
        resp = client.post("/api/v1/upload")
        assert resp.status_code == 422


# ------------------------------------------------------------------
# Ask validation
# ------------------------------------------------------------------

class TestAskValidation:
    """Verify /ask endpoint input validation."""

    def test_reject_empty_question(self, client: TestClient) -> None:
        """POST /api/v1/ask with empty question should fail."""
        resp = client.post(
            "/api/v1/ask",
            json={"question": ""},
        )
        assert resp.status_code == 422

    def test_reject_no_documents(self, client: TestClient) -> None:
        """POST /api/v1/ask without uploaded docs should return 404."""
        resp = client.post(
            "/api/v1/ask",
            json={"question": "What is the summary?"},
        )
        # If no FAISS index exists, service raises ValueError → 404
        assert resp.status_code in (404, 502)


# ------------------------------------------------------------------
# Memory
# ------------------------------------------------------------------

class TestMemory:
    """Verify memory management endpoints."""

    def test_clear_memory(self, client: TestClient) -> None:
        """POST /api/v1/memory/clear should succeed."""
        resp = client.post(
            "/api/v1/memory/clear",
            json={"session_id": "test-session"},
        )
        assert resp.status_code == 200
        assert "cleared" in resp.json()["message"].lower()
