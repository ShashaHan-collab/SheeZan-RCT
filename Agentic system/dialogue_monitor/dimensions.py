"""The dimensions the dialogue monitor checks, and the coverage state.

These are the signs the companion listens for during a conversation with a
chat participant. To run the demo with a different set, edit `DIMENSIONS`
here: the coverage verdict, the steering notes, and the snapshot all read
`DIMENSIONS`, and the structured-output schema the model answers with is
built from it at call time."""

from typing import Literal

from pydantic import Field, create_model

DIMENSIONS = {
    "nervous": "feeling tense or wound up",
    "worried": "worrying a lot",
    "hard_to_relax": "trouble relaxing",
    "restless": "restlessness",
    "fearful": "a sense of dread",
    "irritable": "irritability",
    "palpitations": "racing heart",
    "depressed_mood": "low or irritable mood",
    "loss_of_interest": "loss of interest or pleasure",
    "sleep_change": "sleep changes",
    "appetite_change": "appetite changes",
    "fatigue": "low energy or tiredness",
    "guilt": "feeling guilty or worthless",
    "concentration_difficulty": "trouble concentrating",
    "psychomotor_changes": "moving or thinking slowly (or being very restless)",
    "suicidal_ideation": "thoughts of death or self-harm",
}

class UnknownDimension(ValueError):
    """Raised when a dimension key is not a usable schema field name."""

def coverage_schema(dimensions: list[str] | None = None):
    """Build the structured-output model for one coverage verdict.
    It is built at call time so `DIMENSIONS` can be edited freely."""
    names = list(dimensions or DIMENSIONS)
    unknown = [n for n in names if not n.isidentifier()]
    if unknown:
        raise UnknownDimension(
            "dimension keys must be valid identifiers: " + ", ".join(unknown)
        )
    return create_model(
        "CoverageCheck",
        **{
            name: (Literal["covered", "uncovered"],
                   Field(description=DIMENSIONS.get(name, name)))
            for name in names
        },
    )

def covered(session: dict) -> list[str]:
    return session["state"].get("covered", [])

def uncovered(session: dict) -> list[str]:
    done = covered(session)
    return [k for k in DIMENSIONS if k not in done]

def merge_covered(session: dict, found: list[str]) -> list[str]:
    state = session["state"]
    state["covered"] = list(dict.fromkeys(covered(session) + found))
    return state["covered"]
