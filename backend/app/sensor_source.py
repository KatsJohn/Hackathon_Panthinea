from datetime import UTC, datetime
from math import sin

from .models import SensorReading


def _wave(seed: float, low: float, high: float) -> float:
    normalized = (sin(seed) + 1) / 2
    return low + normalized * (high - low)


def get_sensor_reading(now: datetime | None = None) -> SensorReading:
    """Return deterministic live-looking sensor data for hackathon demos."""
    current = now or datetime.now(UTC)
    minutes = current.timestamp() / 60

    return SensorReading(
        ph=round(_wave(minutes / 17, 5.8, 7.4), 2),
        conductivity=round(_wave(minutes / 13 + 1.3, 1.2, 2.8), 2),
        turbidity=round(_wave(minutes / 19 + 2.1, 4.0, 38.0), 1),
        water_temperature=round(_wave(minutes / 23 + 0.7, 18.0, 25.5), 1),
        humidity=round(_wave(minutes / 11 + 2.8, 42.0, 84.0), 1),
        flow_rate=round(_wave(minutes / 29 + 1.9, 0.55, 2.25), 2),
        timestamp=current.isoformat(),
    )
