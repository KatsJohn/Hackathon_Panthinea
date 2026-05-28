from datetime import UTC, datetime
from math import sin

from .models import CameraObservation, ImageAnalysisRequest, PlantCondition


KEYWORD_HINTS: dict[str, tuple[list[PlantCondition], int, int, int, int, int]] = {
    "dry": (["dry"], 82, 36, 24, 38, 52),
    "wilt": (["wilted"], 58, 84, 28, 48, 46),
    "crowd": (["crowded"], 28, 24, 88, 42, 32),
    "neglect": (["neglected"], 64, 62, 36, 86, 72),
    "reservoir": (["healthy"], 28, 22, 30, 26, 82),
    "healthy": (["healthy"], 12, 10, 24, 12, 18),
}


def _wave(seed: float, low: int, high: int) -> int:
    normalized = (sin(seed) + 1) / 2
    return round(low + normalized * (high - low))


def _conditions(dryness: int, wilt: int, crowding: int, neglect: int) -> list[PlantCondition]:
    conditions: list[PlantCondition] = []
    if dryness >= 55:
        conditions.append("dry")
    if wilt >= 55:
        conditions.append("wilted")
    if crowding >= 60:
        conditions.append("crowded")
    if neglect >= 60:
        conditions.append("neglected")
    return conditions or ["healthy"]


def get_demo_observation(now: datetime | None = None) -> CameraObservation:
    """Return deterministic live-looking visual observations for hackathon demos."""
    current = now or datetime.now(UTC)
    minutes = current.timestamp() / 60
    dryness = _wave(minutes / 17, 16, 72)
    wilt = _wave(minutes / 23 + 0.8, 10, 68)
    crowding = _wave(minutes / 31 + 1.7, 22, 82)
    neglect = _wave(minutes / 29 + 2.4, 12, 74)
    reservoir = _wave(minutes / 19 + 1.1, 18, 84)
    health = max(0, 100 - round((dryness * 0.28) + (wilt * 0.28) + (neglect * 0.24) + (crowding * 0.12)))

    return CameraObservation(
        source="demo",
        image_name="rotating-demo-camera-view",
        detected_conditions=_conditions(dryness, wilt, crowding, neglect),
        plant_health_index=health,
        dryness_score=dryness,
        wilt_score=wilt,
        crowding_score=crowding,
        neglect_score=neglect,
        reservoir_check_score=reservoir,
        confidence=0.74,
        timestamp=current.isoformat(),
    )


def analyze_image(request: ImageAnalysisRequest, now: datetime | None = None) -> CameraObservation:
    """Produce deterministic demo image observations without requiring real CV hardware."""
    current = now or datetime.now(UTC)
    image_label = request.location_name or request.notes or "uploaded-garden-image"
    image_name = image_label.lower()
    for keyword, (conditions, dryness, wilt, crowding, neglect, reservoir) in KEYWORD_HINTS.items():
        if keyword in image_name:
            health = max(0, 100 - round((dryness * 0.28) + (wilt * 0.28) + (neglect * 0.24) + (crowding * 0.12)))
            return CameraObservation(
                source="upload",
                image_name=image_label,
                detected_conditions=conditions,
                plant_health_index=health,
                dryness_score=dryness,
                wilt_score=wilt,
                crowding_score=crowding,
                neglect_score=neglect,
                reservoir_check_score=reservoir,
                confidence=0.82,
                timestamp=current.isoformat(),
            )

    seed_text = f"{image_label}:{len(request.image_base64)}"
    seed = sum(ord(char) for char in seed_text)
    dryness = 18 + seed % 52
    wilt = 14 + (seed // 3) % 58
    crowding = 22 + (seed // 5) % 62
    neglect = 12 + (seed // 7) % 64
    reservoir = 16 + (seed // 11) % 70
    health = max(0, 100 - round((dryness * 0.28) + (wilt * 0.28) + (neglect * 0.24) + (crowding * 0.12)))

    return CameraObservation(
        source="upload",
        image_name=image_label,
        detected_conditions=_conditions(dryness, wilt, crowding, neglect),
        plant_health_index=health,
        dryness_score=dryness,
        wilt_score=wilt,
        crowding_score=crowding,
        neglect_score=neglect,
        reservoir_check_score=reservoir,
        confidence=0.68,
        timestamp=current.isoformat(),
    )
