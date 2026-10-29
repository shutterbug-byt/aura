
import json

from backend.reasoning.model_client import ask_model


SYSTEM_PROMPT = """
You are AURA's activity-understanding engine.

Infer the most likely current activity from recent visual observations.

Rules:
- Use only evidence supported by the observations.
- Reason across observations to identify ongoing activities.
- Do not infer an activity from an object alone.
- Distinguish observable actions from assumptions about intentions.
- Prefer broad, well-supported activities over unsupported specifics.
- Maintain continuity when evidence supports the same activity.
- Recognize activity changes when evidence supports them.
- If evidence is insufficient, return "unclear".
- Do not provide advice or conversational responses.
- Return valid JSON only.
"""


def infer_activity(
    observations: list[dict],
    previous_activity: str = "",
) -> dict:
    """Infer the current activity from recent visual observations."""

    if not observations:
        return {
            "activity": "unclear",
            "reason": "No recent visual observations are available.",
        }

    payload = {
        "previous_activity": previous_activity,
        "recent_observations": observations,
    }

    response = ask_model(
        prompt=(
            "Infer the most likely current activity from the evidence below.\n"
            'Return one JSON object with exactly two string fields: '
            '"activity" and "reason".\n'
            "Do not include Markdown or additional fields.\n\n"
            + json.dumps(payload, ensure_ascii=False)
        ),
        system_prompt=SYSTEM_PROMPT,
        max_tokens=2048,
        json_mode=True,
        enable_thinking=False,
    )

    if not isinstance(response, str) or not response.strip():
        raise RuntimeError(
            "Activity inference model returned an empty response."
        )

    try:
        cleaned_response = response.strip()

        if cleaned_response.startswith("```"):
            cleaned_response = cleaned_response.split("\n", 1)[1]
            cleaned_response = cleaned_response.rsplit("```", 1)[0].strip()

        result = json.loads(cleaned_response)

    except (TypeError, json.JSONDecodeError, IndexError) as exc:
        print("Raw activity inference response:", repr(response))
        raise ValueError(
            "Activity inference returned invalid JSON."
        ) from exc

    if (
        not isinstance(result, dict)
        or not isinstance(result.get("activity"), str)
        or not isinstance(result.get("reason"), str)
    ):
        raise ValueError(
            "Activity inference returned an invalid structure."
        )

    return result
