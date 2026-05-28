from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .digital_twin import build_digital_twin
from .garden_agent import explain_garden_state
from .models import ExplanationRequest, SystemSnapshot
from .risk_engine import calculate_risks, get_recommendations
from .sensor_source import get_sensor_reading
from .stochastic_simulation import run_monte_carlo_forecast


app = FastAPI(
    title="GardenMind AI",
    description="Hackathon copilot for an autonomous indoor vertical tower garden.",
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
    sensors = get_sensor_reading()
    risks = calculate_risks(sensors)
    digital_twin = build_digital_twin(sensors, risks)
    forecast = run_monte_carlo_forecast(sensors, risks)
    recommendations = get_recommendations(risks)
    return SystemSnapshot(
        sensors=sensors,
        risks=risks,
        digital_twin=digital_twin,
        forecast=forecast,
        recommendations=recommendations,
    )


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok", "service": "GardenMind AI backend"}


@app.get("/sensors")
def sensors():
    return get_sensor_reading()


@app.get("/risks")
def risks():
    reading = get_sensor_reading()
    return calculate_risks(reading)


@app.get("/digital-twin")
def digital_twin():
    reading = get_sensor_reading()
    risk_scores = calculate_risks(reading)
    return build_digital_twin(reading, risk_scores)


@app.get("/forecast")
def forecast():
    reading = get_sensor_reading()
    risk_scores = calculate_risks(reading)
    return run_monte_carlo_forecast(reading, risk_scores)


@app.get("/recommendations")
def recommendations():
    reading = get_sensor_reading()
    risk_scores = calculate_risks(reading)
    return get_recommendations(risk_scores)


@app.get("/snapshot")
def snapshot():
    return build_snapshot()


@app.post("/explain")
async def explain(request: ExplanationRequest | None = None):
    snapshot_data = build_snapshot()
    include_ai = True if request is None else request.include_ai
    return await explain_garden_state(
        snapshot_data.sensors,
        snapshot_data.risks,
        snapshot_data.forecast,
        snapshot_data.recommendations,
        include_ai=include_ai,
    )
