from typing import TypedDict

from .models import (
    AgentResponse,
    EmployeeRecipient,
    MeetingSuggestion,
    NotificationDecision,
    PhoneNotification,
    PhoneNotificationResult,
    VisionObservation,
)


class DemoScenario(TypedDict):
    vision_observation: VisionObservation
    notification_decision: NotificationDecision
    phone_notification_result: PhoneNotificationResult
    meeting_suggestion: MeetingSuggestion
    agent_response: AgentResponse


MOCK_EMPLOYEE = EmployeeRecipient(
    employee_id="mock-garden-care-employee",
    display_name="Garden Care Employee",
    role="Facilities / Sustainability Team",
    phone_label="Employee phone",
)


def _phone_result(
    scenario_id: str,
    decision: NotificationDecision,
    created_at: str,
) -> PhoneNotificationResult:
    delivered = decision.should_notify
    return PhoneNotificationResult(
        notification=PhoneNotification(
            notification_id=f"mock-phone-{scenario_id}",
            recipient=MOCK_EMPLOYEE,
            title=decision.notification_title,
            message=decision.notification_message,
            urgency=decision.urgency,
            status="sent" if delivered else "created",
            created_at=created_at,
        ),
        delivered_to_mock_phone=delivered,
        delivery_note=(
            "Simulated phone notification delivered to the in-app mock phone."
            if delivered
            else "No simulated phone notification was sent because this scenario does not need employee attention right now."
        ),
    )


def _scenario(
    scenario_id: str,
    created_at: str,
    summary: str,
    observation: VisionObservation,
    notification: NotificationDecision,
    meeting_suggestion: MeetingSuggestion,
    employee_friendly_explanation: str,
) -> DemoScenario:
    phone_notification_result = _phone_result(scenario_id, notification, created_at)
    agent_response = AgentResponse(
        summary=summary,
        observations=observation,
        notification=notification,
        phone_notification_result=phone_notification_result,
        meeting_suggestion=meeting_suggestion,
        employee_friendly_explanation=employee_friendly_explanation,
        limitations=(
            "This is a simulated camera-based demo. The system does not identify people, analyze faces, "
            "track individuals, or claim certainty from images; it describes what appears visible and "
            "suggests a human check."
        ),
    )
    return {
        "vision_observation": observation,
        "notification_decision": notification,
        "phone_notification_result": phone_notification_result,
        "meeting_suggestion": meeting_suggestion,
        "agent_response": agent_response,
    }


