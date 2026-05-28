from .models import DigitalTwinState, RiskScore, SensorReading


def _max_status(risks: list[RiskScore], risk_ids: set[str]) -> str:
    selected = [risk for risk in risks if risk.id in risk_ids]
    if not selected:
        return "low"
    return max(selected, key=lambda risk: risk.score).status


def build_digital_twin(reading: SensorReading, risks: list[RiskScore]) -> DigitalTwinState:
    highest = max(risks, key=lambda risk: risk.score)
    trend = "stable"
    if highest.score >= 70:
        trend = f"watch {highest.label.lower()} closely over the next cycle"
    elif reading.flow_rate < 1.0 or reading.humidity > 75:
        trend = "conditions may worsen without operator attention"

    return DigitalTwinState(
        water_quality=_max_status(risks, {"nutrient_imbalance", "algae_formation"}),
        root_zone_health=_max_status(risks, {"root_disease", "mold_fungal"}),
        irrigation_flow_condition=_max_status(risks, {"clogged_irrigation", "dehydration_stress"}),
        environmental_comfort=_max_status(risks, {"dehydration_stress", "mold_fungal"}),
        plant_stress_level=highest.status,
        predicted_near_future_trend=trend,
        summary=(
            f"The tower is currently {highest.status} for {highest.label.lower()} "
            f"with pH {reading.ph}, conductivity {reading.conductivity} mS/cm, "
            f"and flow {reading.flow_rate} L/min."
        ),
    )
