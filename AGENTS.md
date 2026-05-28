# AGENTS.md

Guidance for AI coding agents working in this repository.

## Project Context

This project is GardenMind AI, a hackathon prototype for an AI-powered autonomous vertical tower garden. The priority is a convincing, working demo with clear safety boundaries, not a perfect production architecture.

The system monitors:

- pH
- Conductivity
- Turbidity
- Water temperature
- Humidity
- Flow rate

The system predicts:

- Nutrient imbalance
- Root disease risk
- Algae formation
- Clogged irrigation
- Dehydration stress
- Mold or fungal conditions

Core expected features:

- Sensor simulation
- Deterministic risk scoring
- Digital twin simulation
- Stochastic Monte Carlo forecasting
- OpenAI-powered AI explanations
- React dashboard
- Safe action recommendations

## Determinism And Stochastic Simulation

The system may be stochastic only inside the digital twin and forecasting layer.

The following must remain deterministic:

- Approved action validation
- Safety checks
- Real hardware control
- Human approval rules
- Chemical dosing and pH correction workflows

Monte Carlo simulation, randomized forecasts, and probabilistic scenario exploration are allowed for demo forecasting and digital twin behavior. They must not decide whether an action is safe, whether approval is required, or whether hardware should be controlled.

## Safety Rules

These rules are mandatory:

- Never expose the OpenAI API key in frontend code.
- Keep all OpenAI API calls on the backend.
- The LLM must never directly control hardware.
- The LLM may explain system state and recommend actions only.
- The LLM may recommend only approved action IDs.
- Only approved safe actions may be recommended.
- Chemical dosing and pH correction must require human approval.
- Do not add autonomous actuation for pumps, valves, dosing, lights, fans, or other hardware unless there is an explicit human approval step.
- Prefer conservative recommendations when sensor data is uncertain, missing, stochastic, or simulated.

## Hackathon Priorities

Optimize for demo value:

- Make the app easy to run locally.
- Keep data flows simple and visible.
- Prefer deterministic risk scoring plus AI explanation over opaque logic.
- Use mock sensor data when real hardware is unavailable.
- Make the dashboard show live-looking updates, clear risk labels, forecasts, and recommended next steps.
- Keep implementation understandable for judges and teammates.

Avoid spending time on:

- Overly complex infrastructure.
- Premature microservices.
- Heavy database design unless already present.
- Perfect ML models when heuristic scoring is enough for the demo.

## Architecture Guidance

Recommended shape:

- Backend handles sensor simulation, deterministic risk scoring, digital twin state, Monte Carlo forecasting, approved action lists, and OpenAI calls.
- Frontend displays sensor readings, risk scores, digital twin state, forecasts, AI explanations, and safe recommendations.
- Shared action IDs and labels should come from backend-approved constants or schemas.
- Approved action validation should be deterministic and backend-owned.
- Any recommendation involving chemicals, dosing, pH correction, or hardware actuation should be marked as requiring human approval.

Do not put secrets in:

- React source files
- Browser environment variables
- Static assets
- Committed config files
- API responses

Use `.env` only for local backend secrets, and keep it out of version control.

## OpenAI Usage

OpenAI integration should be used for explanations, summaries, and operator-friendly guidance. It should not be the source of truth for safety decisions.

Before calling the LLM:

- Compute sensor status and deterministic risk scores in backend code.
- Generate any stochastic forecast only in the digital twin or forecasting layer.
- Map possible recommendations to an approved safe-action list.
- Pass approved action IDs to the model instead of free-form action authority.
- Pass only sanitized system state to the model.

The model may:

- Explain why risks are elevated.
- Summarize sensor trends and forecasts.
- Suggest approved safe actions.
- Refer to approved action IDs.
- Tell the operator when human approval is required.

The model must not:

- Invent direct hardware commands.
- Override risk scoring logic.
- Override action validation.
- Invent action IDs.
- Recommend unapproved chemical dosing amounts.
- Claim that an unsafe action has been performed.
- Receive or expose API keys.

## Risk Scoring Guidance

For the demo, simple heuristic scoring is acceptable. Risk scoring must be deterministic and transparent.

Each risk should ideally include:

- Score from 0 to 100
- Status such as `low`, `medium`, `high`, or `critical`
- Main contributing sensor factors
- Recommended approved action IDs
- Whether human approval is required

When in doubt, keep thresholds easy to adjust and document assumptions near the scoring code.

## Digital Twin And Forecasting Guidance

The digital twin can be lightweight. It should represent the current virtual state of the tower garden, such as:

- Water quality
- Root-zone health
- Irrigation flow condition
- Environmental comfort
- Plant stress level
- Predicted near-future trend

Monte Carlo forecasting may be used to simulate likely future states, uncertainty bands, and scenario outcomes. Keep the output demo-friendly and clearly separate forecasts from deterministic safety decisions.

## Frontend Guidance

The React dashboard should prioritize:

- Current sensor readings
- Risk cards or gauges
- Digital twin visualization
- Forecast visualization
- AI explanation panel
- Safe action recommendation panel
- Clear human approval labels for sensitive actions

Do not call OpenAI from the React app. The frontend should call backend endpoints only.

## Backend Guidance

Backend endpoints should be clear and demo-friendly. Useful endpoints may include:

- `GET /health`
- `GET /sensors`
- `GET /risks`
- `GET /digital-twin`
- `GET /forecast`
- `GET /recommendations`
- `GET /snapshot`
- `POST /explain`

If the existing code uses different routes or patterns, follow the existing project style instead of forcing this exact shape.

## Coding Style

- Keep changes small and easy to review.
- Follow existing file organization and naming conventions.
- Prefer readable functions over clever abstractions.
- Add tests only where they help protect meaningful behavior within hackathon time.
- Do not rewrite unrelated code.
- Do not introduce new frameworks unless clearly needed.

## Definition Of Done

A useful demo-ready change should usually satisfy:

- The backend runs without exposing secrets.
- The frontend can show simulated garden state.
- Risks and recommendations are visible and understandable.
- Forecasting is clearly separated from deterministic safety logic.
- Sensitive actions are clearly gated behind human approval.
- OpenAI explanations are generated through backend code only.
- The app remains easy for teammates to run during the hackathon.