DEMO_SCENARIOS: dict[str, DemoScenario] = {
    "healthy_garden": _scenario(
        scenario_id="healthy_garden",
        created_at="2026-05-28T09:00:00Z",
        summary="Plants appear healthy and the garden area appears clean.",
        observation=VisionObservation(
            plant_health_status="healthy",
            water_check_needed=False,
            area_status="free",
            visible_issues=[],
            confidence=0.9,
        ),
        notification=NotificationDecision(
            should_notify=False,
            urgency="low",
            notification_title="Garden looks good",
            notification_message=(
                "GardenSpace AI: The tower garden appears healthy and tidy. No action is needed right now."
            ),
            suggested_employee_action="No plant-care action needed right now.",
        ),
        meeting_suggestion=MeetingSuggestion(
            should_suggest_meeting=False,
            meeting_type="none",
            reason="The garden appears healthy, but this scenario is focused on plant status rather than scheduling.",
            suggested_duration_minutes=0,
        ),
        employee_friendly_explanation=(
            "The plants appear upright and green, and the surrounding tower garden area looks clean. "
            "GardenSpace AI is not creating a phone alert because there is no urgent employee action."
        ),
    ),
    "dry_plants": _scenario(
        scenario_id="dry_plants",
        created_at="2026-05-28T09:05:00Z",
        summary="Plants appear dry or drooping and may need water.",
        observation=VisionObservation(
            plant_health_status="possibly_dry",
            water_check_needed=True,
            area_status="free",
            visible_issues=[
                "Leaves appear dry or slightly drooping.",
                "The plants may need water or a reservoir check.",
            ],
            confidence=0.84,
        ),
        notification=NotificationDecision(
            should_notify=True,
            urgency="high",
            notification_title="Tower garden may need water",
            notification_message=(
                "GardenSpace AI: The tower garden plants appear dry or drooping. "
                "Please water the plants if appropriate, or check the reservoir when you can."
            ),
            suggested_employee_action="Water the plants if appropriate, or check the reservoir level.",
        ),
        meeting_suggestion=MeetingSuggestion(
            should_suggest_meeting=False,
            meeting_type="none",
            reason="Plant care attention should come before suggesting a wellbeing break near the garden.",
            suggested_duration_minutes=0,
        ),
        employee_friendly_explanation=(
            "Some leaves appear dry or less upright than expected. A human should water the plants if appropriate "
            "or check the reservoir; the system is not claiming that any watering has happened."
        ),
    ),
    "low_water_check": _scenario(
        scenario_id="low_water_check",
        created_at="2026-05-28T09:10:00Z",
        summary="The reservoir or watering area may need a human check.",
        observation=VisionObservation(
            plant_health_status="needs_attention",
            water_check_needed=True,
            area_status="free",
            visible_issues=[
                "The reservoir or watering area may need checking.",
                "Plant health appears acceptable but could decline without attention.",
            ],
            confidence=0.8,
        ),
        notification=NotificationDecision(
            should_notify=True,
            urgency="high",
            notification_title="Check the garden reservoir",
            notification_message=(
                "GardenSpace AI: The tower garden reservoir area may need attention. "
                "Please add water if needed, or inspect the reservoir today."
            ),
            suggested_employee_action="Inspect the reservoir and add water if needed.",
        ),
        meeting_suggestion=MeetingSuggestion(
            should_suggest_meeting=False,
            meeting_type="none",
            reason="The reservoir should be checked before promoting the garden as a meeting spot.",
            suggested_duration_minutes=0,
        ),
        employee_friendly_explanation=(
            "The plants do not appear critical, but the reservoir area suggests a check would be useful. "
            "A facilities teammate should inspect it and add water only if needed."
        ),
    ),
    "neglected_area": _scenario(
        scenario_id="neglected_area",
        created_at="2026-05-28T09:15:00Z",
        summary="The garden area appears messy or unattended.",
        observation=VisionObservation(
            plant_health_status="needs_attention",
            water_check_needed=False,
            area_status="cluttered",
            visible_issues=[
                "The area appears messy or unattended.",
                "The tower garden could use a manual tidy-up.",
            ],
            confidence=0.82,
        ),
        notification=NotificationDecision(
            should_notify=True,
            urgency="medium",
            notification_title="Garden area needs a quick tidy",
            notification_message=(
                "GardenSpace AI: The tower garden area appears messy or unattended. "
                "Please inspect and tidy the area when you have a moment."
            ),
            suggested_employee_action="Inspect and tidy the tower garden area.",
        ),
        meeting_suggestion=MeetingSuggestion(
            should_suggest_meeting=False,
            meeting_type="none",
            reason="The area should be tidied before suggesting it for a team check-in.",
            suggested_duration_minutes=0,
        ),
        employee_friendly_explanation=(
            "The tower garden area appears like it could use a human walkthrough and tidy-up. "
            "This is a request for inspection only, not a claim that maintenance has been completed."
        ),
    ),
    "meeting_friendly_space": _scenario(
        scenario_id="meeting_friendly_space",
        created_at="2026-05-28T09:20:00Z",
        summary="The garden area appears clean, calm, and available.",
        observation=VisionObservation(
            plant_health_status="healthy",
            water_check_needed=False,
            area_status="free",
            visible_issues=[],
            confidence=0.88,
        ),
        notification=NotificationDecision(
            should_notify=True,
            urgency="low",
            notification_title="Garden space is available",
            notification_message=(
                "GardenSpace AI: The garden area looks clean, calm, and available. "
                "It could be a good spot for a short wellbeing break or team check-in."
            ),
            suggested_employee_action="Consider a short wellbeing break or team check-in near the garden.",
        ),
        meeting_suggestion=MeetingSuggestion(
            should_suggest_meeting=True,
            meeting_type="wellbeing_break",
            reason="The garden appears clean, calm, and available, with no urgent plant-care issue visible.",
            suggested_duration_minutes=10,
        ),
        employee_friendly_explanation=(
            "The tower garden appears healthy and the space looks available. "
            "A short wellbeing break or lightweight team check-in near the garden may be appropriate."
        ),
    ),
    "occupied_space": _scenario(
        scenario_id="occupied_space",
        created_at="2026-05-28T09:25:00Z",
        summary="The garden area appears occupied and no urgent plant-care issue is visible.",
        observation=VisionObservation(
            plant_health_status="healthy",
            water_check_needed=False,
            area_status="occupied",
            visible_issues=["The area appears occupied."],
            confidence=0.76,
        ),
        notification=NotificationDecision(
            should_notify=False,
            urgency="low",
            notification_title="Garden area currently occupied",
            notification_message=(
                "GardenSpace AI: The garden area appears occupied, so it is not a good meeting spot right now. "
                "No urgent plant-care action is visible."
            ),
            suggested_employee_action="No urgent plant-care action needed; avoid suggesting a meeting there right now.",
        ),
        meeting_suggestion=MeetingSuggestion(
            should_suggest_meeting=False,
            meeting_type="none",
            reason="The garden area appears occupied, so the app should not suggest a meeting there right now.",
            suggested_duration_minutes=0,
        ),
        employee_friendly_explanation=(
            "The scene suggests the garden area is currently occupied. The app does not identify anyone "
            "or infer personal attributes, and it should not suggest a meeting there right now."
        ),
    ),
}


def list_demo_scenarios() -> list[str]:
    return list(DEMO_SCENARIOS)


def get_demo_scenarios() -> dict[str, DemoScenario]:
    return DEMO_SCENARIOS


def get_demo_scenario(scenario_id: str) -> DemoScenario:
    return DEMO_SCENARIOS[scenario_id]
