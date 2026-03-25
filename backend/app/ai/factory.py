from functools import lru_cache
from app.ai.base import BaseLLMProvider
from app.core.config import get_settings


@lru_cache
def get_llm_provider() -> BaseLLMProvider:
    settings = get_settings()
    provider = settings.LLM_PROVIDER

    if provider == "openai":
        from app.ai.providers.openai_provider import OpenAIProvider
        return OpenAIProvider(api_key=settings.OPENAI_API_KEY, model=settings.OPENAI_MODEL)

    if provider == "anthropic":
        from app.ai.providers.anthropic_provider import AnthropicProvider
        return AnthropicProvider(api_key=settings.ANTHROPIC_API_KEY, model=settings.ANTHROPIC_MODEL)

    if provider == "gemini":
        from app.ai.providers.gemini_provider import GeminiProvider
        return GeminiProvider(api_key=settings.GEMINI_API_KEY, model=settings.GEMINI_MODEL)

    if provider == "ollama":
        from app.ai.providers.ollama_provider import OllamaProvider
        return OllamaProvider(base_url=settings.OLLAMA_BASE_URL, model=settings.OLLAMA_MODEL)

    raise ValueError(f"Unknown LLM provider: {provider}")
