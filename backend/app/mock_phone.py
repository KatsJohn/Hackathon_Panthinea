from .models import PhoneNotification, PhoneNotificationResult


_MOCK_PHONE_NOTIFICATIONS: list[PhoneNotification] = []


def send_to_mock_phone(phone_notification: PhoneNotification) -> PhoneNotificationResult:
    sent_notification = phone_notification.model_copy(update={"status": "sent"})
    _MOCK_PHONE_NOTIFICATIONS.append(sent_notification)
    return PhoneNotificationResult(
        notification=sent_notification,
        delivered_to_mock_phone=True,
        delivery_note="Simulated delivery to the in-app employee phone. No real SMS was sent.",
    )


def get_mock_phone_notifications() -> list[PhoneNotification]:
    return list(_MOCK_PHONE_NOTIFICATIONS)


def clear_mock_phone_notifications():
    _MOCK_PHONE_NOTIFICATIONS.clear()
