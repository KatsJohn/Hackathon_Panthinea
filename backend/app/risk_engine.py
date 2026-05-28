from .models import ApprovedAction, CameraObservation, RiskScore


APPROVED_ACTIONS: dict[str, ApprovedAction] = {
    "notify_water_check": ApprovedAction(
        id="notify_water_check",
        label="Notify employees to check plant water",
        category="notification",
        rationale="A friendly notification asks a person to check the tower before any maintenance is performed.",
    ),
    "inspect_reservoir_area": ApprovedAction(
        id="inspect_reservoir_area",
        label="Check the water reservoir area",
        category="reservoir",
        rationale="The demo can flag the reservoir for visual inspection without controlling pumps or valves.",
    ),
    "remove_dry_leaves": ApprovedAction(
        id="remove_dry_leaves",
        label="Remove dry leaves and tidy the tower",
        category="maintenance",
        rationale="A simple manual tidy-up keeps the workplace garden welcoming.",
    ),
    "space_or_trim_plants": ApprovedAction(
        id="space_or_trim_plants",
        label="Trim crowded growth",
        category="maintenance",
        rationale="Manual trimming can improve visibility and reduce crowding without automated actuation.",
    ),
    "schedule_plant_meetup": ApprovedAction(
        id="schedule_plant_meetup",
        label="Schedule a short meeting near the plants",
        category="workplace",
        rationale="A positive workplace moment can draw attention to the garden and encourage shared care.",
    ),
    "capture_followup_photo": ApprovedAction(
        id="capture_followup_photo",
        label="Capture another photo later today",
        category="observe",
        rationale="A follow-up image helps confirm whether the plant appearance is improving.",
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


def _risk(
    risk_id: str,
    label: str,
    score: float,
    factors: list[str],
    action_ids: list[str],
) -> RiskScore:
    final_score = _clamp(score)
    return RiskScore(
        id=risk_id,
        label=label,
        score=final_score,
        status=_status(final_score),
        contributing_factors=factors or ["The uploaded image looks close to the healthy demo baseline."],
        recommended_action_ids=action_ids,
        requires_human_approval=False,
    )


def calculate_risks(observation: CameraObservation) -> list[RiskScore]:
    """Calculate deterministic visual risks from the current camera observation."""
    dryness_factors = []
    if observation.dryness_score >= 45:
        dryness_factors.append("Leaves appear lighter, curled, or dry in the demo analysis.")
    if observation.reservoir_check_score >= 55:
        dryness_factors.append("The reservoir area may need a quick visual check.")

    wilt_factors = []
    if observation.wilt_score >= 45:
        wilt_factors.append("Some plants appear droopy or less upright than the healthy baseline.")
    if observation.neglect_score >= 55:
        wilt_factors.append("The tower area appears like it may not have been checked recently.")

    crowding_factors = []
    if observation.crowding_score >= 45:
        crowding_factors.append("Plant growth appears dense enough to hide parts of the tower.")

    neglect_factors = []
    if observation.neglect_score >= 45:
        neglect_factors.append("The area may need a tidy-up or employee attention.")
    if observation.confidence < 0.72:
        neglect_factors.append("Image confidence is moderate, so the app recommends conservative follow-up.")

    reservoir_factors = []
    if observation.reservoir_check_score >= 45:
        reservoir_factors.append("The visible reservoir zone is flagged for human inspection.")

    engagement_factors = []
    if observation.plant_health_index < 72:
        engagement_factors.append("A shared workplace check-in could turn maintenance into a visible team habit.")

    return [
        _risk(
            "dry_appearance",
            "Plants may look dry",
            observation.dryness_score,
            dryness_factors,
            ["notify_water_check", "capture_followup_photo"],
        ),
        _risk(
            "wilted_appearance",
            "Plants may look wilted",
            observation.wilt_score,
            wilt_factors,
            ["notify_water_check", "capture_followup_photo"],
        ),
        _risk(
            "crowded_growth",
            "Plants may look crowded",
            observation.crowding_score,
            crowding_factors,
            ["space_or_trim_plants", "schedule_plant_meetup"],
        ),
        _risk(
            "neglected_area",
            "Area may look neglected",
            observation.neglect_score,
            neglect_factors,
            ["remove_dry_leaves", "schedule_plant_meetup"],
        ),
        _risk(
            "reservoir_attention",
            "Reservoir may need checking",
            observation.reservoir_check_score,
            reservoir_factors,
            ["inspect_reservoir_area", "capture_followup_photo"],
        ),
        _risk(
            "workplace_engagement",
            "Workplace engagement opportunity",
            max(18, 100 - observation.plant_health_index),
            engagement_factors,
            ["schedule_plant_meetup"],
        ),
    ]


def get_recommendations(risks: list[RiskScore]) -> list[ApprovedAction]:
    action_ids: list[str] = []
    for risk in sorted(risks, key=lambda item: item.score, reverse=True):
        if risk.score >= 35:
            action_ids.extend(risk.recommended_action_ids)

    unique_ids = list(dict.fromkeys(action_ids))
    if not unique_ids:
        unique_ids = ["capture_followup_photo", "schedule_plant_meetup"]

    return [APPROVED_ACTIONS[action_id] for action_id in unique_ids]
