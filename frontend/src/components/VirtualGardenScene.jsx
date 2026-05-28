function formatLabel(value) {
  return String(value || "idle").replaceAll("_", " ");
}

function normalizeSceneEvent(virtualSceneEvent) {
  const event = virtualSceneEvent || {};
  const phoneMessage = event.phone_message || {};
  const visibleOnPhone = Boolean(phoneMessage.visible_on_phone ?? event.phone_message_visible);
  const title = phoneMessage.title || event.phone_title || "GardenSpace AI";
  const message = phoneMessage.message || event.phone_message || "";
  const nextAction = event.next_visual_action || "none";
  let animationState = event.animation_state || "idle";

  if (animationState === "idle" && visibleOnPhone) {
    animationState = "phone_buzz";
  }
  if (nextAction === "walk_to_garden") {
    animationState = "walking";
  }
  if (nextAction === "check_reservoir") {
    animationState = "checking_reservoir";
  }
  if (nextAction === "start_meeting") {
    animationState = "meeting";
  }
  if (nextAction === "water_plants") {
    animationState = "watering";
  }

  return {
    animationState,
    nextAction,
    title,
    message,
    visibleOnPhone,
    narration: event.event_note || "Virtual scene waiting for the next GardenSpace AI event.",
  };
}

function VirtualGardenScene({ virtualSceneEvent }) {
  const scene = normalizeSceneEvent(virtualSceneEvent);

  return (
    <section className={`vgs-card vgs-${scene.animationState}`}>
      <style>{`
        .vgs-card {
          min-height: 520px;
          overflow: hidden;
          border: 1px solid #d7e2da;
          border-radius: 14px;
          background: rgba(255, 255, 255, .94);
          padding: 18px;
          box-shadow: 0 12px 30px rgba(32, 50, 39, .07);
        }
        .vgs-head {
          display: flex;
          align-items: center;
          justify-content: space-between;
          gap: 12px;
        }
        .vgs-eyebrow {
          margin: 0 0 9px;
          color: #4f6b5a;
          font-size: .76rem;
          font-weight: 850;
          letter-spacing: .08em;
          text-transform: uppercase;
        }
        .vgs-head h2 {
          margin: 0 0 10px;
          font-size: 1.08rem;
          line-height: 1.25;
        }
        .vgs-badge {
          display: inline-flex;
          align-items: center;
          border-radius: 999px;
          padding: 6px 10px;
          border: 1px solid #cfdcd1;
          background: #ffffff;
          font-size: .78rem;
          font-weight: 800;
          text-transform: uppercase;
          white-space: nowrap;
        }
        .vgs-room {
          position: relative;
          height: 430px;
          margin-top: 12px;
          border-radius: 14px;
          overflow: hidden;
          border: 1px solid #d5e0d8;
          background:
            linear-gradient(180deg, rgba(255,255,255,.5), rgba(255,255,255,0)),
            linear-gradient(125deg, #dbe7e4 0%, #f4f0e7 54%, #dce8dc 100%);
        }
        .vgs-room::after {
          content: "";
          position: absolute;
          left: 0;
          right: 0;
          bottom: 0;
          height: 86px;
          background: rgba(202, 214, 199, .72);
        }
        .vgs-window {
          position: absolute;
          left: 28px;
          top: 28px;
          width: 36%;
          height: 42%;
          background: #a8cbd0;
          border: 10px solid rgba(255,255,255,.75);
        }
        .vgs-tower {
          position: absolute;
          z-index: 2;
          left: 16%;
          bottom: 70px;
          width: 108px;
          height: 260px;
          border: 10px solid #d8e3dc;
          border-radius: 999px;
          background: #f9fcfa;
        }
        .vgs-leaf {
          position: absolute;
          width: 56px;
          height: 30px;
          border-radius: 100% 0 100% 0;
          background: #2f8d54;
        }
        .vgs-leaf:nth-child(1) { left: -18px; top: 38px; transform: rotate(-30deg); }
        .vgs-leaf:nth-child(2) { right: -18px; top: 88px; transform: rotate(34deg); }
        .vgs-leaf:nth-child(3) { left: -18px; top: 148px; transform: rotate(-32deg); }
        .vgs-leaf:nth-child(4) { right: -18px; top: 204px; transform: rotate(30deg); }
        .vgs-reservoir {
          position: absolute;
          left: -24px;
          bottom: -46px;
          width: 142px;
          height: 44px;
          border-radius: 10px;
          border: 7px solid #edf3ef;
          background: #8abfcb;
        }
        .vgs-avatar {
          position: absolute;
          z-index: 3;
          right: 16%;
          bottom: 78px;
          width: 112px;
          height: 220px;
          transform-origin: bottom center;
          transition: right .6s ease, transform .6s ease;
        }
        .vgs-head-shape {
          width: 54px;
          height: 54px;
          margin: 0 auto;
          border-radius: 50%;
          background: #7f937f;
        }
        .vgs-body {
          width: 82px;
          height: 116px;
          margin: 8px auto 0;
          border-radius: 34px 34px 12px 12px;
          background: #446657;
        }
        .vgs-arm {
          position: absolute;
          right: 4px;
          top: 78px;
          width: 42px;
          height: 16px;
          border-radius: 999px;
          background: #7f937f;
          transform: rotate(28deg);
        }
        .vgs-phone {
          position: absolute;
          right: -4px;
          top: 88px;
          width: 28px;
          height: 44px;
          border-radius: 7px;
          border: 4px solid #21332b;
          background: #dcefe5;
          transform: rotate(-8deg);
        }
        .vgs-phone::before {
          content: "";
          display: block;
          width: 12px;
          height: 2px;
          margin: 5px auto;
          background: #21332b;
        }
        .vgs-phone-visible {
          box-shadow: 0 0 0 7px rgba(69, 166, 99, .16);
        }
        .vgs-notification {
          position: absolute;
          z-index: 4;
          right: 24px;
          top: 28px;
          width: min(300px, calc(100% - 48px));
          border-radius: 14px;
          background: rgba(255,255,255,.96);
          border: 1px solid #d7e2da;
          padding: 13px;
          box-shadow: 0 18px 40px rgba(29, 48, 38, .14);
        }
        .vgs-notification p {
          margin: 6px 0 0;
          color: #425349;
          font-size: .9rem;
        }
        .vgs-meeting-bubble {
          position: absolute;
          z-index: 4;
          left: 36%;
          top: 42px;
          border-radius: 999px;
          padding: 10px 13px;
          background: #ffffff;
          border: 1px solid #d7e2da;
          font-weight: 800;
          box-shadow: 0 10px 28px rgba(29, 48, 38, .12);
        }
        .vgs-water-drops {
          position: absolute;
          z-index: 5;
          left: calc(16% + 96px);
          bottom: 194px;
          display: flex;
          gap: 8px;
        }
        .vgs-water-drops span {
          width: 9px;
          height: 18px;
          border-radius: 999px 999px 999px 0;
          background: #5faec2;
          transform: rotate(35deg);
          animation: vgsDrop 1.2s ease-in-out infinite;
        }
        .vgs-water-drops span:nth-child(2) { animation-delay: .16s; }
        .vgs-water-drops span:nth-child(3) { animation-delay: .32s; }
        .vgs-check-label {
          position: absolute;
          z-index: 4;
          left: 24%;
          bottom: 48px;
          border-radius: 999px;
          padding: 8px 11px;
          background: #ffffff;
          border: 1px solid #d7e2da;
          font-size: .82rem;
          font-weight: 800;
        }
        .vgs-phone_buzz .vgs-phone {
          animation: vgsBuzz .35s ease-in-out infinite;
        }
        .vgs-reading_phone .vgs-avatar {
          transform: rotate(-2deg) translateY(-4px);
        }
        .vgs-reading_phone .vgs-phone {
          animation: vgsPhonePulse 1.2s ease-in-out infinite;
        }
        .vgs-walking .vgs-avatar {
          right: 42%;
          animation: vgsWalk .8s ease-in-out infinite;
        }
        .vgs-checking_reservoir .vgs-avatar {
          right: 52%;
          transform: scale(.92) translateY(16px);
        }
        .vgs-watering .vgs-avatar {
          right: 44%;
          transform: rotate(-5deg);
        }
        .vgs-meeting .vgs-avatar {
          right: 28%;
        }
        .vgs-meeting-markers {
          position: absolute;
          z-index: 3;
          right: 8%;
          bottom: 100px;
          display: flex;
          gap: 12px;
        }
        .vgs-meeting-markers span {
          width: 48px;
          height: 84px;
          border-radius: 24px 24px 10px 10px;
          background: rgba(86, 112, 98, .82);
        }
        .vgs-meeting-markers span::before {
          content: "";
          display: block;
          width: 34px;
          height: 34px;
          margin: -26px auto 8px;
          border-radius: 50%;
          background: #91a48e;
        }
        .vgs-narration {
          display: grid;
          gap: 6px;
          margin-top: 12px;
          color: #68766d;
          font-size: .88rem;
        }
        @keyframes vgsBuzz {
          0%, 100% { transform: rotate(-8deg) translateX(0); }
          25% { transform: rotate(-5deg) translateX(1px); }
          75% { transform: rotate(-11deg) translateX(-1px); }
        }
        @keyframes vgsPhonePulse {
          0%, 100% { transform: rotate(-8deg) scale(1); }
          50% { transform: rotate(-5deg) scale(1.06); }
        }
        @keyframes vgsWalk {
          0%, 100% { transform: translateY(0); }
          50% { transform: translateY(-5px); }
        }
        @keyframes vgsDrop {
          0%, 100% { transform: rotate(35deg) translateY(0); opacity: .45; }
          50% { transform: rotate(35deg) translateY(12px); opacity: 1; }
        }
        @media (max-width: 680px) {
          .vgs-head {
            align-items: flex-start;
            flex-direction: column;
          }
          .vgs-room { height: 380px; }
          .vgs-tower { left: 8%; transform: scale(.88); }
          .vgs-avatar { right: 9%; transform: scale(.88); }
          .vgs-notification { right: 12px; top: 12px; }
        }
      `}</style>

      <div className="vgs-head">
        <div>
          <p className="vgs-eyebrow">Virtual environment</p>
          <h2>Human receives the agent notification</h2>
        </div>
        <span className="vgs-badge">{formatLabel(scene.animationState)}</span>
      </div>

      <div className="vgs-room">
        <div className="vgs-window" />
        <div className="vgs-tower">
          <span className="vgs-leaf" />
          <span className="vgs-leaf" />
          <span className="vgs-leaf" />
          <span className="vgs-leaf" />
          <div className="vgs-reservoir" />
        </div>
        <div className="vgs-avatar" aria-label="Generic employee avatar">
          <div className="vgs-head-shape" />
          <div className="vgs-body" />
          <div className="vgs-arm" />
          <div className={`vgs-phone ${scene.visibleOnPhone ? "vgs-phone-visible" : ""}`} />
        </div>

        {scene.visibleOnPhone && (
          <div className="vgs-notification">
            <strong>{scene.title}</strong>
            <p>{scene.message}</p>
          </div>
        )}
        {scene.animationState === "watering" && (
          <div className="vgs-water-drops" aria-label="Water drops">
            <span />
            <span />
            <span />
          </div>
        )}
        {scene.animationState === "checking_reservoir" && (
          <div className="vgs-check-label">Checking reservoir</div>
        )}
        {scene.animationState === "meeting" && (
          <>
            <div className="vgs-meeting-bubble">Short check-in near the garden</div>
            <div className="vgs-meeting-markers" aria-label="Generic meeting markers">
              <span />
              <span />
            </div>
          </>
        )}
      </div>

      <div className="vgs-narration">
        <span>Generic avatar and simulated phone message only.</span>
        <span>Next visual action: {formatLabel(scene.nextAction)}</span>
        <span>{scene.narration}</span>
      </div>
    </section>
  );
}

export default VirtualGardenScene;
