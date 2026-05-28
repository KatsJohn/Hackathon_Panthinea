from typing import Any


def _not_configured(channel: str, message: str, phone_label: str | None = None) -> dict[str, Any]:
    return {
        "channel": channel,
        "status": "not_configured",
        "sent": False,
        "message": message,
        "phone_label": phone_label,
        "detail": f"{channel} notifications are not configured for this hackathon demo.",
    }


def send_mock_notification(message: str) -> dict[str, Any]:
    return {
        "channel": "mock",
        "status": "sent",
        "sent": True,
        "message": message,
        "detail": "Simulated notification created for the in-app mock phone. No real message was sent.",
    }


def send_sms_notification_placeholder(message: str, phone_label: str) -> dict[str, Any]:
    return _not_configured("sms", message, phone_label)


def send_whatsapp_notification_placeholder(message: str, phone_label: str) -> dict[str, Any]:
    return _not_configured("whatsapp", message, phone_label)


def send_slack_notification_placeholder(message: str) -> dict[str, Any]:
    return _not_configured("slack", message)


def send_teams_notification_placeholder(message: str) -> dict[str, Any]:
    return _not_configured("teams", message)


# Production integrations could be added behind these placeholders using an SMS
# provider, the WhatsApp Business API, Slack, Microsoft Teams, or mobile push
# notifications. Keep provider API keys backend-only and out of version control.
# This demo must not require real phone numbers or send real messages by default.
