from typing import Literal

from pydantic import BaseModel, Field


RiskStatus = Literal["low", "medium", "high", "critical"]
ActionCategory = Literal["observe", "maintenance", "environment", "chemical", "hardware"]


class SensorReading(BaseModel):
    ph: float = Field(..., ge=0, le=14)
    conductivity: float = Field(..., description="Electrical conductivity in mS/cm")
    turbidity: float = Field(..., description="Turbidity in NTU")
    water_temperature: float = Field(..., description="Water temperature in Celsius")
    humidity: float = Field(..., ge=0, le=100, description="Relative humidity percentage")
    flow_rate: float = Field(..., ge=0, description="Irrigation flow rate in L/min")
    timestamp: str


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
    water_quality: RiskStatus
    root_zone_health: RiskStatus
    irrigation_flow_condition: RiskStatus
    environmental_comfort: RiskStatus
    plant_stress_level: RiskStatus
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
    sensors: SensorReading
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
