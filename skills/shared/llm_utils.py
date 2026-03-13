"""LLM response parsing utilities."""

import json
from typing import Type, TypeVar
from pydantic import BaseModel

T = TypeVar("T", bound=BaseModel)


def parse_json_response(raw: str, model: Type[T]) -> T:
    """Parse an LLM response string into a validated Pydantic model.

    Strips markdown fences if the LLM wraps the response in ```json blocks.

    Args:
        raw: Raw LLM response string
        model: Pydantic model class to validate against

    Returns:
        Validated Pydantic model instance

    Raises:
        ValueError: If JSON parsing or validation fails
    """
    cleaned = raw.strip()
    if cleaned.startswith("```"):
        cleaned = cleaned.split("```")[1]
        if cleaned.startswith("json"):
            cleaned = cleaned[4:]
    cleaned = cleaned.strip()

    try:
        data = json.loads(cleaned)
        return model(**data)
    except json.JSONDecodeError as e:
        raise ValueError(f"LLM returned invalid JSON: {e}\nRaw response:\n{raw}")
    except Exception as e:
        raise ValueError(f"Response validation failed: {e}\nRaw response:\n{raw}")
