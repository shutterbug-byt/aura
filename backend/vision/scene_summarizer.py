
import json

from backend.reasoning.model_client import ask_model


SYSTEM_PROMPT = """
You are AURA's visual scene summarizer.

Summarize only what the supplied observations support.
Do not invent objects, actions, intentions, emotions, or personal traits.
Distinguish recent activity from stable scene details.
If observations conflict, mention the uncertainty.
Return one valid JSON object only.
"""


def summarize_scene(
    observations: list[dict],
    previous_summary: str = "",
) -> dict:
    """Produce a concise, evidence-based summary of recent observations."""

    if not observations:
        return {
            "environment": "",
            "visible_entities": [],
            "recent_activity": "Not enough observations yet.",
            "uncertainties": [],
            "summary": previous_summary,
        }

    payload = {
        "previous_summary": previous_summary,
        "recent_observations": observations,
    }

    response = ask_model(
        prompt=(
            "Summarize these observations in concise JSON. Use exactly "
            "these fields: environment (string), visible_entities "
            "(array of strings), recent_activity (string), uncertainties "
            "(array of strings), summary (string). Keep every field brief. "
            "Use only the evidence supplied.\n\n"
            + json.dumps(payload, ensure_ascii=False)
        ),
        system_prompt=SYSTEM_PROMPT,
        max_tokens=512,
        json_mode=True,
        enable_thinking=False,
    )

    if not isinstance(response, str) or not response.strip():
        raise RuntimeError("Scene summarizer returned empty content.")

    try:
        result = json.loads(response.strip())
    except json.JSONDecodeError as exc:
        print("Raw scene summarizer response:", repr(response))
        raise ValueError(
            "Scene summarizer returned invalid JSON."
        ) from exc

    required_keys = {
        "environment",
        "visible_entities",
        "recent_activity",
        "uncertainties",
        "summary",
    }

    if not isinstance(result, dict) or not required_keys.issubset(result):
        raise ValueError("Scene summarizer returned an invalid structure.")

    if (
        not isinstance(result["environment"], str)
        or not isinstance(result["visible_entities"], list)
        or not all(isinstance(item, str) for item in result["visible_entities"])
        or not isinstance(result["recent_activity"], str)
        or not isinstance(result["uncertainties"], list)
        or not all(isinstance(item, str) for item in result["uncertainties"])
        or not isinstance(result["summary"], str)
    ):
        raise ValueError("Scene summarizer returned invalid field types.")

    return result
