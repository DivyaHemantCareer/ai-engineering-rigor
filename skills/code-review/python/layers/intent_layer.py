from dataclasses import dataclass
from typing import Optional


@dataclass
class IntentContext:
    """
    Layer 2 — Intent behind the change.
    Provided by the developer per review.
    Helps LLM reason about PURPOSE not just syntax.
    """
    pr_description: Optional[str] = None
    ticket_id: Optional[str] = None
    spec_summary: Optional[str] = None

    def to_prompt_payload(self) -> str:
        """
        Serialize intent context into compact string.
        Empty fields are skipped to save tokens.
        """
        parts = []

        if self.pr_description:
            parts.append(f"PR DESCRIPTION:\n{self.pr_description}")

        if self.ticket_id:
            parts.append(f"TICKET: {self.ticket_id}")

        if self.spec_summary:
            parts.append(f"SPEC SUMMARY:\n{self.spec_summary}")

        if not parts:
            return "PR DESCRIPTION: Not provided — review based on code context only."

        return "\n\n".join(parts)

    def is_empty(self) -> bool:
        return not any([self.pr_description, self.ticket_id, self.spec_summary])
