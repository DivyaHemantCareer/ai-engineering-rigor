from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Optional
import os


@dataclass
class LLMConfig:
    """
    User-supplied LLM configuration.
    Skill is model-agnostic — user brings their own LLM.
    """
    provider: str                    # "azure" | "openai"
    api_key: str
    model: str                       # e.g. "gpt-4o-mini"
    endpoint: Optional[str] = None   # required for Azure
    api_version: Optional[str] = "2024-02-01"  # Azure API version
    temperature: float = 0.1         # low temperature — deterministic review
    max_tokens: int = 1500           # bounded response

    @classmethod
    def from_env(cls) -> "LLMConfig":
        """
        Load config from environment variables.
        Useful for CI pipelines and programmatic usage.
        """
        provider = os.getenv("LLM_PROVIDER", "azure")
        return cls(
            provider=provider,
            api_key=os.getenv("LLM_API_KEY", ""),
            model=os.getenv("LLM_MODEL", "gpt-4o-mini"),
            endpoint=os.getenv("LLM_ENDPOINT"),
            api_version=os.getenv("LLM_API_VERSION", "2024-02-01"),
            temperature=float(os.getenv("LLM_TEMPERATURE", "0.1")),
            max_tokens=int(os.getenv("LLM_MAX_TOKENS", "1500")),
        )


class LLMProvider(ABC):
    """Abstract base — any LLM can be plugged in."""

    @abstractmethod
    def complete(self, system_prompt: str, user_prompt: str) -> str:
        pass


class AzureAIFoundryProvider(LLMProvider):
    """Azure AI Foundry via OpenAI-compatible SDK."""

    def __init__(self, config: LLMConfig):
        try:
            from openai import AzureOpenAI
        except ImportError:
            raise ImportError("Run: pip install openai")

        self.client = AzureOpenAI(
            api_key=config.api_key,
            azure_endpoint=config.endpoint,
            api_version=config.api_version
        )
        self.model = config.model
        self.temperature = config.temperature
        self.max_tokens = config.max_tokens

    def complete(self, system_prompt: str, user_prompt: str) -> str:
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=self.temperature,
            max_tokens=self.max_tokens
        )
        return response.choices[0].message.content

class OpenAIProvider(LLMProvider):
    """Direct OpenAI API."""

    def __init__(self, config: LLMConfig):
        try:
            from openai import OpenAI
        except ImportError:
            raise ImportError("Run: pip install openai")

        self.client = OpenAI(api_key=config.api_key)
        self.model = config.model
        self.temperature = config.temperature
        self.max_tokens = config.max_tokens

    def complete(self, system_prompt: str, user_prompt: str) -> str:
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=self.temperature,
            max_tokens=self.max_tokens
        )
        return response.choices[0].message.content


def create_provider(config: LLMConfig) -> LLMProvider:
    """Factory — returns the right provider based on config."""
    if config.provider == "azure":
        return AzureAIFoundryProvider(config)
    elif config.provider == "openai":
        return OpenAIProvider(config)
    else:
        raise ValueError(f"Unsupported provider: {config.provider}. Use 'azure' or 'openai'")
