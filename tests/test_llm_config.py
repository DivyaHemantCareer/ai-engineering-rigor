"""Tests for configurable LLM parameters."""

import os
import pytest

from skills.code_review.python.llm_provider import LLMConfig


class TestLLMConfig:
    def test_default_temperature_and_max_tokens(self):
        config = LLMConfig(provider="openai", api_key="k", model="m")
        assert config.temperature == 0.1
        assert config.max_tokens == 1500

    def test_custom_temperature_and_max_tokens(self):
        config = LLMConfig(
            provider="openai", api_key="k", model="m",
            temperature=0.7, max_tokens=3000,
        )
        assert config.temperature == 0.7
        assert config.max_tokens == 3000

    def test_from_env_reads_temperature(self, monkeypatch):
        monkeypatch.setenv("LLM_API_KEY", "test-key")
        monkeypatch.setenv("LLM_TEMPERATURE", "0.5")
        monkeypatch.setenv("LLM_MAX_TOKENS", "2000")
        config = LLMConfig.from_env()
        assert config.temperature == 0.5
        assert config.max_tokens == 2000

    def test_from_env_defaults(self, monkeypatch):
        monkeypatch.delenv("LLM_TEMPERATURE", raising=False)
        monkeypatch.delenv("LLM_MAX_TOKENS", raising=False)
        config = LLMConfig.from_env()
        assert config.temperature == 0.1
        assert config.max_tokens == 1500
