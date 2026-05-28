# GardenMind AI

GardenMind AI is a hackathon prototype for an AI-powered copilot for an autonomous indoor vertical tower garden.

It monitors pH, conductivity, turbidity, water temperature, humidity, and flow rate. It predicts nutrient imbalance, root disease risk, algae formation, clogged irrigation, dehydration stress, and mold or fungal conditions.

The prototype includes deterministic risk scoring, a lightweight digital twin, stochastic Monte Carlo forecasting, backend-only OpenAI explanations, a React dashboard, and approved safe action recommendations.

## Safety Model

- The OpenAI API key stays on the backend only.
- The LLM never directly controls hardware.
- The LLM may explain state and reference approved action IDs only.
- Chemical dosing and pH correction require human approval.
- Stochastic simulation is limited to the digital twin and forecasting layer.
- Safety checks, approved action validation, human approval rules, and any future hardware control stay deterministic.

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
- `GET /sensors`
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

## Environment

Copy `.env.example` to `.env` for local backend configuration, then add your real key locally:

```bash
OPENAI_API_KEY=your_api_key_here
OPENAI_MODEL=gpt-4o-mini
```

Do not put real API keys in frontend code, committed config, static assets, or API responses.

