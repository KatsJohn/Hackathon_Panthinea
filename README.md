# GardenSpace AI

GardenSpace AI is a hackathon prototype for a camera-based AI agent for an indoor vertical tower garden in a workplace.

It monitors the garden area using uploaded demo images or webcam captures. The prototype detects whether plants appear dry, wilted, healthy, crowded, or neglected, flags when the water reservoir area may need checking, and suggests positive employee-friendly actions.

The demo includes deterministic visual risk scoring, a lightweight digital twin, stochastic Monte Carlo forecasting, backend-only OpenAI explanations, a React dashboard, and approved safe recommendations.

## Safety Model

- The OpenAI API key stays on the backend only.
- The LLM never directly controls hardware.
- The LLM may explain observations and reference approved action IDs only.
- Recommendations are employee notifications, visual checks, and manual workplace actions.
- Stochastic simulation is limited to the digital twin and forecasting layer.
- Action approval and any future hardware control must stay deterministic and human-mediated.

## Backend

```bash
cd backend
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

The backend runs at `http://localhost:8000`.

Useful endpoints:

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

## Frontend

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

## Demo Images

The prototype does not require real camera hardware at first. Use the upload control or webcam capture in the dashboard.

For predictable hackathon demos, image filenames can include words like `healthy`, `dry`, `wilt`, `crowd`, `neglect`, or `reservoir` to steer the deterministic demo analysis.

## Environment

Copy `.env.example` to `.env` for local backend configuration, then add your real key locally:

```bash
OPENAI_API_KEY=your_api_key_here
OPENAI_MODEL=gpt-4o-mini
```

Do not put real API keys in frontend code, committed config, static assets, or API responses.
