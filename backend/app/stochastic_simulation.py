from random import Random

from .models import ForecastBand, ForecastResponse, RiskScore, SensorReading


def run_monte_carlo_forecast(
    reading: SensorReading,
    risks: list[RiskScore],
    runs: int = 250,
    horizon_hours: int = 6,
) -> ForecastResponse:
    """Run stochastic demo forecasting only; never use this for safety decisions."""
    seed = int(sum(ord(char) for char in reading.timestamp))
    rng = Random(seed)
    bands: list[ForecastBand] = []

    for risk in risks:
        samples = []
        for _ in range(runs):
            drift = 0
            if risk.id in {"algae_formation", "root_disease"} and reading.water_temperature > 22:
                drift += rng.uniform(1, 9)
            if risk.id in {"clogged_irrigation", "dehydration_stress"} and reading.flow_rate < 1.1:
                drift += rng.uniform(2, 12)
            if risk.id == "mold_fungal" and reading.humidity > 70:
                drift += rng.uniform(2, 10)
            if risk.id == "nutrient_imbalance" and (reading.ph < 6.0 or reading.ph > 6.8):
                drift += rng.uniform(1, 8)

            noise = rng.gauss(0, 6)
            samples.append(max(0, min(100, round(risk.score + drift + noise))))

        samples.sort()
        expected = round(sum(samples) / len(samples))
        p90 = samples[int(len(samples) * 0.9) - 1]
        probability_high = sum(1 for value in samples if value >= 60) / len(samples)

        bands.append(
            ForecastBand(
                risk_id=risk.id,
                label=risk.label,
                current_score=risk.score,
                expected_score=expected,
                p90_score=p90,
                probability_high_or_critical=round(probability_high, 2),
            )
        )

    return ForecastResponse(
        horizon_hours=horizon_hours,
        runs=runs,
        note="Monte Carlo output is for digital twin forecasting only, not safety validation or hardware control.",
        bands=bands,
    )
