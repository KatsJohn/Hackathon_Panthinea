import { useEffect, useRef, useState } from "react";
import VirtualGardenScene from "./components/VirtualGardenScene";

const API_BASE = import.meta.env.VITE_API_BASE_URL || "http://localhost:8000";
const DEFAULT_SCENARIO = "healthy_garden";

function formatLabel(value) {
  return String(value || "unknown").replaceAll("_", " ");
}

function stripDataUrl(dataUrl) {
  return dataUrl.includes(",") ? dataUrl.split(",")[1] : dataUrl;
}

function statusClass(value) {
  return `pill pill-${String(value || "low").toLowerCase()}`;
}

function App() {
  const [agentResponse, setAgentResponse] = useState(null);
  const [previewImage, setPreviewImage] = useState("");
  const [imageBase64, setImageBase64] = useState("");
  const [imageName, setImageName] = useState("");
  const [scenarioNames, setScenarioNames] = useState([]);
  const [selectedScenario, setSelectedScenario] = useState(DEFAULT_SCENARIO);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [cameraOn, setCameraOn] = useState(false);
  const videoRef = useRef(null);
  const streamRef = useRef(null);

  async function loadScenario(scenarioName = selectedScenario) {
    try {
      setLoading(true);
      setError("");
      const response = await fetch(`${API_BASE}/api/demo/scenario/${scenarioName}`, { method: "POST" });
      if (!response.ok) {
        throw new Error(`Scenario request failed (${response.status})`);
      }
      setAgentResponse(await response.json());
      setSelectedScenario(scenarioName);
    } catch (currentError) {
      setError(currentError.message);
    } finally {
      setLoading(false);
    }
  }

  async function loadInitialDemo() {
    try {
      setLoading(true);
      setError("");
      const response = await fetch(`${API_BASE}/api/demo/scenarios`);
      if (!response.ok) {
        throw new Error(`Scenario list failed (${response.status})`);
      }
      const data = await response.json();
      const names = data.scenarios || [];
      setScenarioNames(names);
      const initialScenario = names.includes(DEFAULT_SCENARIO) ? DEFAULT_SCENARIO : names[0];
      if (initialScenario) {
        await loadScenario(initialScenario);
      }
    } catch (currentError) {
      setError(currentError.message);
    } finally {
      setLoading(false);
    }
  }

  async function analyzeSelectedImage() {
    if (!imageBase64) {
      setError("Upload or capture an image before analyzing.");
      return;
    }

    try {
      setLoading(true);
      setError("");
      const response = await fetch(`${API_BASE}/api/vision/analyze`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          image_base64: imageBase64,
          location_name: imageName || "Workplace tower garden",
          notes: "Frontend upload or webcam snapshot for GardenSpace AI demo.",
        }),
      });
      if (!response.ok) {
        throw new Error(`Image analysis failed (${response.status})`);
      }
      setAgentResponse(await response.json());
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
      const dataUrl = String(reader.result || "");
      setPreviewImage(dataUrl);
      setImageBase64(stripDataUrl(dataUrl));
      setImageName(file.name);
      setError("");
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
      setError(currentError.message || "Camera permission was not granted.");
    }
  }

  function stopCamera() {
    streamRef.current?.getTracks().forEach((track) => track.stop());
    streamRef.current = null;
    setCameraOn(false);
  }

  function captureSnapshot() {
    const video = videoRef.current;
    if (!video) {
      return;
    }
    const canvas = document.createElement("canvas");
    canvas.width = video.videoWidth || 960;
    canvas.height = video.videoHeight || 540;
    canvas.getContext("2d").drawImage(video, 0, 0, canvas.width, canvas.height);
    const dataUrl = canvas.toDataURL("image/jpeg", 0.86);
    setPreviewImage(dataUrl);
    setImageBase64(stripDataUrl(dataUrl));
    setImageName(`webcam-snapshot-${Date.now()}.jpg`);
    setError("");
  }

  useEffect(() => {
    loadInitialDemo();
    return () => stopCamera();
  }, []);

  const observations = agentResponse?.observations;
  const notification = agentResponse?.notification;
  const phoneResult = agentResponse?.phone_notification_result;
  const meeting = agentResponse?.meeting_suggestion;
  const sceneEvent = agentResponse?.virtual_scene_event || {
    phone_message_visible: false,
    phone_title: "",
    phone_message: "",
    animation_state: "idle",
    next_visual_action: "none",
    event_note: "Simulation waiting for analysis.",
  };

  return (
    <main className="shell">
      <Style />

      <header className="hero">
        <div>
          <p className="eyebrow">GardenSpace AI</p>
          <h1>Camera-based workplace tower-garden assistant</h1>
        </div>
        <div className="hero-status">
          <span className="sim-dot" />
          Simulation only
        </div>
      </header>

      {error && <div className="alert">{error}</div>}

      <section className="workspace">
        <section className="panel input-panel">
          <div className="section-head">
            <div>
              <p className="eyebrow">Camera / image</p>
              <h2>Garden image</h2>
            </div>
            {loading && <span className="loading">Working...</span>}
          </div>

          <div className="preview-frame">
            {previewImage ? (
              <img src={previewImage} alt="Selected tower garden preview" />
            ) : (
              <div className="preview-placeholder">
                <div className="mini-tower">
                  <span />
                  <span />
                  <span />
                </div>
                <p>Upload a garden image or capture a webcam snapshot.</p>
              </div>
            )}
            <video ref={videoRef} autoPlay playsInline muted className={cameraOn ? "video-on" : ""} />
          </div>

          <div className="tool-row">
            <label className="button-like">
              Upload image
              <input type="file" accept="image/*" onChange={handleUpload} />
            </label>
            <button onClick={cameraOn ? stopCamera : startCamera}>{cameraOn ? "Stop webcam" : "Start webcam"}</button>
            <button onClick={captureSnapshot} disabled={!cameraOn}>Snapshot</button>
            <button className="primary" onClick={analyzeSelectedImage} disabled={!imageBase64 || loading}>Analyze</button>
          </div>
          <p className="subtle">Images are sent only to the backend. No OpenAI API key is present in frontend code.</p>

          <div className="scenario-box">
            <div>
              <p className="eyebrow">Demo scenario</p>
              <h2>Run a scripted scene</h2>
            </div>
            <div className="scenario-controls">
              <select value={selectedScenario} onChange={(event) => setSelectedScenario(event.target.value)}>
                {scenarioNames.length ? (
                  scenarioNames.map((name) => (
                    <option value={name} key={name}>{formatLabel(name)}</option>
                  ))
                ) : (
                  <option value={DEFAULT_SCENARIO}>{formatLabel(DEFAULT_SCENARIO)}</option>
                )}
              </select>
              <button onClick={() => loadScenario(selectedScenario)} disabled={!selectedScenario || loading}>Load scenario</button>
            </div>
          </div>
        </section>

        <VirtualGardenScene virtualSceneEvent={sceneEvent} />
      </section>

      <section className="result-grid">
        <ResultCard title="Plant / space status">
          {observations ? (
            <div className="status-list">
              <StatusRow label="Plant health" value={formatLabel(observations.plant_health_status)} />
              <StatusRow label="Area" value={formatLabel(observations.area_status)} />
              <StatusRow label="Water check" value={observations.water_check_needed ? "May need checking" : "No check flagged"} />
              <StatusRow label="Confidence" value={`${Math.round((observations.confidence || 0) * 100)}%`} />
            </div>
          ) : <p className="subtle">No observation yet.</p>}
        </ResultCard>

        <ResultCard title="Visible issues">
          {observations?.visible_issues?.length ? (
            <ul className="issue-list">
              {observations.visible_issues.map((issue) => <li key={issue}>{issue}</li>)}
            </ul>
          ) : <p className="subtle">No visible issues flagged in this simulation.</p>}
        </ResultCard>

        <ResultCard title="Employee notification">
          {notification ? (
            <>
              <div className="card-title-row">
                <strong>{notification.notification_title}</strong>
                <span className={statusClass(notification.urgency)}>{notification.urgency}</span>
              </div>
              <p>{notification.notification_message}</p>
              <p className="subtle">
                {phoneResult?.delivered_to_mock_phone ? "Visible on the simulated phone." : "No simulated phone message shown."}
              </p>
            </>
          ) : <p className="subtle">No notification decision yet.</p>}
        </ResultCard>

        <ResultCard title="Recommended action">
          <p>{notification?.suggested_employee_action || "No action selected yet."}</p>
        </ResultCard>

        <ResultCard title="Meeting suggestion">
          {meeting ? (
            <>
              <div className="card-title-row">
                <strong>{meeting.should_suggest_meeting ? meeting.meeting_type : "No meeting suggested"}</strong>
                <span>{meeting.suggested_duration_minutes} min</span>
              </div>
              <p>{meeting.reason}</p>
            </>
          ) : <p className="subtle">No meeting suggestion yet.</p>}
        </ResultCard>

        <ResultCard title="Limitations">
          <p>{agentResponse?.limitations || "This simulation avoids identifying people and does not send real phone messages."}</p>
        </ResultCard>
      </section>

      <section className="panel explanation-panel">
        <p className="eyebrow">AI explanation</p>
        <h2>{agentResponse?.summary || "Ready for a GardenSpace AI analysis"}</h2>
        <p>{agentResponse?.employee_friendly_explanation || "Select a scenario or analyze an uploaded image to see the employee-friendly explanation."}</p>
      </section>
    </main>
  );
}

