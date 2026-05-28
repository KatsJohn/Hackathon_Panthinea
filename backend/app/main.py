from datetime import UTC, datetime

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from .camera_source import analyze_image, get_demo_observation
from .calendar_planner import create_mock_calendar_event
from .demo_scenarios import get_demo_scenario, list_demo_scenarios
from .digital_twin import build_digital_twin
from .garden_agent import explain_garden_state
from .meeting_suggestion_engine import create_meeting_suggestion
from .models import (
    AgentResponse,
    EmployeeRecipient,
    ExplanationRequest,
    ImageAnalysisRequest,
    MeetingSuggestion,
    NotificationDecision,
    PhoneNotification,
    PhoneNotificationResult,
    SystemSnapshot,
    VirtualSceneEvent,
    VisionObservation,
)
from .mock_phone import clear_mock_phone_notifications, get_mock_phone_notifications, send_to_mock_phone
from .notification_engine import create_notification_decision, create_virtual_scene_event
from .risk_engine import calculate_risks, get_recommendations
from .stochastic_simulation import run_monte_carlo_forecast
from .vision_agent import analyze_garden_image


app = FastAPI(
    title="GardenSpace AI",
    description="Hackathon camera agent for an indoor workplace vertical tower garden.",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def build_snapshot() -> SystemSnapshot:
    observation = get_demo_observation()
    risks = calculate_risks(observation)
    digital_twin = build_digital_twin(observation, risks)
    forecast = run_monte_carlo_forecast(observation, risks)
    recommendations = get_recommendations(risks)
    return SystemSnapshot(
        observation=observation,
        risks=risks,
        digital_twin=digital_twin,
        forecast=forecast,
        recommendations=recommendations,
    )


MOCK_EMPLOYEE = EmployeeRecipient(
    employee_id="mock-garden-care-employee",
    display_name="Garden Care Employee",
    role="Facilities / Sustainability Team",
    phone_label="Employee phone",
)


def build_mock_phone_result(notification: NotificationDecision) -> PhoneNotificationResult:
    delivered = notification.should_notify
    phone_notification = PhoneNotification(
        notification_id=f"mock-phone-{datetime.now(UTC).strftime('%Y%m%d%H%M%S%f')}",
        recipient=MOCK_EMPLOYEE,
        title=notification.notification_title,
        message=notification.notification_message,
        urgency=notification.urgency,
        status="created",
        created_at=datetime.now(UTC).isoformat(),
    )
    if delivered:
        return send_to_mock_phone(phone_notification)
    return PhoneNotificationResult(
        notification=phone_notification,
        delivered_to_mock_phone=delivered,
        delivery_note="No simulated phone notification was sent because no employee action is needed right now.",
    )


@app.get("/")
def root() -> dict[str, str]:
    return {"project": "GardenSpace AI", "status": "ok"}


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok", "service": "GardenSpace AI backend"}


@app.get("/api/demo/scenarios")
def api_demo_scenarios() -> dict[str, list[str]]:
    return {"scenarios": list_demo_scenarios()}


@app.post("/api/demo/scenario/{scenario_name}", response_model=AgentResponse)
def api_demo_scenario(scenario_name: str) -> AgentResponse:
    try:
        scenario = get_demo_scenario(scenario_name)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=f"Unknown demo scenario: {scenario_name}") from exc
    agent_response = scenario["agent_response"]
    phone_notification_result = build_mock_phone_result(agent_response.notification)
    return agent_response.model_copy(update={"phone_notification_result": phone_notification_result})


@app.post("/api/vision/analyze", response_model=AgentResponse)
def api_vision_analyze(request: ImageAnalysisRequest) -> AgentResponse:
    agent_response = analyze_garden_image(
        request.image_base64,
        location_name=request.location_name,
        notes=request.notes,
    )
    notification = create_notification_decision(agent_response.observations)
    meeting_suggestion = create_meeting_suggestion(agent_response.observations)
    virtual_scene_event = create_virtual_scene_event(notification, meeting_suggestion)
    phone_notification_result = build_mock_phone_result(notification)
    return agent_response.model_copy(
        update={
            "notification": notification,
            "phone_notification_result": phone_notification_result,
            "meeting_suggestion": meeting_suggestion,
            "virtual_scene_event": virtual_scene_event,
        }
    )


@app.post("/api/notifications/preview", response_model=NotificationDecision)
def api_notifications_preview(observation: VisionObservation) -> NotificationDecision:
    return create_notification_decision(observation)


@app.post("/api/scene/preview", response_model=VirtualSceneEvent)
def api_scene_preview(notification_decision: NotificationDecision) -> VirtualSceneEvent:
    return create_virtual_scene_event(notification_decision)


@app.get("/api/mock-phone/notifications", response_model=list[PhoneNotification])
def api_mock_phone_notifications() -> list[PhoneNotification]:
    return get_mock_phone_notifications()


@app.post("/api/mock-phone/clear")
def api_mock_phone_clear() -> dict[str, str]:
    clear_mock_phone_notifications()
    return {"status": "cleared"}


@app.post("/api/calendar/mock-event")
def api_calendar_mock_event(meeting_suggestion: MeetingSuggestion) -> dict[str, str | int]:
    return create_mock_calendar_event(meeting_suggestion)


@app.get("/observation")
def observation():
    return get_demo_observation()


@app.post("/analyze-image")
def analyze_uploaded_image(request: ImageAnalysisRequest):
    current_observation = analyze_image(request)
    risks = calculate_risks(current_observation)
    digital_twin = build_digital_twin(current_observation, risks)
    forecast = run_monte_carlo_forecast(current_observation, risks)
    recommendations = get_recommendations(risks)
    return SystemSnapshot(
        observation=current_observation,
        risks=risks,
        digital_twin=digital_twin,
        forecast=forecast,
        recommendations=recommendations,
    )


@app.post("/explain-image")
async def explain_uploaded_image(request: ImageAnalysisRequest):
    current_observation = analyze_image(request)
    risk_scores = calculate_risks(current_observation)
    forecast_data = run_monte_carlo_forecast(current_observation, risk_scores)
    recommendations_data = get_recommendations(risk_scores)
    return await explain_garden_state(
        current_observation,
        risk_scores,
        forecast_data,
        recommendations_data,
        include_ai=True,
    )


@app.get("/risks")
def risks():
    current_observation = get_demo_observation()
    return calculate_risks(current_observation)


@app.get("/digital-twin")
def digital_twin():
    current_observation = get_demo_observation()
    risk_scores = calculate_risks(current_observation)
    return build_digital_twin(current_observation, risk_scores)


@app.get("/forecast")
def forecast():
    current_observation = get_demo_observation()
    risk_scores = calculate_risks(current_observation)
    return run_monte_carlo_forecast(current_observation, risk_scores)


@app.get("/recommendations")
def recommendations():
    current_observation = get_demo_observation()
    risk_scores = calculate_risks(current_observation)
    return get_recommendations(risk_scores)


@app.get("/snapshot")
def snapshot():
    return build_snapshot()


@app.post("/explain")
async def explain(request: ExplanationRequest | None = None):
    snapshot_data = build_snapshot()
    include_ai = True if request is None else request.include_ai
    return await explain_garden_state(
        snapshot_data.observation,
        snapshot_data.risks,
        snapshot_data.forecast,
        snapshot_data.recommendations,
        include_ai=include_ai,
    )
