from .models import CameraObservation, DigitalTwinState, RiskScore


def _max_status(risks: list[RiskScore], risk_ids: set[str]) -> str:
    selected = [risk for risk in risks if risk.id in risk_ids]
    if not selected:
        return "low"
    return max(selected, key=lambda risk: risk.score).status


def build_digital_twin(observation: CameraObservation, risks: list[RiskScore]) -> DigitalTwinState:
    highest = max(risks, key=lambda risk: risk.score)
    trend = "stable"
    if highest.score >= 70:
        trend = f"watch {highest.label.lower()} closely over the next cycle"
    elif observation.reservoir_check_score > 60 or observation.neglect_score > 55:
        trend = "conditions may look worse without employee attention"

    return DigitalTwinState(
        workplace_area_condition=_max_status(risks, {"neglected_area", "crowded_growth"}),
        plant_appearance=_max_status(risks, {"dry_appearance", "wilted_appearance", "crowded_growth"}),
        reservoir_attention=_max_status(risks, {"reservoir_attention"}),
        team_engagement=_max_status(risks, {"workplace_engagement"}),
        maintenance_urgency=highest.status,
        predicted_near_future_trend=trend,
        summary=(
            f"The tower camera view is currently {highest.status} for {highest.label.lower()} "
            f"with a plant health index of {observation.plant_health_index}/100."
        ),
    )
