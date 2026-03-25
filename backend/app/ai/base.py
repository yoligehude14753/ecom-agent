from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import AsyncIterator


@dataclass
class LLMMessage:
    role: str  # system | user | assistant
    content: str


@dataclass
class LLMResponse:
    content: str
    model: str
    prompt_tokens: int
    completion_tokens: int
    total_tokens: int


class BaseLLMProvider(ABC):
    """Abstract base for all LLM providers."""

    @abstractmethod
    async def chat(
        self,
        messages: list[LLMMessage],
        temperature: float = 0.7,
        max_tokens: int = 4096,
    ) -> LLMResponse:
        ...

    @abstractmethod
    async def stream(
        self,
        messages: list[LLMMessage],
        temperature: float = 0.7,
        max_tokens: int = 4096,
    ) -> AsyncIterator[str]:
        ...

    async def complete(self, prompt: str, system: str = "", **kwargs) -> str:
        """Convenience wrapper: single user turn."""
        messages = []
        if system:
            messages.append(LLMMessage(role="system", content=system))
        messages.append(LLMMessage(role="user", content=prompt))
        response = await self.chat(messages, **kwargs)
        return response.content
