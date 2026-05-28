import { useEffect, useMemo, useState } from "react";

const API_BASE = import.meta.env.VITE_API_BASE_URL || "http://localhost:8000";

const sensorLabels = {
  ph: "pH",
  conductivity: "Conductivity",
  turbidity: "Turbidity",
  water_temperature: "Water temp",
  humidity: "Humidity",
  flow_rate: "Flow rate",
};

const units = {
  ph: "",
  conductivity: "mS/cm",
  turbidity: "NTU",
  water_temperature: "C",
  humidity: "%",
  flow_rate: "L/min",
};

function statusClass(status) {
  return `status status-${status}`;
}

function App() {
  const [snapshot, setSnapshot] = useState(null);
  const [explanation, setExplanation] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  async function loadGardenState() {
    try {
      setError("");
      const [snapshotResponse, explanationResponse] = await Promise.all([
        fetch(`${API_BASE}/snapshot`),
        fetch(`${API_BASE}/explain`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ include_ai: true }),
        }),
      ]);

      if (!snapshotResponse.ok || !explanationResponse.ok) {
        throw new Error("Backend returned an error");
      }

      setSnapshot(await snapshotResponse.json());
      setExplanation(await explanationResponse.json());
    } catch (currentError) {
      setError(currentError.message);
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    loadGardenState();
    const interval = window.setInterval(loadGardenState, 10000);
    return () => window.clearInterval(interval);
  }, []);

  const topRisk = useMemo(() => {
    if (!snapshot?.risks?.length) {
      return null;
    }
    return [...snapshot.risks].sort((a, b) => b.score - a.score)[0];
  }, [snapshot]);

  if (loading) {
    return (
      <main className="shell">
        <Style />
        <section className="hero">
          <p className="eyebrow">GardenMind AI</p>
          <h1>Loading tower state...</h1>
        </section>
      </main>
    );
  }

  return (
    <main className="shell">
      <Style />
      <section className="hero">
        <div>
          <p className="eyebrow">GardenMind AI</p>
          <h1>Autonomous tower garden copilot</h1>
          <p className="hero-copy">
            Deterministic safety logic with stochastic forecasting kept inside the digital twin.
          </p>
        </div>
        <button className="refresh" onClick={loadGardenState}>Refresh</button>
      </section>

      {error && <div className="alert">Backend unavailable: {error}</div>}

      {snapshot && (
        <>
          <section className="overview">
            <div className="panel tower-panel">
              <div className="tower">
                <div className="water" />
                <div className="plant plant-a" />
                <div className="plant plant-b" />
                <div className="plant plant-c" />
                <div className="plant plant-d" />
              </div>
              <div>
                <p className="eyebrow">Digital twin</p>
                <h2>{snapshot.digital_twin.summary}</h2>
                <p>{snapshot.digital_twin.predicted_near_future_trend}</p>
              </div>
            </div>

            <div className="panel">
              <p className="eyebrow">Top deterministic risk</p>
              <h2>{topRisk.label}</h2>
              <div className="score-row">
                <span className={statusClass(topRisk.status)}>{topRisk.status}</span>
                <strong>{topRisk.score}/100</strong>
              </div>
              <p>{topRisk.contributing_factors[0]}</p>
            </div>
          </section>

          <section className="grid">
            <div className="panel">
              <h2>Sensors</h2>
              <div className="sensor-grid">
                {Object.entries(sensorLabels).map(([key, label]) => (
                  <div className="metric" key={key}>
                    <span>{label}</span>
                    <strong>{snapshot.sensors[key]} {units[key]}</strong>
                  </div>
                ))}
              </div>
            </div>

            <div className="panel">
              <h2>Risks</h2>
              <div className="stack">
                {snapshot.risks.map((risk) => (
                  <div className="risk" key={risk.id}>
                    <div>
                      <strong>{risk.label}</strong>
                      <span className={statusClass(risk.status)}>{risk.status}</span>
                    </div>
                    <div className="bar">
                      <span style={{ width: `${risk.score}%` }} />
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </section>

          <section className="grid">
            <div className="panel">
              <h2>Forecast</h2>
              <p className="muted">{snapshot.forecast.horizon_hours}h Monte Carlo, {snapshot.forecast.runs} runs</p>
              <div className="stack">
                {snapshot.forecast.bands.map((band) => (
                  <div className="forecast" key={band.risk_id}>
                    <span>{band.label}</span>
                    <strong>Expected {band.expected_score}, p90 {band.p90_score}</strong>
                    <small>{Math.round(band.probability_high_or_critical * 100)}% chance high+</small>
                  </div>
                ))}
              </div>
            </div>

            <div className="panel">
              <h2>Approved Actions</h2>
              <div className="stack">
                {snapshot.recommendations.map((action) => (
                  <div className="action" key={action.id}>
                    <strong>{action.label}</strong>
                    <code>{action.id}</code>
                    {action.requires_human_approval && <span className="approval">Human approval required</span>}
                    <p>{action.rationale}</p>
                  </div>
                ))}
              </div>
            </div>
          </section>

          <section className="panel ai-panel">
            <p className="eyebrow">{explanation?.used_ai ? "OpenAI explanation" : "Local fallback explanation"}</p>
            <h2>Operator brief</h2>
            <p>{explanation?.explanation}</p>
            <div className="ids">
              {(explanation?.approved_action_ids || []).map((id) => <code key={id}>{id}</code>)}
            </div>
          </section>
        </>
      )}
    </main>
  );
}

function Style() {
  return (
    <style>{`
      * { box-sizing: border-box; }
      body {
        margin: 0;
        font-family: Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
        background: #f4f7f2;
        color: #17211b;
      }
      .shell {
        width: min(1180px, calc(100% - 32px));
        margin: 0 auto;
        padding: 28px 0 44px;
      }
      .hero {
        min-height: 240px;
        display: flex;
        align-items: center;
        justify-content: space-between;
        gap: 24px;
        padding: 30px 0;
      }
      h1, h2, p { margin-top: 0; }
      h1 { max-width: 760px; margin-bottom: 12px; font-size: clamp(2.2rem, 7vw, 5.8rem); line-height: .92; }
      h2 { margin-bottom: 12px; font-size: 1.15rem; line-height: 1.25; }
      .eyebrow {
        margin-bottom: 10px;
        color: #4d6d59;
        font-size: .78rem;
        font-weight: 800;
        letter-spacing: .08em;
        text-transform: uppercase;
      }
      .hero-copy { max-width: 620px; color: #405247; font-size: 1.08rem; }
      .refresh {
        border: 1px solid #b8c9be;
        border-radius: 8px;
        background: #ffffff;
        color: #17211b;
        cursor: pointer;
        font-weight: 800;
        padding: 11px 16px;
        white-space: nowrap;
      }
      .overview, .grid {
        display: grid;
        grid-template-columns: minmax(0, 1.3fr) minmax(320px, .7fr);
        gap: 16px;
        margin-bottom: 16px;
      }
      .panel {
        background: #ffffff;
        border: 1px solid #dbe5dd;
        border-radius: 8px;
        padding: 18px;
        box-shadow: 0 8px 24px rgba(33, 49, 39, .06);
      }
      .tower-panel {
        display: grid;
        grid-template-columns: 150px minmax(0, 1fr);
        align-items: center;
        gap: 18px;
      }
      .tower {
        position: relative;
        width: 112px;
        height: 220px;
        margin: 0 auto;
        border: 10px solid #dce9df;
        border-radius: 56px;
        background: linear-gradient(#f8fbf9, #e8f1eb);
        overflow: hidden;
      }
      .water {
        position: absolute;
        left: 0;
        right: 0;
        bottom: 0;
        height: 34%;
        background: #7dc8d8;
      }
      .plant {
        position: absolute;
        width: 42px;
        height: 24px;
        background: #34a853;
        border-radius: 100% 0 100% 0;
      }
      .plant-a { left: 10px; top: 34px; transform: rotate(-30deg); }
      .plant-b { right: 10px; top: 72px; transform: rotate(35deg); }
      .plant-c { left: 8px; top: 116px; transform: rotate(-32deg); }
      .plant-d { right: 8px; top: 154px; transform: rotate(34deg); }
      .sensor-grid {
        display: grid;
        grid-template-columns: repeat(2, minmax(0, 1fr));
        gap: 10px;
      }
      .metric, .forecast, .action {
        border: 1px solid #e3ece6;
        border-radius: 8px;
        padding: 12px;
        background: #fbfdfb;
      }
      .metric span, .forecast span { display: block; color: #627368; font-size: .86rem; }
      .metric strong { display: block; margin-top: 6px; font-size: 1.25rem; }
      .stack { display: grid; gap: 10px; }
      .risk > div:first-child, .score-row {
        display: flex;
        align-items: center;
        justify-content: space-between;
        gap: 12px;
      }
      .status {
        border-radius: 999px;
        padding: 4px 8px;
        font-size: .72rem;
        font-weight: 900;
        text-transform: uppercase;
      }
      .status-low { background: #dff3e4; color: #176332; }
      .status-medium { background: #fff0c7; color: #7b4d00; }
      .status-high { background: #ffe0c8; color: #8b3900; }
      .status-critical { background: #ffd7d7; color: #9c1b1b; }
      .bar {
        height: 9px;
        margin-top: 10px;
        border-radius: 999px;
        background: #e8eee9;
        overflow: hidden;
      }
      .bar span {
        display: block;
        height: 100%;
        border-radius: inherit;
        background: #2f855a;
      }
      .muted, small { color: #627368; }
      code {
        display: inline-block;
        margin: 6px 6px 0 0;
        border-radius: 6px;
        background: #edf4ef;
        padding: 4px 6px;
        font-size: .78rem;
      }
      .approval {
        display: inline-block;
        margin-top: 8px;
        border-radius: 6px;
        background: #fff0c7;
        color: #7b4d00;
        padding: 5px 7px;
        font-size: .78rem;
        font-weight: 800;
      }
      .ai-panel { margin-top: 16px; }
      .alert {
        margin-bottom: 16px;
        border-radius: 8px;
        background: #ffe1e1;
        color: #8b1f1f;
        padding: 12px 14px;
        font-weight: 700;
      }
      @media (max-width: 820px) {
        .hero, .overview, .grid, .tower-panel {
          display: block;
        }
        .refresh, .panel { margin-top: 12px; }
        .sensor-grid { grid-template-columns: 1fr; }
      }
    `}</style>
  );
}

export default App;
