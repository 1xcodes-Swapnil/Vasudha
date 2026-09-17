"""Local/Mock LLM Provider for offline evaluation and deterministic testing (Phase 8)."""

from typing import Optional
from backend.app.core.logging import logger
from backend.app.intelligence.llm.base import LLMProvider, LLMResponse


class LocalLLMProvider(LLMProvider):
    """Deterministic offline LLM provider for local testing and graceful fallback."""

    def __init__(self, model: str = "local-deterministic-mock"):
        self._model = model
        logger.info(f"Initialized LocalLLMProvider with model='{self._model}'")

    @property
    def provider_name(self) -> str:
        return "local"

    @property
    def default_model(self) -> str:
        return self._model

    def generate(
        self,
        prompt: str,
        system_instruction: Optional[str] = None,
        temperature: float = 0.2,
        max_tokens: Optional[int] = None,
    ) -> LLMResponse:
        """Generates a structured, deterministic response."""
        content = (
            f"[LocalLLMProvider Synthesis]\n"
            f"Grounding Mode: Deterministic Knowledge Layer\n"
            f"Prompt Analysis: Processed {len(prompt.split())} tokens.\n"
            f"Response: Based on ecological reasoning and scientific RAG evidence packets, "
            f"the assessed environmental dynamics follow established biological mechanisms."
        )
        return LLMResponse(
            content=content,
            model_name=self._model,
            provider_name=self.provider_name,
            prompt_tokens=len(prompt.split()),
            completion_tokens=len(content.split()),
            metadata={"mode": "deterministic_mock"},
        )

    async def generate_async(
        self,
        prompt: str,
        system_instruction: Optional[str] = None,
        temperature: float = 0.2,
        max_tokens: Optional[int] = None,
    ) -> LLMResponse:
        return self.generate(
            prompt=prompt,
            system_instruction=system_instruction,
            temperature=temperature,
            max_tokens=max_tokens,
        )
