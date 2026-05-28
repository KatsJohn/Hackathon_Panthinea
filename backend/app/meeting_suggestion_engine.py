from .models import MeetingSuggestion, VisionObservation


MEETING_TYPES = [
    "10-minute team check-in",
    "wellbeing break",
    "stand-up meeting near the garden",
    "sustainability reflection session",
]


def create_meeting_suggestion(observation: VisionObservation) -> MeetingSuggestion:
    can_suggest = observation.area_status == "free" and observation.plant_health_status in {"healthy", "unknown"}

    if not can_suggest:
        reason = "The garden area does not appear suitable for a meeting right now."
        if observation.area_status == "occupied":
            reason = "The garden area appears occupied, so it should not be suggested for a meeting right now."
        elif observation.area_status == "cluttered":
            reason = "The garden area appears cluttered, so it should be tidied before suggesting a meeting."
        elif observation.plant_health_status not in {"healthy", "unknown"}:
            reason = "The plants may need care first, so a meeting suggestion should wait."

        return MeetingSuggestion(
            should_suggest_meeting=False,
            meeting_type="none",
            reason=reason,
            suggested_duration_minutes=0,
        )

    if observation.plant_health_status == "unknown":
        meeting_type = "wellbeing break"
        reason = (
            "The garden area appears free, and no clear plant-care issue is visible. "
            "A short wellbeing break may be appropriate."
        )
    else:
        meeting_type = MEETING_TYPES[0]
        reason = (
            "The garden area appears free and the plants appear healthy, "
            "so it could be a friendly spot for a short team check-in."
        )

    return MeetingSuggestion(
        should_suggest_meeting=True,
        meeting_type=meeting_type,
        reason=reason,
        suggested_duration_minutes=10,
    )
