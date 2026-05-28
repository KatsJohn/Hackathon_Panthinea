from typing import Literal

from pydantic import BaseModel, Field


RiskStatus = Literal["low", "medium", "high", "critical"]
PlantCondition = Literal["healthy", "dry", "wilted", "crowded", "neglected"]
ActionCategory = Literal["observe", "maintenance", "reservoir", "notification", "workplace"]
PlantHealthStatus = Literal["healthy", "possibly_dry", "possibly_wilted", "needs_attention", "unknown"]
AreaStatus = Literal["free", "occupied", "cluttered", "unknown"]
UrgencyLevel = Literal["low", "medium", "high"]
NotificationChannel = Literal["mock_phone"]
NotificationStatus = Literal["created", "sent", "failed"]


class CameraObservation(BaseModel):
    source: Literal["demo", "upload", "webcam"]
    image_name: str
    detected_conditions: list[PlantCondition]
    plant_health_index: int = Field(..., ge=0, le=100)
    dryness_score: int = Field(..., ge=0, le=100)
    wilt_score: int = Field(..., ge=0, le=100)
    crowding_score: int = Field(..., ge=0, le=100)
    neglect_score: int = Field(..., ge=0, le=100)
    reservoir_check_score: int = Field(..., ge=0, le=100)
    confidence: float = Field(..., ge=0, le=1)
    timestamp: str


class ImageAnalysisRequest(BaseModel):
    image_base64: str
    location_name: str | None = None
    notes: str | None = None


class VisionObservation(BaseModel):
    plant_health_status: PlantHealthStatus
    water_check_needed: bool
    area_status: AreaStatus
    visible_issues: list[str]
    confidence: float = Field(..., ge=0, le=1)


class NotificationDecision(BaseModel):
    should_notify: bool
    urgency: UrgencyLevel
    notification_title: str
    notification_message: str
    suggested_employee_action: str


class EmployeeRecipient(BaseModel):
    employee_id: str
    display_name: str
    role: str
    phone_label: str = "Employee phone"


class PhoneNotification(BaseModel):
    notification_id: str
    recipient: EmployeeRecipient
    title: str
    message: str
    urgency: UrgencyLevel
    channel: NotificationChannel = "mock_phone"
    status: NotificationStatus = "created"
    created_at: str


class PhoneNotificationResult(BaseModel):
    notification: PhoneNotification
    delivered_to_mock_phone: bool
    delivery_note: str


class MeetingSuggestion(BaseModel):
    should_suggest_meeting: bool
    meeting_type: str
    reason: str
    suggested_duration_minutes: int


class AgentResponse(BaseModel):
    summary: str
    observations: VisionObservation
    notification: NotificationDecision
    phone_notification_result: PhoneNotificationResult
    meeting_suggestion: MeetingSuggestion
    employee_friendly_explanation: str
    limitations: str


class ApprovedAction(BaseModel):
    id: str
    label: str
    category: ActionCategory
    requires_human_approval: bool = False
    rationale: str


class RiskScore(BaseModel):
    id: str
    label: str
    score: int = Field(..., ge=0, le=100)
    status: RiskStatus
    contributing_factors: list[str]
    recommended_action_ids: list[str]
    requires_human_approval: bool = False


class DigitalTwinState(BaseModel):
    workplace_area_condition: RiskStatus
    plant_appearance: RiskStatus
    reservoir_attention: RiskStatus
    team_engagement: RiskStatus
    maintenance_urgency: RiskStatus
    predicted_near_future_trend: str
    summary: str


class ForecastBand(BaseModel):
    risk_id: str
    label: str
    current_score: int = Field(..., ge=0, le=100)
    expected_score: int = Field(..., ge=0, le=100)
    p90_score: int = Field(..., ge=0, le=100)
    probability_high_or_critical: float = Field(..., ge=0, le=1)


class ForecastResponse(BaseModel):
    horizon_hours: int
    runs: int
    note: str
    bands: list[ForecastBand]


class SystemSnapshot(BaseModel):
    observation: CameraObservation
    risks: list[RiskScore]
    digital_twin: DigitalTwinState
    forecast: ForecastResponse
    recommendations: list[ApprovedAction]


class ExplanationRequest(BaseModel):
    include_ai: bool = True


class ExplanationResponse(BaseModel):
    explanation: str
    approved_action_ids: list[str]
    used_ai: bool
