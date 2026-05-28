# GardenSpace AI

GardenSpace AI is a hackathon prototype for a camera-based workplace tower-garden assistant. It helps employees and facilities teams notice when an indoor vertical garden may need water, reservoir attention, tidying, or a simple wellbeing moment near the plants.

The priority is a working web app demo. Real camera hardware is not required at first.

## What The App Does

- Analyzes uploaded images, webcam snapshots, or scripted demo scenarios.
- Checks visible plant and garden-space conditions such as healthy plants, possible dryness, wilting, clutter, neglect, and reservoir/watering area concerns.
- Produces employee-friendly observations, urgency, plant-care recommendations, and suggested next actions.
- Creates simulated phone notifications for a mock employee when plant care or maintenance may be needed.
- Suggests short plant-side meetings or wellbeing breaks when the garden area appears clean, calm, and available.
- Shows a virtual environment where a generic employee avatar receives the AI message on a phone.

## Camera And Image Flow

The frontend can use:

- An uploaded image.
- A webcam snapshot.
- A scripted demo scenario.
- A future camera stream integration.

Images are sent from the React frontend to the FastAPI backend. The backend performs the analysis and returns a structured GardenSpace AI response. Do not put OpenAI API keys or other secrets in frontend code.

## Employee Notifications

GardenSpace AI decides whether an employee should be notified based on visible plant health, dryness or wilting signs, reservoir/watering concerns, and whether the area appears neglected.

The notification response includes:

- Urgency level.
- Notification title.
- Employee-friendly message.
- Suggested next action.
- Simulated delivery result.

In this prototype, phone notifications are simulated inside the app so the hackathon demo works reliably without external messaging services.

## Mock Phone Simulation

The backend keeps temporary in-memory mock phone notifications. When a scenario or image analysis creates a notification, the app can show it in the "Employee Phone" panel.

This does not send a real SMS and does not require real phone numbers. The mock phone is only for demo visualization. The notification history resets when the backend process restarts or when the app's Clear Phone button is used.

Future integrations could add SMS, WhatsApp Business API, Slack, Microsoft Teams, or mobile push notifications behind the same notification decision flow.

## Plant-Side Meeting Suggestions

When the garden space appears free and the plants appear healthy or no clear plant-care issue is visible, GardenSpace AI may suggest a short workplace action such as:

- A 10-minute team check-in.
- A wellbeing break.
- A stand-up meeting near the garden.
- A sustainability reflection session.

The mock calendar button can create a simulated calendar suggestion near the tower garden. It does not create a real calendar event or invite.

## Privacy Rules

GardenSpace AI analyzes the tower garden and surrounding space. It does not identify employees, analyze faces, track individuals, or make sensitive personal inferences. Images are used for plant-care and space-status analysis only. In this prototype, images are not stored permanently.

If people appear in an image, the system should describe only non-identifying context such as "the area appears occupied." The app should use uncertain language such as "appears," "may need," and "suggests" when interpreting images.

## Run The Backend

```bash
cd backend
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

The backend runs at `http://localhost:8000`.

Useful GardenSpace endpoints:

- `GET /`
- `GET /health`
- `GET /api/demo/scenarios`
- `POST /api/demo/scenario/{scenario_name}`
- `POST /api/vision/analyze`
- `POST /api/mock-phone/clear`
- `GET /api/mock-phone/notifications`
- `POST /api/calendar/mock-event`

## Run The Frontend

```bash
cd frontend
npm install
npm run dev
```

The frontend runs at `http://localhost:5173` and calls the backend at `http://localhost:8000` by default.

To use a different backend URL, create a frontend environment variable:

```bash
VITE_API_BASE_URL=http://localhost:8000
```

## Environment

Copy `.env.example` to `.env` for local backend configuration, then add your real key locally:

```bash
OPENAI_API_KEY=your_api_key_here
OPENAI_MODEL=gpt-4o-mini
```

Do not put real API keys in frontend code, committed config, static assets, or API responses.

## 60-Second Demo Script

1. Open the app.
2. Select the `dry_plants` demo scenario.
3. Show the AI observation that the plants may need water.
4. Show the employee phone receiving a message from GardenSpace AI.
5. Select `low_water_check`.
6. Show the phone notification asking the employee to check or add water to the reservoir.
7. Select `meeting_friendly_space`.
8. Show the meeting suggestion near the tower garden.
9. Explain that real SMS, WhatsApp, Slack, Teams, or push notifications could be added later.
