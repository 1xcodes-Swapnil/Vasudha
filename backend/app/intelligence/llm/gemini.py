"""Google Gemini LLM provider implementation (Phase 8)."""

from typing import Optional
from backend.app.core.config import get_settings
from backend.app.core.errors import AIProviderError
from backend.app.core.logging import logger
from backend.app.intelligence.llm.base import LLMProvider, LLMResponse


class GeminiLLMProvider(LLMProvider):
    """LLM provider implementation for Google Gemini models with scientific guardrails."""

    def __init__(
        self,
        api_key: Optional[str] = None,
        model: Optional[str] = None,
    ):
        settings = get_settings()
        if api_key is not None:
            self._api_key = api_key
        else:
            self._api_key = settings.GEMINI_API_KEY

        self._model = model or settings.LLM_MODEL or "gemini-2.5-flash"
        self._client = None
        logger.info(f"Initialized GeminiLLMProvider with model='{self._model}'")

    @property
    def provider_name(self) -> str:
        return "gemini"

    @property
    def default_model(self) -> str:
        return self._model

    def _get_client(self):
        """Lazy initialization of Gemini client."""
        if self._client is not None:
            return self._client

        if not self._api_key or self._api_key in ("MY_GEMINI_API_KEY", "placeholder", ""):
            raise AIProviderError(
                "GEMINI_API_KEY is not configured. Please set the GEMINI_API_KEY environment variable."
            )

        try:
            from google import genai
            self._client = genai.Client(api_key=self._api_key)
            return self._client
        except ImportError:
            raise AIProviderError(
                "google-genai Python package is not installed. Install via pip or configure an alternate provider."
            )

    def generate(
        self,
        prompt: str,
        system_instruction: Optional[str] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
    ) -> LLMResponse:
        """Generate response using Gemini with strict grounding instruction."""
        client = self._get_client()
        settings = get_settings()
        temp = temperature if temperature is not None else settings.LLM_TEMPERATURE
        max_t = max_tokens or settings.LLM_MAX_OUTPUT_TOKENS

        # Default grounding guardrail: LLM is synthesis layer, NOT calculation or fact engine
        base_instruction = (
            "You are the conversational and synthesis interface for VASUDHA (Biodiversity Intelligence for a Living Earth). "
            "You MUST ground all scientific, quantitative, and ecological claims strictly in the provided "
            "structured environmental state and retrieved peer-reviewed scientific evidence. "
            "Never invent facts, metrics, or citations."
        )
        full_instruction = f"{base_instruction}\n\n{system_instruction}" if system_instruction else base_instruction

        try:
            config = {
                "system_instruction": full_instruction,
                "temperature": temp,
            }
            if max_t:
                config["max_output_tokens"] = max_t

            response = client.models.generate_content(
                model=self._model,
                contents=prompt,
                config=config,
            )
            text_content = response.text or ""
            return LLMResponse(
                content=text_content,
                model_name=self._model,
                provider_name=self.provider_name,
                prompt_tokens=len(prompt.split()),
                completion_tokens=len(text_content.split()),
                metadata={"grounding": "structured_evidence"},
            )
        except Exception as exc:
            err_msg = str(exc).lower()
            if "resource_exhausted" in err_msg or "quota" in err_msg or "429" in err_msg or "rate limit" in err_msg:
                logger.warning(
                    f"Gemini API quota/rate limit encountered ({exc}). Gracefully falling back to LocalLLMProvider."
                )
                from backend.app.intelligence.llm.local import LocalLLMProvider
                fallback_provider = LocalLLMProvider()
                return fallback_provider.generate(
                    prompt=prompt,
                    system_instruction=system_instruction,
                    temperature=temp,
                    max_tokens=max_tokens,
                )
            logger.error(f"Gemini generation error: {exc}")
            raise AIProviderError(f"Gemini API request failed: {exc}")

    async def generate_async(
        self,
        prompt: str,
        system_instruction: Optional[str] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
    ) -> LLMResponse:
        """Asynchronous generation using Gemini."""
        return self.generate(
            prompt=prompt,
            system_instruction=system_instruction,
            temperature=temperature,
            max_tokens=max_tokens,
        )
