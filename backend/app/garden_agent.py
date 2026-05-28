import os

from dotenv import load_dotenv

from .models import ApprovedAction, CameraObservation, ExplanationResponse, ForecastResponse, RiskScore


def _fallback_explanation(
    observation: CameraObservation,
    risks: list[RiskScore],
    forecast: ForecastResponse,
    recommendations: list[ApprovedAction],
) -> str:
    top_risk = max(risks, key=lambda risk: risk.score)
    action_labels = ", ".join(action.label for action in recommendations[:3])
    highest_forecast = max(forecast.bands, key=lambda band: band.p90_score)
    return (
        f"GardenSpace AI is watching {top_risk.label.lower()} most closely "
        f"({top_risk.status}, score {top_risk.score}/100). The image is tagged as "
        f"{', '.join(observation.detected_conditions)} with plant health "
        f"{observation.plant_health_index}/100 and confidence {round(observation.confidence * 100)}%. "
        f"The forecast's "
        f"highest p90 risk is {highest_forecast.label.lower()} at {highest_forecast.p90_score}/100. "
        f"Recommended employee-friendly actions: {action_labels}."
    )


async def explain_garden_state(
    observation: CameraObservation,
    risks: list[RiskScore],
    forecast: ForecastResponse,
    recommendations: list[ApprovedAction],
    include_ai: bool = True,
) -> ExplanationResponse:
    approved_action_ids = [action.id for action in recommendations]

    if not include_ai:
        return ExplanationResponse(
            explanation=_fallback_explanation(observation, risks, forecast, recommendations),
            approved_action_ids=approved_action_ids,
            used_ai=False,
        )

    load_dotenv()
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        return ExplanationResponse(
            explanation=_fallback_explanation(observation, risks, forecast, recommendations),
            approved_action_ids=approved_action_ids,
            used_ai=False,
        )

    try:
        from openai import AsyncOpenAI

        client = AsyncOpenAI(api_key=api_key)
        risk_lines = "\n".join(f"- {risk.id}: {risk.status}, {risk.score}/100" for risk in risks)
        action_lines = "\n".join(
            f"- {action.id}: {action.label}; human approval required={action.requires_human_approval}"
            for action in recommendations
        )
        response = await client.chat.completions.create(
            model=os.getenv("OPENAI_MODEL", "gpt-4o-mini"),
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You explain camera observations of an indoor workplace vertical tower garden. "
                        "Use simple employee-friendly language. Never invent hardware commands or claim action was taken. "
                        "Recommend only the provided approved action IDs."
                    ),
                },
                {
                    "role": "user",
                    "content": (
                        f"Camera observation: {observation.model_dump()}\n"
                        f"Deterministic visual risks:\n{risk_lines}\n"
                        f"Approved actions:\n{action_lines}\n"
                        f"Forecast note: {forecast.note}\n"
                        "Write a concise employee-facing explanation."
                    ),
                },
            ],
            temperature=0.2,
            max_tokens=220,
        )
        content = response.choices[0].message.content or ""
        return ExplanationResponse(
            explanation=content.strip() or _fallback_explanation(observation, risks, forecast, recommendations),
            approved_action_ids=approved_action_ids,
            used_ai=True,
        )
    except Exception:
        return ExplanationResponse(
            explanation=_fallback_explanation(observation, risks, forecast, recommendations),
            approved_action_ids=approved_action_ids,
            used_ai=False,
        )
