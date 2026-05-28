# AGENTS.md

Guidance for AI coding agents working in this repository.

## Project Context

This project is GardenSpace AI, a hackathon prototype for a camera-based workplace tower-garden assistant. The priority is a convincing, working web app demo with clear privacy and safety boundaries, not a perfect production architecture.

The system uses:

- Uploaded images
- Webcam snapshots
- Demo scenarios
- Optional future camera stream

The system should analyze:

- Plant visible health
- Dryness or wilting signs
- Whether the area looks neglected
- Whether the reservoir or watering area needs checking
- Whether the garden space looks suitable for a short team meeting or wellbeing break

The AI agent should produce:

- Plant care recommendation
- Employee notification message
- Urgency level
- Suggested next action
- Optional meeting or wellbeing suggestion
- Explanation of what it observed

Core expected features:

- Image upload or webcam capture in the frontend
- Demo scenarios that do not require real camera hardware
- Deterministic visual risk scoring
- Lightweight digital twin for the garden area
- Stochastic Monte Carlo forecasting for demo trends
- Backend-only OpenAI-powered employee-friendly explanations
- React dashboard
- Safe action recommendations
- Simulated phone-style employee notification shown in the app

## Determinism And Stochastic Simulation

The system may be stochastic only inside the digital twin and forecasting layer.

The following must remain deterministic:

- Approved action validation
- Safety checks
- Human approval rules
- Notification routing mode, such as simulated versus real provider
- Any future hardware control
- Any future watering, pump, valve, light, fan, camera, or reservoir workflows

Monte Carlo simulation, randomized forecasts, and probabilistic scenario exploration are allowed for demo forecasting and digital twin behavior. They must not decide whether an action is safe, whether approval is required, whether a real notification should be sent, or whether hardware should be controlled.

## Safety Rules

These rules are mandatory:

- Never expose the OpenAI API key in frontend code.
- Keep all OpenAI API calls on the backend.
- The LLM must never directly control hardware.
- The LLM may explain observations and recommend actions only.
- The LLM may recommend only approved action IDs.
- Only approved safe actions may be recommended.
- Do not add autonomous actuation for pumps, valves, dosing, lights, fans, cameras, or other hardware unless there is an explicit human approval step.
- Prefer conservative recommendations when image data is uncertain, missing, stochastic, simulated, or low confidence.
- Reservoir or maintenance findings should be framed as requests for a human check, not claims that work was performed.
- The system should not claim certainty from images. Use language like "appears", "may need", and "suggests".

## Privacy Rules

These privacy rules are mandatory:

- Do not identify employees or analyze faces.
- Do not track individuals.
- Do not make sensitive inferences about people.
- Do not infer identity, emotion, productivity, health, age, gender, ethnicity, or other personal attributes.
- If people appear in the image, describe only non-identifying context such as "the area appears occupied."
- Focus only on the plant, tower garden, visible environment, reservoir or watering area, and general space availability.
- Do not store personal imagery longer than needed for the local demo flow unless the user explicitly adds storage behavior.
- Keep explanations uncertainty-aware. Prefer "appears", "may need", "could use", "suggests", and "worth checking" over certainty claims.

## Notification Behavior

When the simulation runs, the system should create a phone-style notification for a mock employee.

Notification requirements:

- The notification is simulated by default and shown in the app, not sent as a real SMS.
- The phone notification should contain the agent's employee-friendly message.
- The notification should include an urgency level and suggested next action when available.
- The mock recipient should be generic, such as "Mock employee" or "Workplace garden buddy"; do not use or infer real employee identities from images.
- The notification copy should be calm, positive, and action-oriented.
- The app should make it clear that the notification is simulated.

Future provider guidance:

- Design notification code behind a small interface or service boundary so real providers can be added later.
- Possible future providers include SMS, WhatsApp, Slack, Teams, or push notifications.
- Provider-specific credentials must remain backend-only and out of version control.
- Real outbound notifications must require explicit configuration and should not be enabled by default.

## Hackathon Priorities

Optimize for demo value:

- Make the app easy to run locally.
- Keep data flows simple and visible.
- Prefer deterministic visual scoring plus AI explanation over opaque logic.
- Use uploaded demo images, demo scenarios, or webcam capture when real camera hardware is unavailable.
- Make the dashboard show the current image, clear labels, urgency, forecast, recommended next steps, and simulated phone notification.
- Keep implementation understandable for judges and teammates.

Avoid spending time on:

- Overly complex infrastructure.
- Premature microservices.
- Heavy database design unless already present.
- Perfect computer vision models when heuristic scoring is enough for the demo.

