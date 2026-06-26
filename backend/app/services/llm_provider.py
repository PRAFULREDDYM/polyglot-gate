from abc import ABC, abstractmethod
from time import perf_counter
from typing import Optional

from app.config import settings


class LLMProvider(ABC):
    @abstractmethod
    def generate(
        self,
        prompt: str,
        locale: str = "en",
        system: Optional[str] = None,
    ) -> dict:
        """Generate model text and return text, latency_ms, and model metadata."""


class AnthropicProvider(LLMProvider):
    def __init__(self, model: str = "claude-sonnet-4-6", max_tokens: int = 1024):
        if not settings.ANTHROPIC_API_KEY:
            raise RuntimeError(
                "ANTHROPIC_API_KEY is required when LLM_PROVIDER is set to anthropic."
            )

        try:
            from anthropic import Anthropic
        except ImportError as exc:
            raise RuntimeError(
                "The anthropic package is required when LLM_PROVIDER is set to anthropic."
            ) from exc

        self.client = Anthropic(api_key=settings.ANTHROPIC_API_KEY)
        self.model = model
        self.max_tokens = max_tokens

    def generate(
        self,
        prompt: str,
        locale: str = "en",
        system: Optional[str] = None,
    ) -> dict:
        system_prompt = system
        if locale != "en":
            locale_instruction = (
                f"Respond fluently in the language associated with locale '{locale}'."
            )
            system_prompt = (
                f"{locale_instruction}\n\n{system}" if system else locale_instruction
            )

        start = perf_counter()
        request = {
            "model": self.model,
            "max_tokens": self.max_tokens,
            "messages": [{"role": "user", "content": prompt}],
        }
        if system_prompt:
            request["system"] = system_prompt

        response = self.client.messages.create(**request)
        latency_ms = int((perf_counter() - start) * 1000)

        text_parts = [
            block.text for block in response.content if getattr(block, "text", None)
        ]
        text = "".join(text_parts)

        return {"text": text, "latency_ms": latency_ms, "model": self.model}


class MockProvider(LLMProvider):
    def generate(
        self,
        prompt: str,
        locale: str = "en",
        system: Optional[str] = None,
    ) -> dict:
        return {
            "text": f"[MOCK-{locale}] {prompt}",
            "latency_ms": 10,
            "model": "mock",
        }


def get_llm_provider() -> LLMProvider:
    if settings.LLM_PROVIDER.strip().lower() == "anthropic":
        return AnthropicProvider()
    return MockProvider()


if __name__ == "__main__":
    print(MockProvider().generate("hello", "en"))
