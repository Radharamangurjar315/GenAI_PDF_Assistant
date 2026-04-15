"""
LLM service — provider-agnostic interface to language models.

Supports OpenAI and Groq as configurable backends, using LangChain
chat-model wrappers for a consistent API surface.
"""

import logging
from typing import Optional

from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_openai import ChatOpenAI

from app.core.config import LLMProvider, Settings

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Prompt template
# ---------------------------------------------------------------------------

SYSTEM_PROMPT: str = (
    "You are an expert AI assistant specialising in answering questions "
    "about uploaded documents. Be precise, cite the document content when "
    "possible, and acknowledge when information is not available in the "
    "provided context. Maintain a professional yet approachable tone."
)

RAG_USER_TEMPLATE: str = """Use the following pieces of retrieved context and the conversation history to answer the user's question.
If the answer is not in the context, say "I don't have enough information in the uploaded documents to answer this question."

--- CONVERSATION HISTORY ---
{history}

--- RETRIEVED CONTEXT ---
{context}

--- USER QUESTION ---
{question}

Answer:"""


# ---------------------------------------------------------------------------
# Service
# ---------------------------------------------------------------------------

class LLMService:
    """
    Thin wrapper around LangChain chat models.

    Automatically selects the correct provider (OpenAI / Groq) based on
    application settings and exposes a single ``generate`` method.
    """

    def __init__(self, settings: Settings) -> None:
        """
        Initialise the LLM service with the active provider.

        Args:
            settings: Application-wide settings instance.
        """
        self._settings = settings
        self._llm: BaseChatModel = self._build_llm()
        logger.info(
            "LLMService ready — provider=%s  model=%s",
            settings.llm_provider.value,
            settings.active_model,
        )

    # ------------------------------------------------------------------
    # Internal
    # ------------------------------------------------------------------

    def _build_llm(self) -> BaseChatModel:
        """
        Construct the appropriate LangChain chat model.

        Returns:
            A configured ``BaseChatModel`` instance.
        """
        if self._settings.llm_provider == LLMProvider.OPENAI:
            return ChatOpenAI(
                model=self._settings.openai_model,
                api_key=self._settings.openai_api_key,
                temperature=0.3,
                max_tokens=1024,
            )
        # Groq uses OpenAI-compatible API, so we use ChatOpenAI with
        # the Groq base URL.
        return ChatOpenAI(
            model=self._settings.groq_model,
            api_key=self._settings.groq_api_key,
            base_url="https://api.groq.com/openai/v1",
            temperature=0.3,
            max_tokens=1024,
        )

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    async def generate(
        self,
        question: str,
        context: str,
        history: str,
        system_prompt: Optional[str] = None,
    ) -> str:
        """
        Generate an LLM response using RAG context and conversation history.

        Args:
            question: The user's query.
            context: Relevant document chunks retrieved from the vector store.
            history: Formatted conversation history string.
            system_prompt: Optional override for the system message.

        Returns:
            The model's generated answer as a plain string.
        """
        sys_msg = SystemMessage(content=system_prompt or SYSTEM_PROMPT)
        user_msg = HumanMessage(
            content=RAG_USER_TEMPLATE.format(
                history=history,
                context=context,
                question=question,
            )
        )

        logger.debug("Sending prompt to LLM (question=%r).", question[:80])
        response = await self._llm.ainvoke([sys_msg, user_msg])
        answer: str = response.content  # type: ignore[assignment]
        logger.info("LLM responded (%d chars).", len(answer))
        return answer
