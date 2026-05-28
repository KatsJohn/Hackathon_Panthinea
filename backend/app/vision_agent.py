import json
import os
from datetime import UTC, datetime

from dotenv import load_dotenv
from openai import OpenAI

from .image_utils import image_to_data_url, validate_base64_image
from .models import (
    AgentResponse,
    EmployeeRecipient,
    MeetingSuggestion,
    NotificationDecision,
    PhoneNotification,
    PhoneNotificationResult,
    VisionObservation,
)


MOCK_EMPLOYEE = EmployeeRecipient(
    employee_id="mock-garden-care-employee",
    display_name="Garden Care Employee",
    role="Facilities / Sustainability Team",
    phone_label="Employee phone",
)

SYSTEM_PROMPT = """
You are GardenSpace AI, a privacy-conscious workplace tower-garden assistant.
Analyze only:
- tower garden condition
- visible plant health
- visible dryness or wilting
- whether the area looks clean or neglected
- whether the water or reservoir area may need checking
- whether the space appears free, occupied, cluttered, or unknown
- whether it is suitable for a short employee meeting or wellbeing break

Privacy rules:
- Do not identify people.
- Do not describe faces.
- Do not infer age, gender, emotions, health, job role, productivity, or identity.
- If people are visible, say only whether the area appears occupied.
- Use uncertain language such as "appears", "may need", "suggests", and "worth checking".
- Do not claim watering, maintenance, or notification delivery occurred.

Return JSON only. Do not include markdown.
""".strip()

JSON_INSTRUCTIONS = """
Return exactly this JSON shape:
{
  "summary": "short employee-friendly summary",
  "observations": {
    "plant_health_status": "healthy | possibly_dry | possibly_wilted | needs_attention | unknown",
    "water_check_needed": true,
    "area_status": "free | occupied | cluttered | unknown",
    "visible_issues": ["short issue strings"],
    "confidence": 0.0
  },
  "notification": {
    "should_notify": true,
    "urgency": "low | medium | high",
    "notification_title": "phone-style title",
    "notification_message": "phone-style message for the mock employee",
    "suggested_employee_action": "one practical next step"
  },
  "meeting_suggestion": {
    "should_suggest_meeting": false,
    "meeting_type": "none | wellbeing_break | team_check_in",
    "reason": "short reason",
    "suggested_duration_minutes": 0
  },
  "employee_friendly_explanation": "plain-language explanation of what appears visible",
  "limitations": "privacy and uncertainty limitations"
}
""".strip()


def _created_at() -> str:
    return datetime.now(UTC).isoformat()


def _build_phone_notification(notification: NotificationDecision) -> PhoneNotificationResult:
    delivered = notification.should_notify
    return PhoneNotificationResult(
        notification=PhoneNotification(
            notification_id=f"mock-phone-{datetime.now(UTC).strftime('%Y%m%d%H%M%S%f')}",
            recipient=MOCK_EMPLOYEE,
            title=notification.notification_title,
            message=notification.notification_message,
            urgency=notification.urgency,
            channel="mock_phone",
            status="sent" if delivered else "created",
            created_at=_created_at(),
        ),
        delivered_to_mock_phone=delivered,
        delivery_note=(
            "Simulated phone notification delivered to the in-app mock phone."
            if delivered
            else "No simulated phone notification was sent because the image does not suggest employee action right now."
        ),
    )


def _safe_fallback_response(reason: str) -> AgentResponse:
    observations = VisionObservation(
        plant_health_status="unknown",
        water_check_needed=True,
        area_status="unknown",
        visible_issues=["Image analysis was unavailable.", reason],
        confidence=0.0,
    )
    notification = NotificationDecision(
        should_notify=True,
        urgency="medium",
        notification_title="Garden check recommended",
        notification_message=(
            "GardenSpace AI: I could not confidently analyze the garden image. "
            "Please visually inspect the tower garden and reservoir when you can."
        ),
        suggested_employee_action="Inspect the tower garden plants and reservoir area.",
    )
    meeting_suggestion = MeetingSuggestion(
        should_suggest_meeting=False,
        meeting_type="none",
        reason="The image could not be analyzed confidently, so the space should not be suggested for a meeting.",
        suggested_duration_minutes=0,
    )
    return AgentResponse(
        summary="GardenSpace AI could not confidently analyze the image.",
        observations=observations,
        notification=notification,
        phone_notification_result=_build_phone_notification(notification),
        meeting_suggestion=meeting_suggestion,
        employee_friendly_explanation=(
            "The camera-based analysis is unavailable or uncertain. "
            "A human should check whether the plants appear healthy and whether the reservoir may need attention."
        ),
        limitations=(
            "This is a simulated camera-based demo. It does not identify people, analyze faces, track individuals, "
            "or claim certainty from images. Real systems should use consent, secure storage, and retention policies."
        ),
    )


def _parse_json_object(content: str) -> dict:
    cleaned = content.strip()
    if cleaned.startswith("```"):
        cleaned = cleaned.removeprefix("```json").removeprefix("```").strip()
        cleaned = cleaned.removesuffix("```").strip()
    parsed = json.loads(cleaned)
    if not isinstance(parsed, dict):
        raise ValueError("Model response was not a JSON object.")
    return parsed


def _build_user_content(image_data_url: str, location_name: str | None, notes: str | None) -> list[dict]:
    context_lines = [
        f"Location name: {location_name or 'Not provided'}",
        f"Notes: {notes or 'Not provided'}",
        JSON_INSTRUCTIONS,
    ]
    return [
        {"type": "text", "text": "\n\n".join(context_lines)},
        {
            "type": "image_url",
            "image_url": {
                "url": image_data_url,
                "detail": "low",
            },
        },
    ]


def analyze_garden_image(
    image_base64: str,
    location_name: str | None = None,
    notes: str | None = None,
) -> AgentResponse:
    if not image_base64 or not image_base64.strip():
        return _safe_fallback_response("No image was provided.")

    try:
        validate_base64_image(image_base64)
        image_data_url = image_to_data_url(image_base64)
    except ValueError as exc:
        return _safe_fallback_response(str(exc))

    load_dotenv()
    if not os.getenv("OPENAI_API_KEY"):
        return _safe_fallback_response("OpenAI API key is not configured.")

    try:
        client = OpenAI()
        response = client.chat.completions.create(
            model=os.getenv("OPENAI_MODEL", "gpt-4o-mini"),
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {
                    "role": "user",
                    "content": _build_user_content(image_data_url, location_name, notes),
                },
            ],
            temperature=0.1,
            response_format={"type": "json_object"},
            max_tokens=700,
        )
        content = response.choices[0].message.content or ""
        payload = _parse_json_object(content)

        observations = VisionObservation(**payload["observations"])
        notification = NotificationDecision(**payload["notification"])
        meeting_suggestion = MeetingSuggestion(**payload["meeting_suggestion"])

        return AgentResponse(
            summary=payload["summary"],
            observations=observations,
            notification=notification,
            phone_notification_result=_build_phone_notification(notification),
            meeting_suggestion=meeting_suggestion,
            employee_friendly_explanation=payload["employee_friendly_explanation"],
            limitations=payload["limitations"],
        )
    except Exception as exc:
        return _safe_fallback_response(f"OpenAI image analysis failed: {exc}")
