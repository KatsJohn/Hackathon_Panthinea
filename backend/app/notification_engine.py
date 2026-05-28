from .models import MeetingSuggestion, NotificationDecision, VirtualSceneEvent, VisionObservation


CARE_ATTENTION_STATUSES = {"possibly_dry", "possibly_wilted", "needs_attention"}
WATER_WORDS = {"water", "reservoir"}
MEETING_WORDS = {"meeting", "wellbeing", "break", "check-in", "check in"}


def _has_visible_issue(observation: VisionObservation, *keywords: str) -> bool:
    issue_text = " ".join(observation.visible_issues).lower()
    return any(keyword in issue_text for keyword in keywords)


def create_notification_decision(observation: VisionObservation) -> NotificationDecision:
    needs_plant_care = observation.plant_health_status in CARE_ATTENTION_STATUSES
    meeting_friendly = (
        observation.plant_health_status == "healthy"
        and not observation.water_check_needed
        and observation.area_status == "free"
        and not observation.visible_issues
    )
    cluttered_area = observation.area_status == "cluttered" or _has_visible_issue(
        observation,
        "messy",
        "cluttered",
        "neglected",
        "unattended",
        "tidy",
    )
    should_notify = needs_plant_care or observation.water_check_needed or meeting_friendly or cluttered_area

    if observation.water_check_needed:
        title = "Check the garden water"
        message = (
            "GardenSpace AI: The tower garden may need a water or reservoir check. "
            "Please inspect the reservoir and add water if needed."
        )
        action = "Inspect the reservoir and add water if needed."
    elif observation.plant_health_status == "possibly_dry":
        title = "Plants may need water"
        message = (
            "GardenSpace AI: The plants appear possibly dry. "
            "Please water the plants if appropriate or check the reservoir."
        )
        action = "Water the plants if appropriate or check the reservoir."
    elif observation.plant_health_status == "possibly_wilted":
        title = "Plants may need attention"
        message = (
            "GardenSpace AI: The plants appear possibly wilted. "
            "Please inspect the tower garden when you can."
        )
        action = "Inspect the tower garden plants."
    elif observation.plant_health_status == "needs_attention":
        title = "Garden needs attention"
        message = (
            "GardenSpace AI: The tower garden appears to need attention. "
            "Please inspect the plants and visible garden area."
        )
        action = "Inspect the plants and garden area."
    elif cluttered_area:
        title = "Garden area could use a tidy"
        message = (
            "GardenSpace AI: The tower garden area appears cluttered or unattended. "
            "Please inspect and tidy the area when you can."
        )
        action = "Inspect and tidy the tower garden area."
    elif meeting_friendly:
        title = "Garden space looks available"
        message = (
            "GardenSpace AI: The garden appears calm and available. "
            "It may be a nice spot for a short wellbeing break or team check-in."
        )
        action = "Consider a short wellbeing break or team check-in near the garden."
    else:
        title = "Garden check complete"
        message = (
            "GardenSpace AI: No urgent plant-care action appears needed right now."
        )
        action = "No immediate action needed."

    urgency = "low"
    if should_notify and not meeting_friendly:
        urgency = "medium"
    if observation.water_check_needed and observation.plant_health_status in {"possibly_dry", "needs_attention"}:
        urgency = "high"
    if _has_visible_issue(observation, "neglected", "urgent", "very dry", "severely dry"):
        urgency = "high"

    return NotificationDecision(
        should_notify=should_notify,
        urgency=urgency,
        notification_title=title,
        notification_message=message,
        suggested_employee_action=action,
    )


def _contains_any(value: str, words: set[str]) -> bool:
    lowered = value.lower()
    return any(word in lowered for word in words)


def create_virtual_scene_event(
    notification_decision: NotificationDecision,
    meeting_suggestion: MeetingSuggestion | None = None,
) -> VirtualSceneEvent:
    if not notification_decision.should_notify:
        return VirtualSceneEvent(
            phone_message_visible=False,
            phone_title="",
            phone_message="",
            animation_state="idle",
            next_visual_action="none",
            event_note="No simulated phone message is visible because no notification is needed.",
        )

    action_text = notification_decision.suggested_employee_action
    message_text = f"{notification_decision.notification_title} {notification_decision.notification_message} {action_text}"
    meeting_requested = bool(meeting_suggestion and meeting_suggestion.should_suggest_meeting) or _contains_any(
        message_text,
        MEETING_WORDS,
    )
    water_requested = _contains_any(message_text, WATER_WORDS)

    animation_state = "idle"
    if notification_decision.urgency in {"medium", "high"}:
        animation_state = "reading_phone"
    if meeting_requested:
        animation_state = "meeting"

    next_visual_action = "none"
    if water_requested:
        next_visual_action = "check_reservoir" if "reservoir" in message_text.lower() else "walk_to_garden"
    elif "tidy" in message_text.lower() or "clean" in message_text.lower():
        next_visual_action = "tidy_garden"
    elif meeting_requested:
        next_visual_action = "start_meeting"
    elif notification_decision.should_notify:
        next_visual_action = "walk_to_garden"

    return VirtualSceneEvent(
        phone_message_visible=True,
        phone_title=notification_decision.notification_title,
        phone_message=notification_decision.notification_message,
        animation_state=animation_state,
        next_visual_action=next_visual_action,
        event_note="Simulated virtual scene event only; no real phone notification was sent.",
    )
