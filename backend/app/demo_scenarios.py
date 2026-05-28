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

SCENARIO_CREATED_AT = "2026-05-28T09:00:00Z"


def _phone_notification_result(
    scenario_id: str,
    notification: NotificationDecision,
) -> PhoneNotificationResult:
    delivered = notification.should_notify
    phone_notification = PhoneNotification(
        notification_id=f"mock-phone-{scenario_id}",
        recipient=MOCK_EMPLOYEE,
        title=notification.notification_title,
        message=notification.notification_message,
        urgency=notification.urgency,
        status="sent" if delivered else "created",
        created_at=SCENARIO_CREATED_AT,
    )
    delivery_note = (
        "Simulated phone notification delivered to the in-app mock phone."
        if delivered
        else "No simulated phone notification was sent because the scenario does not need employee attention right now."
    )
    return PhoneNotificationResult(
        notification=phone_notification,
        delivered_to_mock_phone=delivered,
        delivery_note=delivery_note,
    )


def _scenario(
    scenario_id: str,
    summary: str,
    observation: VisionObservation,
    notification: NotificationDecision,
    meeting_suggestion: MeetingSuggestion,
    employee_friendly_explanation: str,
) -> AgentResponse:
    return AgentResponse(
        summary=summary,
        observations=observation,
        notification=notification,
        phone_notification_result=_phone_notification_result(scenario_id, notification),
        meeting_suggestion=meeting_suggestion,
        employee_friendly_explanation=employee_friendly_explanation,
        limitations=(
            "This is a simulated camera-based demo. The system does not identify people, analyze faces, "
            "or claim certainty from images; it describes what appears visible and suggests a human check."
        ),
    )


