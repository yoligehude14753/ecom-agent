from typing import AsyncIterator
import anthropic
from app.ai.base import BaseLLMProvider, LLMMessage, LLMResponse


class AnthropicProvider(BaseLLMProvider):
    def __init__(self, api_key: str, model: str = "claude-3-5-sonnet-20241022") -> None:
        self._client = anthropic.AsyncAnthropic(api_key=api_key)
        self._model = model

    async def chat(
        self,
        messages: list[LLMMessage],
        temperature: float = 0.7,
        max_tokens: int = 4096,
    ) -> LLMResponse:
        system = next((m.content for m in messages if m.role == "system"), None)
        non_system = [{"role": m.role, "content": m.content} for m in messages if m.role != "system"]

        kwargs: dict = dict(
            model=self._model,
            max_tokens=max_tokens,
            temperature=temperature,
            messages=non_system,
        )
        if system:
            kwargs["system"] = system

        resp = await self._client.messages.create(**kwargs)
        content = resp.content[0].text if resp.content else ""
        return LLMResponse(
            content=content,
            model=self._model,
            prompt_tokens=resp.usage.input_tokens,
            completion_tokens=resp.usage.output_tokens,
            total_tokens=resp.usage.input_tokens + resp.usage.output_tokens,
        )

    async def stream(
        self,
        messages: list[LLMMessage],
        temperature: float = 0.7,
        max_tokens: int = 4096,
    ) -> AsyncIterator[str]:
        system = next((m.content for m in messages if m.role == "system"), None)
        non_system = [{"role": m.role, "content": m.content} for m in messages if m.role != "system"]

        kwargs: dict = dict(
            model=self._model,
            max_tokens=max_tokens,
            temperature=temperature,
            messages=non_system,
        )
        if system:
            kwargs["system"] = system

        async with self._client.messages.stream(**kwargs) as stream:
            async for text in stream.text_stream:
                yield text
