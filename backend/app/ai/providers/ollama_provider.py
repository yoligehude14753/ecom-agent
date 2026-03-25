from typing import AsyncIterator
import httpx
from app.ai.base import BaseLLMProvider, LLMMessage, LLMResponse


class OllamaProvider(BaseLLMProvider):
    def __init__(self, base_url: str = "http://localhost:11434", model: str = "llama3.1") -> None:
        self._base_url = base_url.rstrip("/")
        self._model = model

    async def chat(
        self,
        messages: list[LLMMessage],
        temperature: float = 0.7,
        max_tokens: int = 4096,
    ) -> LLMResponse:
        async with httpx.AsyncClient(timeout=120) as client:
            resp = await client.post(
                f"{self._base_url}/api/chat",
                json={
                    "model": self._model,
                    "messages": [{"role": m.role, "content": m.content} for m in messages],
                    "stream": False,
                    "options": {"temperature": temperature, "num_predict": max_tokens},
                },
            )
            resp.raise_for_status()
            data = resp.json()
            content = data["message"]["content"]
            prompt_eval_count = data.get("prompt_eval_count", 0)
            eval_count = data.get("eval_count", 0)
            return LLMResponse(
                content=content,
                model=self._model,
                prompt_tokens=prompt_eval_count,
                completion_tokens=eval_count,
                total_tokens=prompt_eval_count + eval_count,
            )

    async def stream(
        self,
        messages: list[LLMMessage],
        temperature: float = 0.7,
        max_tokens: int = 4096,
    ) -> AsyncIterator[str]:
        import json
        async with httpx.AsyncClient(timeout=120) as client:
            async with client.stream(
                "POST",
                f"{self._base_url}/api/chat",
                json={
                    "model": self._model,
                    "messages": [{"role": m.role, "content": m.content} for m in messages],
                    "stream": True,
                    "options": {"temperature": temperature, "num_predict": max_tokens},
                },
            ) as resp:
                async for line in resp.aiter_lines():
                    if line:
                        data = json.loads(line)
                        delta = data.get("message", {}).get("content", "")
                        if delta:
                            yield delta
