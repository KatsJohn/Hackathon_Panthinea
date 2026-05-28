from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .camera_source import analyze_image, get_demo_observation
from .digital_twin import build_digital_twin
from .garden_agent import explain_garden_state
from .models import ExplanationRequest, ImageAnalysisRequest, SystemSnapshot
from .risk_engine import calculate_risks, get_recommendations
from .stochastic_simulation import run_monte_carlo_forecast


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


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok", "service": "GardenSpace AI backend"}


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