## Architecture Guidance

Recommended shape:

- Backend handles image observation analysis, deterministic visual risk scoring, notification message generation, digital twin state, Monte Carlo forecasting, approved action lists, and OpenAI calls.
- Frontend handles image upload, webcam capture, image preview, display of backend results, and simulated phone-style notification UI.
- Shared action IDs and labels should come from backend-approved constants or schemas.
- Approved action validation should be deterministic and backend-owned.
- Any recommendation involving physical maintenance or reservoir checks should be framed as a human task.
- Any future camera stream should be optional and should follow the same privacy rules as uploaded images and webcam snapshots.

Do not put secrets in:

- React source files
- Browser environment variables
- Static assets
- Committed config files
- API responses

Use `.env` only for local backend secrets, and keep it out of version control.

## OpenAI Usage

OpenAI integration should be used for explanations, summaries, and employee-friendly guidance. It should not be the source of truth for safety decisions.

Before calling the LLM:

- Compute visual observation status and deterministic risk scores in backend code.
- Generate any stochastic forecast only in the digital twin or forecasting layer.
- Map possible recommendations to an approved safe-action list.
- Pass approved action IDs to the model instead of free-form action authority.
- Pass only sanitized observation state to the model.
- Do not pass API keys or secrets.
- Do not ask the model to identify people, analyze faces, track individuals, or infer sensitive personal attributes.

The model may:

- Explain why visual risks are elevated.
- Summarize observed plant condition and forecasts.
- Suggest approved safe actions.
- Refer to approved action IDs.
- Tell employees when a human check is needed.
- Produce an employee notification message.
- Suggest a short meeting or wellbeing break near the garden when the space appears suitable.

The model must not:

- Invent direct hardware commands.
- Override risk scoring logic.
- Override action validation.
- Invent action IDs.
- Claim that watering, maintenance, or hardware actions have been performed.
- Identify employees, analyze faces, track individuals, or make sensitive inferences about people.
- Claim certainty about image observations.
- Receive or expose API keys.

## Risk Scoring Guidance

For the demo, simple heuristic visual scoring is acceptable. Risk scoring must be deterministic and transparent.

Each risk should ideally include:

- Score from 0 to 100
- Status such as `low`, `medium`, `high`, or `critical`
- Urgency level suitable for employee notification
- Main contributing visual factors
- Recommended approved action IDs
- Whether human approval is required

When in doubt, keep thresholds easy to adjust and document assumptions near the scoring code.

## Digital Twin And Forecasting Guidance

The digital twin can be lightweight. It should represent the current virtual state of the workplace garden area, such as:

- Workplace area condition
- Plant appearance
- Reservoir attention
- Team engagement opportunity
- Maintenance urgency
- Meeting or wellbeing suitability
- Predicted near-future trend

Monte Carlo forecasting may be used to simulate likely future states, uncertainty bands, and scenario outcomes. Keep the output demo-friendly and clearly separate forecasts from deterministic safety decisions.

## Frontend Guidance

The React dashboard should prioritize:

- Image upload and webcam capture
- Demo scenario selection if useful for hackathon flow
- Current image preview
- Detected plant appearance labels
- Urgency level
- Risk cards or gauges
- Digital twin visualization
- Forecast visualization
- AI explanation panel
- Simulated phone-style notification for a mock employee
- Safe employee action recommendation panel

Do not call OpenAI from the React app. The frontend should call backend endpoints only.

## Backend Guidance

Backend endpoints should be clear and demo-friendly. Useful endpoints may include:

- `GET /health`
- `GET /observation`
- `POST /analyze-image`
- `POST /explain-image`
- `GET /risks`
- `GET /digital-twin`
- `GET /forecast`
- `GET /recommendations`
- `GET /snapshot`
- `POST /explain`
- Future optional notification endpoints such as `POST /notifications/simulate`

If the existing code uses different routes or patterns, follow the existing project style instead of forcing this exact shape.

Notification provider code should remain backend-owned. Start with a simulated provider, then add real provider adapters only when explicitly needed.

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
- The frontend can upload or capture a garden image.
- Visual observations, urgency, risks, and recommendations are visible and understandable.
- A simulated phone-style notification appears in the app when the simulation runs.
- Forecasting is clearly separated from deterministic safety logic.
- Sensitive physical actions are framed as human checks.
- Privacy rules are respected: no face analysis, no identification, no tracking, and no sensitive inferences.
- OpenAI explanations are generated through backend code only.
- The app remains easy for teammates to run during the hackathon.
