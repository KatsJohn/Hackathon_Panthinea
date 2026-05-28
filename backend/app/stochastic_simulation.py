from random import Random

from .models import CameraObservation, ForecastBand, ForecastResponse, RiskScore


def run_monte_carlo_forecast(
    observation: CameraObservation,
    risks: list[RiskScore],
    runs: int = 250,
    horizon_hours: int = 6,
) -> ForecastResponse:
    """Run stochastic demo forecasting only; never use this for action approval."""
    seed = int(sum(ord(char) for char in observation.timestamp + observation.image_name))
    rng = Random(seed)
    bands: list[ForecastBand] = []

    for risk in risks:
        samples = []
        for _ in range(runs):
            drift = 0
            if risk.id in {"dry_appearance", "wilted_appearance"} and observation.dryness_score > 55:
                drift += rng.uniform(1, 10)
            if risk.id == "reservoir_attention" and observation.reservoir_check_score > 55:
                drift += rng.uniform(2, 12)
            if risk.id == "neglected_area" and observation.neglect_score > 55:
                drift += rng.uniform(2, 10)
            if risk.id == "crowded_growth" and observation.crowding_score > 60:
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
        note="Monte Carlo output is for demo forecasting only, not action approval or hardware control.",
        bands=bands,
    )
