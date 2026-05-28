import { useEffect, useMemo, useRef, useState } from "react";

const API_BASE = import.meta.env.VITE_API_BASE_URL || "http://localhost:8000";

const observationMetrics = {
  plant_health_index: "Health index",
  dryness_score: "Dry look",
  wilt_score: "Wilt look",
  crowding_score: "Crowding",
  neglect_score: "Neglect cues",
  reservoir_check_score: "Reservoir check",
};

const twinLabels = {
  workplace_area_condition: "Workplace area",
  plant_appearance: "Plant appearance",
  reservoir_attention: "Reservoir attention",
  team_engagement: "Team engagement",
  maintenance_urgency: "Maintenance urgency",
};

function statusClass(status) {
  return `status status-${status}`;
}

function App() {
  const [snapshot, setSnapshot] = useState(null);
  const [explanation, setExplanation] = useState(null);
  const [preview, setPreview] = useState("");
  const [loading, setLoading] = useState(true);
  const [cameraOn, setCameraOn] = useState(false);
  const [error, setError] = useState("");
  const videoRef = useRef(null);
  const streamRef = useRef(null);

  async function loadDemoState() {
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

  async function analyzeImage(imageDataUrl, imageName, source) {
    try {
      setError("");
      setLoading(true);
      const imageBase64 = imageDataUrl.includes(",") ? imageDataUrl.split(",")[1] : imageDataUrl;
      const body = JSON.stringify({
        image_base64: imageBase64,
        location_name: imageName,
        notes: `${source} garden image`,
      });
      const [snapshotResponse, explanationResponse] = await Promise.all([
        fetch(`${API_BASE}/analyze-image`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body,
        }),
        fetch(`${API_BASE}/explain-image`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body,
        }),
      ]);

      if (!snapshotResponse.ok || !explanationResponse.ok) {
        throw new Error("Image analysis failed");
      }

      setSnapshot(await snapshotResponse.json());
      setExplanation(await explanationResponse.json());
    } catch (currentError) {
      setError(currentError.message);
    } finally {
      setLoading(false);
    }
  }

  function handleUpload(event) {
    const file = event.target.files?.[0];
    if (!file) {
      return;
    }

    const reader = new FileReader();
    reader.onload = () => {
      const imageDataUrl = String(reader.result || "");
      setPreview(imageDataUrl);
      analyzeImage(imageDataUrl, file.name, "upload");
    };
    reader.readAsDataURL(file);
  }

  async function startCamera() {
    try {
      setError("");
      const stream = await navigator.mediaDevices.getUserMedia({ video: true });
      streamRef.current = stream;
      if (videoRef.current) {
        videoRef.current.srcObject = stream;
      }
      setCameraOn(true);
    } catch (currentError) {
      setError(currentError.message || "Camera permission was not granted");
    }
  }

  function stopCamera() {
    streamRef.current?.getTracks().forEach((track) => track.stop());
    streamRef.current = null;
    setCameraOn(false);
  }

  function captureWebcam() {
    const video = videoRef.current;
    if (!video) {
      return;
    }
    const canvas = document.createElement("canvas");
    canvas.width = video.videoWidth || 960;
    canvas.height = video.videoHeight || 540;
    canvas.getContext("2d").drawImage(video, 0, 0, canvas.width, canvas.height);
    const imageDataUrl = canvas.toDataURL("image/jpeg", 0.86);
    setPreview(imageDataUrl);
    analyzeImage(imageDataUrl, `webcam-capture-${Date.now()}.jpg`, "webcam");
  }

  useEffect(() => {
    loadDemoState();
    return () => stopCamera();
  }, []);

  const topRisk = useMemo(() => {
    if (!snapshot?.risks?.length) {
      return null;
    }
    return [...snapshot.risks].sort((a, b) => b.score - a.score)[0];
  }, [snapshot]);

  if (loading && !snapshot) {
    return (
      <main className="shell">
        <Style />
        <section className="hero">
          <p className="eyebrow">GardenSpace AI</p>
          <h1>Loading workplace garden view...</h1>
        </section>
      </main>
    );
  }

  return (
    <main className="shell">
      <Style />
      <section className="hero">
        <div>
          <p className="eyebrow">GardenSpace AI</p>
          <h1>Camera agent for a workplace tower garden</h1>
          <p className="hero-copy">
            Friendly visual checks for plant appearance, reservoir attention, and shared workplace care.
          </p>
        </div>
        <button className="refresh" onClick={loadDemoState}>Demo refresh</button>
      </section>

      {error && <div className="alert">Demo issue: {error}</div>}

      <section className="capture-band">
        <div className="camera-surface">
          {preview ? <img src={preview} alt="Uploaded tower garden preview" /> : <div className="demo-scene">
            <div className="window" />
            <div className="tower">
              <span />
              <span />
              <span />
              <span />
            </div>
            <div className="reservoir" />
          </div>}
          <video ref={videoRef} autoPlay playsInline muted className={cameraOn ? "video-on" : ""} />
        </div>
        <div className="capture-tools">
          <label className="file-button">
            Upload image
            <input type="file" accept="image/*" onChange={handleUpload} />
          </label>
          <button onClick={cameraOn ? stopCamera : startCamera}>{cameraOn ? "Stop webcam" : "Start webcam"}</button>
          <button onClick={captureWebcam} disabled={!cameraOn}>Capture</button>
        </div>
      </section>

      {snapshot && topRisk && (
        <>
          <section className="overview">
            <div className="panel">
              <p className="eyebrow">Current observation</p>
              <h2>{snapshot.observation.detected_conditions.join(", ")}</h2>
              <p>{snapshot.digital_twin.summary}</p>
              <div className="score-row">
                <span className={statusClass(topRisk.status)}>{topRisk.status}</span>
                <strong>{topRisk.score}/100</strong>
              </div>
            </div>
            <div className="panel">
              <p className="eyebrow">Top visual signal</p>
              <h2>{topRisk.label}</h2>
              <p>{topRisk.contributing_factors[0]}</p>
            </div>
          </section>

          <section className="grid">
            <div className="panel">
              <h2>Visual Scores</h2>
              <div className="metric-grid">
                {Object.entries(observationMetrics).map(([key, label]) => (
                  <div className="metric" key={key}>
                    <span>{label}</span>
                    <strong>{snapshot.observation[key]}</strong>
                  </div>
                ))}
              </div>
            </div>

            <div className="panel">
              <h2>Digital Twin</h2>
              <div className="stack">
                {Object.entries(twinLabels).map(([key, label]) => (
                  <div className="twin-row" key={key}>
                    <span>{label}</span>
                    <span className={statusClass(snapshot.digital_twin[key])}>{snapshot.digital_twin[key]}</span>
                  </div>
                ))}
              </div>
            </div>
          </section>

          <section className="grid">
            <div className="panel">
              <h2>Visual Risks</h2>
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

            <div className="panel">
              <h2>Employee Actions</h2>
              <div className="stack">
                {snapshot.recommendations.map((action) => (
                  <div className="action" key={action.id}>
                    <strong>{action.label}</strong>
                    <code>{action.id}</code>
                    <p>{action.rationale}</p>
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
                {snapshot.forecast.bands.slice(0, 4).map((band) => (
                  <div className="forecast" key={band.risk_id}>
                    <span>{band.label}</span>
                    <strong>Expected {band.expected_score}, p90 {band.p90_score}</strong>
                    <small>{Math.round(band.probability_high_or_critical * 100)}% chance high+</small>
                  </div>
                ))}
              </div>
            </div>

            <div className="panel ai-panel">
              <p className="eyebrow">{explanation?.used_ai ? "OpenAI explanation" : "Local fallback explanation"}</p>
              <h2>Employee brief</h2>
              <p>{explanation?.explanation}</p>
              <div className="ids">
                {(explanation?.approved_action_ids || []).map((id) => <code key={id}>{id}</code>)}
              </div>
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
        background: #f6f7f4;
        color: #18211f;
      }
      .shell {
        width: min(1180px, calc(100% - 32px));
        margin: 0 auto;
        padding: 28px 0 44px;
      }
      .hero {
        min-height: 230px;
        display: flex;
        align-items: center;
        justify-content: space-between;
        gap: 24px;
        padding: 28px 0;
      }
      h1, h2, p { margin-top: 0; }
      h1 { max-width: 820px; margin-bottom: 12px; font-size: clamp(2.35rem, 7vw, 5.6rem); line-height: .94; }
      h2 { margin-bottom: 12px; font-size: 1.18rem; line-height: 1.25; }
      .eyebrow {
        margin-bottom: 10px;
        color: #476557;
        font-size: .78rem;
        font-weight: 800;
        letter-spacing: .08em;
        text-transform: uppercase;
      }
      .hero-copy { max-width: 640px; color: #40524e; font-size: 1.08rem; }
      button, .file-button {
        border: 1px solid #b8c8c0;
        border-radius: 8px;
        background: #ffffff;
        color: #18211f;
        cursor: pointer;
        font: inherit;
        font-weight: 800;
        padding: 11px 16px;
        white-space: nowrap;
      }
      button:disabled {
        cursor: not-allowed;
        opacity: .5;
      }
      .capture-band {
        display: grid;
        grid-template-columns: minmax(0, 1.25fr) minmax(260px, .75fr);
        gap: 16px;
        margin-bottom: 16px;
        align-items: stretch;
      }
      .camera-surface {
        position: relative;
        min-height: 360px;
        border-radius: 8px;
        overflow: hidden;
        background: #dfe7e3;
        border: 1px solid #d5ded9;
      }
      .camera-surface img, .camera-surface video {
        width: 100%;
        height: 100%;
        min-height: 360px;
        object-fit: cover;
        display: block;
      }
      .camera-surface video {
        display: none;
        position: absolute;
        inset: 0;
      }
      .camera-surface .video-on { display: block; }
      .demo-scene {
        position: absolute;
        inset: 0;
        background: linear-gradient(120deg, #dfe8ea 0%, #f4f0e8 55%, #dce8df 100%);
      }
      .window {
        position: absolute;
        left: 32px;
        top: 32px;
        width: 34%;
        height: 44%;
        border: 10px solid rgba(255,255,255,.72);
        background: #a8cdd0;
      }
      .tower {
        position: absolute;
        left: 52%;
        top: 10%;
        width: 112px;
        height: 278px;
        border-radius: 56px;
        background: #f7fbf8;
        border: 10px solid #d7e2da;
      }
      .tower span {
        position: absolute;
        width: 54px;
        height: 30px;
        background: #2f8f52;
        border-radius: 100% 0 100% 0;
      }
      .tower span:nth-child(1) { left: -12px; top: 42px; transform: rotate(-28deg); }
      .tower span:nth-child(2) { right: -12px; top: 88px; transform: rotate(34deg); }
      .tower span:nth-child(3) { left: -12px; top: 148px; transform: rotate(-34deg); }
      .tower span:nth-child(4) { right: -12px; top: 204px; transform: rotate(30deg); }
      .reservoir {
        position: absolute;
        left: 48%;
        bottom: 34px;
        width: 178px;
        height: 48px;
        border-radius: 8px;
        background: #7eb6c6;
        border: 8px solid #e6ece9;
      }
      .capture-tools {
        display: flex;
        align-content: start;
        align-items: start;
        gap: 10px;
        flex-wrap: wrap;
        padding: 18px;
        border: 1px solid #dbe5dd;
        border-radius: 8px;
        background: #ffffff;
      }
      .file-button input { display: none; }
      .overview, .grid {
        display: grid;
        grid-template-columns: minmax(0, 1fr) minmax(320px, 1fr);
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
      .metric-grid {
        display: grid;
        grid-template-columns: repeat(3, minmax(0, 1fr));
        gap: 10px;
      }
      .metric, .forecast, .action {
        border: 1px solid #e3ece6;
        border-radius: 8px;
        padding: 12px;
        background: #fbfdfb;
      }
      .metric span, .forecast span, .twin-row > span:first-child { display: block; color: #627368; font-size: .86rem; }
      .metric strong { display: block; margin-top: 6px; font-size: 1.32rem; }
      .stack { display: grid; gap: 10px; }
      .risk > div:first-child, .score-row, .twin-row {
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
      .alert {
        margin-bottom: 16px;
        border-radius: 8px;
        background: #ffe1e1;
        color: #8b1f1f;
        padding: 12px 14px;
        font-weight: 700;
      }
      @media (max-width: 860px) {
        .hero, .capture-band, .overview, .grid {
          display: block;
        }
        .refresh, .capture-tools, .panel { margin-top: 12px; }
        .metric-grid { grid-template-columns: 1fr; }
      }
    `}</style>
  );
}

export default App;