DEMO_SCENARIOS: dict[str, AgentResponse] = {
    "healthy_garden": _scenario(
        scenario_id="healthy_garden",
        summary="Plants appear healthy and the garden area appears clean.",
        observation=VisionObservation(
            plant_health_status="healthy",
            water_check_needed=False,
            area_status="free",
            visible_issues=[],
            confidence=0.86,
        ),
        notification=NotificationDecision(
            should_notify=False,
            urgency="low",
            notification_title="Garden looks good",
            notification_message="GardenSpace AI: The tower garden appears healthy and tidy. No action is needed right now.",
            suggested_employee_action="No plant-care action needed right now.",
        ),
        meeting_suggestion=MeetingSuggestion(
            should_suggest_meeting=False,
            meeting_type="none",
            reason="The space appears clean, but this scenario is focused on plant health rather than a meeting prompt.",
            suggested_duration_minutes=0,
        ),
        employee_friendly_explanation=(
            "The plants appear upright and green, and the surrounding area looks clean. "
            "Nothing suggests urgent plant care in this demo view."
        ),
    ),
    "dry_plants": _scenario(
        scenario_id="dry_plants",
        summary="Plants appear dry or drooping and may need water.",
        observation=VisionObservation(
            plant_health_status="possibly_dry",
            water_check_needed=True,
            area_status="free",
            visible_issues=["Leaves appear dry", "Some plants appear drooping"],
            confidence=0.81,
        ),
        notification=NotificationDecision(
            should_notify=True,
            urgency="high",
            notification_title="Tower garden may need water",
            notification_message=(
                "GardenSpace AI: The plants appear dry or drooping. Please water the plants or check the reservoir when you can."
            ),
            suggested_employee_action="Water the plants or check the reservoir level.",
        ),
        meeting_suggestion=MeetingSuggestion(
            should_suggest_meeting=False,
            meeting_type="none",
            reason="Plant care appears more important than using the space for a meeting right now.",
            suggested_duration_minutes=0,
        ),
        employee_friendly_explanation=(
            "The leaves appear a bit dry and some growth looks droopy. "
            "This suggests the plants may need water or a quick reservoir check."
        ),
    ),
    "low_water_check": _scenario(
        scenario_id="low_water_check",
        summary="The reservoir or watering area may need checking.",
        observation=VisionObservation(
            plant_health_status="needs_attention",
            water_check_needed=True,
            area_status="free",
            visible_issues=["Reservoir area may need checking", "Watering area appears low or unclear"],
            confidence=0.78,
        ),
        notification=NotificationDecision(
            should_notify=True,
            urgency="high",
            notification_title="Check the garden reservoir",
            notification_message=(
                "GardenSpace AI: The reservoir area may need attention. Please add water or inspect the reservoir today."
            ),
            suggested_employee_action="Add water if needed or inspect the reservoir area.",
        ),
        meeting_suggestion=MeetingSuggestion(
            should_suggest_meeting=False,
            meeting_type="none",
            reason="The watering area appears to need a human check before the space is promoted for a wellbeing break.",
            suggested_duration_minutes=0,
        ),
        employee_friendly_explanation=(
            "The visible watering area suggests the reservoir may need attention. "
            "A human check can confirm whether water should be added."
        ),
    ),
    "neglected_area": _scenario(
        scenario_id="neglected_area",
        summary="The garden area appears messy or unattended.",
        observation=VisionObservation(
            plant_health_status="needs_attention",
            water_check_needed=False,
            area_status="cluttered",
            visible_issues=["Area appears cluttered", "Tower garden may need tidying"],
            confidence=0.8,
        ),
        notification=NotificationDecision(
            should_notify=True,
            urgency="medium",
            notification_title="Garden area could use a tidy-up",
            notification_message=(
                "GardenSpace AI: The tower garden area appears messy or unattended. Please inspect and tidy the area when possible."
            ),
            suggested_employee_action="Inspect and tidy the tower garden area.",
        ),
        meeting_suggestion=MeetingSuggestion(
            should_suggest_meeting=False,
            meeting_type="none",
            reason="The area appears cluttered, so it is not a good moment to suggest a meeting there.",
            suggested_duration_minutes=0,
        ),
        employee_friendly_explanation=(
            "The surrounding space appears cluttered or unattended. "
            "A quick tidy-up would make the garden easier to enjoy and maintain."
        ),
    ),
    "meeting_friendly_space": _scenario(
        scenario_id="meeting_friendly_space",
        summary="The garden area appears clean, calm, and available.",
        observation=VisionObservation(
            plant_health_status="healthy",
            water_check_needed=False,
            area_status="free",
            visible_issues=[],
            confidence=0.84,
        ),
        notification=NotificationDecision(
            should_notify=True,
            urgency="low",
            notification_title="Garden space is available",
            notification_message=(
                "GardenSpace AI: The garden area appears clean and calm. It could be a nice spot for a 10-minute wellbeing break or team check-in."
            ),
            suggested_employee_action="Consider a short wellbeing break or team check-in near the garden.",
        ),
        meeting_suggestion=MeetingSuggestion(
            should_suggest_meeting=True,
            meeting_type="wellbeing break or team check-in",
            reason="The garden area appears clean, calm, and available.",
            suggested_duration_minutes=10,
        ),
        employee_friendly_explanation=(
            "The tower garden appears healthy and the surrounding space looks available. "
            "This may be a good moment for a short break or informal team check-in."
        ),
    ),
    "occupied_space": _scenario(
        scenario_id="occupied_space",
        summary="The garden area appears occupied, so a meeting should not be suggested right now.",
        observation=VisionObservation(
            plant_health_status="healthy",
            water_check_needed=False,
            area_status="occupied",
            visible_issues=["The area appears occupied"],
            confidence=0.76,
        ),
        notification=NotificationDecision(
            should_notify=False,
            urgency="low",
            notification_title="Garden area appears occupied",
            notification_message=(
                "GardenSpace AI: The garden area appears occupied. No plant-care action is needed right now."
            ),
            suggested_employee_action="No urgent action needed; check again later if you want to use the space.",
        ),
        meeting_suggestion=MeetingSuggestion(
            should_suggest_meeting=False,
            meeting_type="none",
            reason="The area appears occupied, so the agent should not suggest a meeting there right now.",
            suggested_duration_minutes=0,
        ),
        employee_friendly_explanation=(
            "The plants appear healthy, but the area appears occupied. "
            "The system does not identify anyone; it only notes that the space may not be available."
        ),
    ),
}


def list_demo_scenarios() -> list[str]:
    return list(DEMO_SCENARIOS)


def get_demo_scenario(scenario_id: str) -> AgentResponse:
    return DEMO_SCENARIOS[scenario_id]