function StatusRow({ label, value }) {
  return (
    <div className="status-row">
      <span>{label}</span>
      <strong>{value}</strong>
    </div>
  );
}

function ResultCard({ title, children }) {
  return (
    <article className="panel result-card">
      <h2>{title}</h2>
      {children}
    </article>
  );
}

function Style() {
  return (
    <style>{`
      * { box-sizing: border-box; }
      body {
        margin: 0;
        font-family: Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
        background: #f4f7f1;
        color: #17221d;
      }
      .shell {
        width: min(1240px, calc(100% - 32px));
        margin: 0 auto;
        padding: 28px 0 44px;
      }
      h1, h2, p { margin-top: 0; }
      h1 {
        max-width: 820px;
        margin-bottom: 0;
        font-size: clamp(2.2rem, 6vw, 5rem);
        line-height: .95;
      }
      h2 {
        margin-bottom: 10px;
        font-size: 1.08rem;
        line-height: 1.25;
      }
      .hero {
        min-height: 190px;
        display: flex;
        align-items: center;
        justify-content: space-between;
        gap: 24px;
        padding: 22px 0;
      }
      .eyebrow {
        margin-bottom: 9px;
        color: #4f6b5a;
        font-size: .76rem;
        font-weight: 850;
        letter-spacing: .08em;
        text-transform: uppercase;
      }
      .hero-status, .scene-badge, .pill {
        display: inline-flex;
        align-items: center;
        gap: 7px;
        border-radius: 999px;
        padding: 6px 10px;
        border: 1px solid #cfdcd1;
        background: #ffffff;
        font-size: .78rem;
        font-weight: 800;
        text-transform: uppercase;
      }
      .sim-dot {
        width: 9px;
        height: 9px;
        border-radius: 999px;
        background: #45a663;
      }
      .workspace {
        display: grid;
        grid-template-columns: minmax(320px, .86fr) minmax(420px, 1.14fr);
        gap: 16px;
        align-items: stretch;
      }
      .panel {
        border: 1px solid #d7e2da;
        border-radius: 14px;
        background: rgba(255, 255, 255, .92);
        padding: 18px;
        box-shadow: 0 12px 30px rgba(32, 50, 39, .07);
      }
      .section-head, .card-title-row, .status-row {
        display: flex;
        align-items: center;
        justify-content: space-between;
        gap: 12px;
      }
      .loading, .subtle {
        color: #68766d;
        font-size: .88rem;
      }
      .preview-frame {
        position: relative;
        min-height: 280px;
        border: 1px solid #d7e2da;
        border-radius: 12px;
        overflow: hidden;
        background: #dfe9e0;
      }
      .preview-frame img, .preview-frame video {
        width: 100%;
        height: 100%;
        min-height: 280px;
        object-fit: cover;
        display: block;
      }
      .preview-frame video {
        display: none;
        position: absolute;
        inset: 0;
      }
      .preview-frame .video-on { display: block; }
      .preview-placeholder {
        min-height: 280px;
        display: grid;
        place-items: center;
        align-content: center;
        gap: 12px;
        text-align: center;
        color: #5d6e63;
      }
      .mini-tower {
        position: relative;
        width: 70px;
        height: 150px;
        border-radius: 999px;
        border: 8px solid #d5e1d8;
        background: #f8fbf7;
      }
      .mini-tower span {
        position: absolute;
        width: 34px;
        height: 20px;
        border-radius: 100% 0 100% 0;
        background: #2f8d54;
      }
      .mini-tower span:nth-child(1) { left: -10px; top: 32px; transform: rotate(-30deg); }
      .mini-tower span:nth-child(2) { right: -10px; top: 66px; transform: rotate(34deg); }
      .mini-tower span:nth-child(3) { left: -10px; top: 104px; transform: rotate(-30deg); }
      .tool-row, .scenario-controls {
        display: flex;
        flex-wrap: wrap;
        gap: 10px;
        margin-top: 12px;
      }
      button, .button-like, select {
        min-height: 42px;
        border: 1px solid #b9cabe;
        border-radius: 10px;
        background: #ffffff;
        color: #17221d;
        font: inherit;
        font-weight: 800;
        padding: 10px 13px;
      }
      button, .button-like, select { cursor: pointer; }
      button:disabled { cursor: not-allowed; opacity: .5; }
      .button-like input { display: none; }
      .primary {
        background: #226b42;
        border-color: #226b42;
        color: #ffffff;
      }
      .scenario-box {
        margin-top: 18px;
        border-top: 1px solid #e1e9e3;
        padding-top: 16px;
      }
      select { min-width: min(100%, 260px); }
      .result-grid {
        display: grid;
        grid-template-columns: repeat(3, minmax(0, 1fr));
        gap: 16px;
        margin-top: 16px;
      }
      .result-card {
        min-height: 190px;
      }
      .status-list {
        display: grid;
        gap: 10px;
      }
      .status-row {
        border-bottom: 1px solid #edf2ee;
        padding-bottom: 9px;
      }
      .status-row span {
        color: #68766d;
      }
      .issue-list {
        margin: 0;
        padding-left: 20px;
      }
      .issue-list li {
        margin-bottom: 8px;
      }
      .pill-low { background: #e3f4e7; color: #176332; border-color: #c7e4ce; }
      .pill-medium { background: #fff1cc; color: #754d00; border-color: #f2d891; }
      .pill-high { background: #ffe2d4; color: #8d3614; border-color: #efb49d; }
      .alert {
        margin-bottom: 16px;
        border-radius: 12px;
        background: #ffe1e1;
        color: #8b1f1f;
        padding: 12px 14px;
        font-weight: 750;
      }
      .explanation-panel {
        margin-top: 16px;
      }
      @media (max-width: 980px) {
        .workspace, .result-grid {
          grid-template-columns: 1fr;
        }
      }
      @media (max-width: 680px) {
        .shell { width: min(100% - 24px, 1240px); padding-top: 18px; }
        .hero, .section-head, .card-title-row {
          align-items: flex-start;
          flex-direction: column;
        }
        h1 { font-size: 2.25rem; }
      }
    `}</style>
  );
}

export default App;
