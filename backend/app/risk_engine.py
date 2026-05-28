from .models import ApprovedAction, RiskScore, SensorReading


APPROVED_ACTIONS: dict[str, ApprovedAction] = {
    "inspect_roots": ApprovedAction(
        id="inspect_roots",
        label="Inspect visible root zone",
        category="maintenance",
        rationale="A visual check can confirm discoloration, slime, or blocked root mats without changing hardware state.",
    ),
    "flush_lines": ApprovedAction(
        id="flush_lines",
        label="Flush irrigation lines with clean water",
        category="maintenance",
        rationale="A supervised flush can clear early blockage symptoms without chemical intervention.",
    ),
    "clean_reservoir": ApprovedAction(
        id="clean_reservoir",
        label="Clean reservoir and remove biofilm",
        category="maintenance",
        rationale="Manual cleaning reduces algae and pathogen pressure.",
    ),
    "increase_airflow": ApprovedAction(
        id="increase_airflow",
        label="Increase airflow around tower",
        category="environment",
        rationale="Improved ventilation reduces mold and fungal pressure.",
    ),
    "check_pump": ApprovedAction(
        id="check_pump",
        label="Check pump and filter assembly",
        category="hardware",
        requires_human_approval=True,
        rationale="Hardware inspection should be confirmed by an operator before any actuation.",
    ),
    "adjust_nutrients_human_approval": ApprovedAction(
        id="adjust_nutrients_human_approval",
        label="Adjust nutrient concentration after human approval",
        category="chemical",
        requires_human_approval=True,
        rationale="Nutrient dosing changes chemistry and must be approved by a person.",
    ),
    "correct_ph_human_approval": ApprovedAction(
        id="correct_ph_human_approval",
        label="Correct pH after human approval",
        category="chemical",
        requires_human_approval=True,
        rationale="pH correction is chemical dosing and must be approved by a person.",
    ),
    "top_up_water": ApprovedAction(
        id="top_up_water",
        label="Top up reservoir with clean water",
        category="maintenance",
        rationale="Adding clean water can reduce dehydration stress and stabilize circulation.",
    ),
}


def _clamp(value: float, low: int = 0, high: int = 100) -> int:
    return max(low, min(high, round(value)))


def _status(score: int) -> str:
    if score >= 80:
        return "critical"
    if score >= 60:
        return "high"
    if score >= 35:
        return "medium"
    return "low"


def _outside_range_score(value: float, low: float, high: float, scale: float) -> float:
    if value < low:
        return (low - value) * scale
    if value > high:
        return (value - high) * scale
    return 0


def _risk(
    risk_id: str,
    label: str,
    score: float,
    factors: list[str],
    action_ids: list[str],
) -> RiskScore:
    final_score = _clamp(score)
    actions = [APPROVED_ACTIONS[action_id] for action_id in action_ids]
    return RiskScore(
        id=risk_id,
        label=label,
        score=final_score,
        status=_status(final_score),
        contributing_factors=factors or ["All monitored values are near the demo target range."],
        recommended_action_ids=action_ids,
        requires_human_approval=any(action.requires_human_approval for action in actions),
    )


def calculate_risks(reading: SensorReading) -> list[RiskScore]:
    """Calculate deterministic heuristic risks from the current sensor reading."""
    nutrient_factors = []
    nutrient_score = 10
    if reading.conductivity < 1.6:
        nutrient_score += (1.6 - reading.conductivity) * 38
        nutrient_factors.append("Conductivity is below the target nutrient range.")
    if reading.conductivity > 2.4:
        nutrient_score += (reading.conductivity - 2.4) * 42
        nutrient_factors.append("Conductivity is above the target nutrient range.")
    ph_pressure = _outside_range_score(reading.ph, 5.9, 6.7, 28)
    if ph_pressure:
        nutrient_score += ph_pressure
        nutrient_factors.append("pH is outside the preferred hydroponic uptake range.")

    root_factors = []
    root_score = 12
    if reading.water_temperature > 22.5:
        root_score += (reading.water_temperature - 22.5) * 8
        root_factors.append("Warm water can reduce oxygen availability in the root zone.")
    if reading.turbidity > 20:
        root_score += (reading.turbidity - 20) * 1.6
        root_factors.append("Elevated turbidity can indicate suspended organic matter.")
    if reading.flow_rate < 0.9:
        root_score += (0.9 - reading.flow_rate) * 25
        root_factors.append("Low flow can create stagnant root-zone pockets.")

    algae_factors = []
    algae_score = 8
    if reading.turbidity > 18:
        algae_score += (reading.turbidity - 18) * 2
        algae_factors.append("Turbidity is elevated.")
    if reading.water_temperature > 21:
        algae_score += (reading.water_temperature - 21) * 7
        algae_factors.append("Warm water increases algae growth pressure.")

    clog_factors = []
    clog_score = 8
    if reading.flow_rate < 1.0:
        clog_score += (1.0 - reading.flow_rate) * 60
        clog_factors.append("Flow rate is below normal circulation range.")
    if reading.turbidity > 25:
        clog_score += (reading.turbidity - 25) * 1.5
        clog_factors.append("Suspended solids may build up in emitters or filters.")

    dehydration_factors = []
    dehydration_score = 10
    if reading.humidity < 50:
        dehydration_score += (50 - reading.humidity) * 2.2
        dehydration_factors.append("Ambient humidity is low.")
    if reading.flow_rate < 1.1:
        dehydration_score += (1.1 - reading.flow_rate) * 45
        dehydration_factors.append("Irrigation flow is reduced.")
    if reading.water_temperature > 24:
        dehydration_score += (reading.water_temperature - 24) * 6
        dehydration_factors.append("Warm water can increase plant stress.")

    mold_factors = []
    mold_score = 10
    if reading.humidity > 72:
        mold_score += (reading.humidity - 72) * 2.5
        mold_factors.append("High humidity favors fungal pressure.")
    if reading.flow_rate < 0.9:
        mold_score += (0.9 - reading.flow_rate) * 18
        mold_factors.append("Low flow can leave wet stagnant zones.")

    return [
        _risk(
            "nutrient_imbalance",
            "Nutrient imbalance",
            nutrient_score,
            nutrient_factors,
            ["adjust_nutrients_human_approval", "correct_ph_human_approval"],
        ),
        _risk("root_disease", "Root disease risk", root_score, root_factors, ["inspect_roots", "clean_reservoir"]),
        _risk("algae_formation", "Algae formation", algae_score, algae_factors, ["clean_reservoir"]),
        _risk("clogged_irrigation", "Clogged irrigation", clog_score, clog_factors, ["flush_lines", "check_pump"]),
        _risk("dehydration_stress", "Dehydration stress", dehydration_score, dehydration_factors, ["top_up_water", "check_pump"]),
        _risk("mold_fungal", "Mold/fungal conditions", mold_score, mold_factors, ["increase_airflow", "inspect_roots"]),
    ]


def get_recommendations(risks: list[RiskScore]) -> list[ApprovedAction]:
    action_ids: list[str] = []
    for risk in sorted(risks, key=lambda item: item.score, reverse=True):
        if risk.score >= 35:
            action_ids.extend(risk.recommended_action_ids)

    unique_ids = list(dict.fromkeys(action_ids))
    if not unique_ids:
        unique_ids = ["inspect_roots"]

    return [APPROVED_ACTIONS[action_id] for action_id in unique_ids]
