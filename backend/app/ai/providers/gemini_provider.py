from typing import AsyncIterator
import google.generativeai as genai
from app.ai.base import BaseLLMProvider, LLMMessage, LLMResponse


class GeminiProvider(BaseLLMProvider):
    def __init__(self, api_key: str, model: str = "gemini-1.5-pro") -> None:
        genai.configure(api_key=api_key)
        self._model_name = model
        self._model = genai.GenerativeModel(model)

    async def chat(
        self,
        messages: list[LLMMessage],
        temperature: float = 0.7,
        max_tokens: int = 4096,
    ) -> LLMResponse:
        history = []
        for m in messages:
            if m.role == "system":
                history.append({"role": "user", "parts": [f"[System]: {m.content}"]})
                history.append({"role": "model", "parts": ["Understood."]})
            elif m.role == "user":
                history.append({"role": "user", "parts": [m.content]})
            elif m.role == "assistant":
                history.append({"role": "model", "parts": [m.content]})

        last = history.pop()
        chat = self._model.start_chat(history=history)
        config = genai.types.GenerationConfig(temperature=temperature, max_output_tokens=max_tokens)
        resp = await chat.send_message_async(last["parts"][0], generation_config=config)
        text = resp.text or ""
        usage = resp.usage_metadata
        return LLMResponse(
            content=text,
            model=self._model_name,
            prompt_tokens=usage.prompt_token_count,
            completion_tokens=usage.candidates_token_count,
            total_tokens=usage.total_token_count,
        )

    async def stream(
        self,
        messages: list[LLMMessage],
        temperature: float = 0.7,
        max_tokens: int = 4096,
    ) -> AsyncIterator[str]:
        history = []
        for m in messages:
            if m.role == "system":
                history.append({"role": "user", "parts": [f"[System]: {m.content}"]})
                history.append({"role": "model", "parts": ["Understood."]})
            elif m.role == "user":
                history.append({"role": "user", "parts": [m.content]})
            elif m.role == "assistant":
                history.append({"role": "model", "parts": [m.content]})

        last = history.pop()
        chat = self._model.start_chat(history=history)
        config = genai.types.GenerationConfig(temperature=temperature, max_output_tokens=max_tokens)
        async for chunk in await chat.send_message_async(last["parts"][0], generation_config=config, stream=True):
            if chunk.text:
                yield chunk.text
