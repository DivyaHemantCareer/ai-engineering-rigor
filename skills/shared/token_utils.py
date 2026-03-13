"""Token estimation and budget management utilities."""


def estimate_tokens(text: str) -> int:
    """Estimate token count using word_count * 1.3 heuristic."""
    word_count = len(text.split())
    return int(word_count * 1.3)


def truncate_to_budget(text: str, max_tokens: int) -> str:
    """Truncate text to fit within a token budget.

    Uses the same word-based heuristic as estimate_tokens.
    Truncates at word boundaries and appends a marker.
    """
    words = text.split()
    max_words = int(max_tokens / 1.3)
    if len(words) <= max_words:
        return text
    return " ".join(words[:max_words]) + "\n[...truncated to fit token budget]"
