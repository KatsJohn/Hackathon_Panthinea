from .models import MeetingSuggestion


def suggest_meeting_time() -> str:
    return "Next available 10-minute workplace break window"


def create_mock_calendar_event(meeting_suggestion: MeetingSuggestion) -> dict[str, str | int]:
    """Create a simulated calendar event without contacting any real calendar provider."""
    if not meeting_suggestion.should_suggest_meeting:
        return {
            "title": "No meeting suggested right now",
            "suggested_duration_minutes": 0,
            "location": "Near the tower garden",
            "reason": meeting_suggestion.reason,
            "suggested_time": suggest_meeting_time(),
        }

    return {
        "title": meeting_suggestion.meeting_type,
        "suggested_duration_minutes": meeting_suggestion.suggested_duration_minutes,
        "location": "Near the tower garden",
        "reason": meeting_suggestion.reason,
        "suggested_time": suggest_meeting_time(),
    }
