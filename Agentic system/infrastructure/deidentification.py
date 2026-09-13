"""De-identification for information sent to the model provider.

These rules are an example, not a fixed recipe. Which patterns to match,
and how aggressively, depends on the data a deployment collects and the
risk it accepts.

This rule-based filter is not a substitute for a validated de-identification
service. A deployment that handles real chat participants should replace
`filter_information` with one.

Note: A locally deployed LLM can replace this rule-based filter.
"""

import re

DATE = re.compile(r"^\d{2,4}[-/.]\d{1,2}[-/.]\d{1,4}$")

def _redact_phone(match: re.Match) -> str:
    return match.group(0) if DATE.match(match.group(0)) else "[phone]"

RULES = [
    (re.compile(r"[\w.+-]+@[\w-]+\.[\w.]+"), "[email]"),
    (re.compile(r"\b(?:https?://|www\.)\S+", re.IGNORECASE), "[link]"),
    (re.compile(r"(?<!\w)(?:\+\d{1,3}[ -]?)?(?:\d{2,4}[ -]){1,3}\d{2,4}(?!\w)"), _redact_phone),
    (re.compile(r"(?<!\d)\d{7,}(?!\d)"), "[number]"),
    (re.compile(
        r"(?:[Mm]y name is|I am called|I'm called|[Cc]all me|[Yy]ou can call me)\s+"
        r"([A-Z][a-z]+(?:\s+[A-Z][a-z]+)?)"), "[name]"),
]

def filter_information(messages: list[dict]) -> list[dict]:
    out = []
    for m in messages:
        text = m.get("content")
        if not isinstance(text, str):
            out.append(m)
            continue
        for pattern, replacement in RULES:
            text = pattern.sub(replacement, text)
        out.append({**m, "content": text})
    return out
